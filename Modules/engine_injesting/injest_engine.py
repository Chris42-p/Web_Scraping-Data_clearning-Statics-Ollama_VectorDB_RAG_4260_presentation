#=== This is the injestion engine ====== 


# take the file location, get the list of documents. 

# run it via edr2pdf to make it readable 
# check the type of document it is 
# open the document 

# feed the document into LLM for meta data. 
# get the medata data tags 

#========================

#=== libraries===
import os
import base64
import mimetypes
from pathlib import Path
import subprocess
import ollama                              # pip3 install ollama --break-system-packages 
from pypdf import PdfReader                #sudo apt install python3-pypdf 
from docx import Document                  #sudo apt install python3-docx 
import spire.presentation                  #pip3 install spire.presentation --break-system-packages
import mailparser                          #pip install mail-parser --break-system-packages
import csv
import zipfile  
import hashlib
import re
import json
from datetime import datetime
import httpx
import time

#=== local imports
from .injest_interface import Interface_InjestionEngine
from .injest_interface import CONST
from .data_base.my_sql_db import SQL_DataBase

class Injest_Engine(Interface_InjestionEngine):
     #=== Meta Data ====
     err_text=CONST["ERR_TXT"]
     err_code=CONST["ERR_CODE"]
     err_model_crash=CONST["MODEL_CRASH_RETRY"]


     def __init__(
               self,
               input_files_path,
               output_files_path,
          ):
          self.input_files_path = Path(input_files_path)
          self.output_files_path = Path(output_files_path)
          self.ingest_folder = self.input_files_path
          self.files_in_dir = []
          self.dir_in_dir = []
          self.my_sql_db = SQL_DataBase()
          self.files_grouped_typ_type = {
               k: [] for k in CONST["DOCUMENT_TYPES"].keys()
     }


     #======= Process files 
     def __reset_injest_state(self):
          self.files_in_dir = [] #files in dir
          self.dir_in_dir = [] #directories in injest directory
          self.files_grouped_typ_type = {k: [] for k in 
                                       CONST["DOCUMENT_TYPES"].keys()} # .PDF, .DOCX, .CSV, .EML, .TXT, .PPTX, .ZIP  -- dict keys
     

     def process_saved_file(
          self,
          file_path: str | Path,
          source: str = "upload",
          sender: str = "",
          email_subject: str = "",
          email_date: str = "",
     ) -> dict:
          file_path = Path(file_path)
          doc_type = file_path.suffix.upper()

          if doc_type == ".PDF" and "_ocr" not in file_path.stem.lower():
               ocr_candidate = file_path.with_name(f"{file_path.stem}_ocr.pdf")
               if ocr_candidate.exists():
                    file_path = ocr_candidate

          processed_doc_obj = self.__read_a_document(doc_type, file_path)
          if processed_doc_obj is None or processed_doc_obj == CONST["ERR_CODE"]:
               raise ValueError(f"Unable to read document: {file_path}")

          raw_payload = processed_doc_obj.to_json()
          ai_processed_doc = self.__call_ollama_on_a_file(raw_payload)
          ai_doc_obj = self.__ollama_parse_response_into_object(ai_processed_doc)

          original_doc = processed_doc_obj.to_json_no_paragraphs()
          original_doc["stored_filename"] = file_path.name
          original_doc["relative_path"] = str(file_path.relative_to(self.ingest_folder)) if file_path.is_relative_to(self.ingest_folder) else file_path.name
          original_doc["original_filename"] = file_path.name
          original_doc["mime_type"] = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
          original_doc["source"] = source
          original_doc["sender"] = sender
          original_doc["email_subject"] = email_subject
          original_doc["email_date"] = email_date
          original_doc["extracted_text"] = processed_doc_obj.paragaphs

          self.my_sql_db.insert_document_with_file_metadata(
               doc_hash=original_doc["doc_hash"],
               title=original_doc["title"],
               author=original_doc["author"],
               stored_filename=original_doc["stored_filename"],
               relative_path=original_doc["relative_path"],
               original_filename=original_doc["original_filename"],
               mime_type=original_doc["mime_type"],
               source=original_doc["source"],
               sender=original_doc["sender"],
               email_subject=original_doc["email_subject"],
               email_date=original_doc["email_date"],
               extracted_text=original_doc["extracted_text"],
          )

          self.my_sql_db.update_document(
               doc_hash=original_doc["doc_hash"],
               ai_updates=ai_doc_obj,
          )

          merged_obj = {**original_doc, **ai_doc_obj}
          from ..engine_embedding.embedding import Embedding_Engine
          Embedding_Engine().embed_processed_document(merged_obj)
          self.my_sql_db.mark_processed(original_doc["doc_hash"])
          return merged_obj
     
     #get the path of the files that're in the dir. 
     def __get_files_in_injest_file(self,path= None):
          if path== None:
               path= self.input_files_path
          
          #check that these are files. 

          for item in Path(path).iterdir():
               if item.is_dir():
                    if str(item) not in self.dir_in_dir:
                         self.dir_in_dir.append(str(item))
               elif str(item) not in self.files_in_dir: #the item is a file
                    self.files_in_dir.append(str(item))

          
          #entries=Path(f"{path}").iterdir()
          #for item in entries:
          #     if item.is_dir() and (item not in self.dir_in_dir):
          #          self.dir_in_dir.append(str(item))
          #     elif (item not in self.files_in_dir): #the item is a file 
          #         self.files_in_dir.append(str(item))


          #recurrsion to get a list of all the files
          while self.dir_in_dir:
               next_dir=self.dir_in_dir.pop(0)
               self.__get_files_in_injest_file(next_dir)

          #=== keep prints for debugging. 
          # print(self.dir_in_dir)
          # print(self.files_in_dir)

     #return a object with list of 
     def __group_files_by_ext(self):
          for file in self.files_in_dir:
               suffix=Path(file).suffix.upper()
               if suffix in self.files_grouped_typ_type:
                    self.files_grouped_typ_type[suffix].append(file)
               else:
                    return f"File not processed, add extension to interface:  {file}"               

          # print(self.files_grouped_typ_type)


     # ingest a local file and save it to the database
     def injest_local_file(self, file_path: str | Path, source: str = "upload") -> dict:
               return self.process_saved_file(file_path=file_path, source=source)

     # ingest a gmail email and save it to the database
     def injest_gmail(
          self,
          processed_doc_obj,
          original_filename: str = "",
          relative_path: str = "",
          mime_type: str = "message/rfc822",
          sender: str = "",
          email_subject: str = "",
          email_date: str = "",
     ) -> dict:
          return self.ingest_processed_document(
               processed_doc_obj=processed_doc_obj,
               source="gmail",
               original_filename=original_filename,
               relative_path=relative_path,
               mime_type=mime_type,
               sender=sender,
               email_subject=email_subject,
               email_date=email_date,
          )

     #OCR my PDF -- make the text readable to machines.  
     def __ocr_my_pdf(self): #optical character recognition. #---- there is a bug  

          for file in self.files_grouped_typ_type[".PDF"]:
               if Path(file).suffix.lower() == ".pdf":
                    #has this file already been processed?  -- need to look at this one 
                    path=Path(file)
                    if ("_ocr" in path.stem.lower()): #or (f"{file_name}_ocr" in path) : ##check if the file name with _ocr excists, if it does then the file has been processed skip it. 
                         print(f"skipping processed file: {file}")
                         continue     

                    output_file_name = path.with_name(f"{path.stem}_ocr.pdf")

                    if output_file_name.exists():
                         print(f"OCR output already exists: {output_file_name}")
                         continue  

                    #temp=file.split("/")
                    #output_dir= "/".join(temp[:len(temp)-1])

                    #== File names
                    #file_name=temp[-1].split(".")[0]
                    #output_file_name="{0}/{1}_ocr.pdf".format(output_dir, file_name) 

                    cmd="ocrmypdf --optimize 1 --skip-text {0} {1}".format(str(file), str(output_file_name)) 
                    
                    #OCR the doc 
                    try:
                         print(f"currently processing: {cmd}")
                         subprocess.run(cmd.split(" "),check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                         print(f"Processed {file}")
                    except subprocess.CalledProcessError as e:
                         print(f"{self.err_text}:injestion engine OCR failed: {e.stderr} ")
                    except FileNotFoundError:
                         print(f"{self.err_text}: ocrmypdf not found — is it installed and on PATH?")

     def  __read_document_bytes(self, document):
          with open(document, "rb") as f:
               _bytes=f.read()
          return _bytes

     # Ingest a processed document and save it to the database
     def ingest_processed_document(
          self,
          processed_doc_obj,
          source="upload",
          original_filename=None,
          relative_path=None,
          mime_type=None,
          sender=None,
          email_subject=None,
          email_date=None,
     ):
          ai_processed_doc = self.__call_ollama_on_a_file(processed_doc_obj.to_json())
          ai_doc_obj = self.__ollama_parse_response_into_object(ai_processed_doc)

          original_doc = processed_doc_obj.to_json_no_paragraphs()
          original_doc["source"] = source
          original_doc["original_filename"] = original_filename
          original_doc["relative_path"] = relative_path
          original_doc["mime_type"] = mime_type
          original_doc["sender"] = sender or ""
          original_doc["email_subject"] = email_subject or ""
          original_doc["email_date"] = email_date or ""
          original_doc["stored_filename"] = Path(original_filename).name if original_filename else ""
          original_doc["extracted_text"] = processed_doc_obj.paragaphs or ""

          self.my_sql_db.insert_document_with_file_metadata(
               doc_hash=original_doc["doc_hash"],
               title=original_doc["title"],
               author=original_doc["author"],
               stored_filename=original_doc["stored_filename"],
               relative_path=original_doc["relative_path"],
               original_filename=original_doc["original_filename"],
               mime_type=original_doc["mime_type"],
               source=original_doc["source"],
               sender=original_doc["sender"],
               email_subject=original_doc["email_subject"],
               email_date=original_doc["email_date"],
               extracted_text=original_doc["extracted_text"],
          )

          self.my_sql_db.update_document(
               doc_hash=original_doc["doc_hash"],
               ai_updates=ai_doc_obj,
          )

          merged_obj = {**original_doc, **ai_doc_obj}
          from ..engine_embedding.embedding import Embedding_Engine
          Embedding_Engine().embed_processed_document(merged_obj)
          self.my_sql_db.mark_processed(original_doc["doc_hash"])
          return {
               "doc_hash": original_doc["doc_hash"],
               "title": original_doc["title"],
               "source": source,
          }
     
     #open the file and read their content. 
     def __read_a_document(self,doc_type, docuemnt): #recurrsion on .zip & .eml
          read_doc_obj=None  
          docuemnt = str(docuemnt) 

          if doc_type ==".PDF":
               #ref: https://www.geeksforgeeks.org/python/working-with-pdf-files-in-python/
               reader= PdfReader(docuemnt) 

               #read text/OCR
               doc_content = []
               for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""   # returns OCR text layer if present
                    doc_content.append({"page": i, "text": text})
               
               joined_text = "\n".join([page["text"] for page in doc_content])
               #Tables being absorbed?

               #== Meta==
               #Who made it, at what time?
               #does it have creaters computer ID?

               # === Metadata ===
               meta = reader.metadata
               title = meta.title if meta.title else None
               author = meta.author if meta.author else None
               time_creation = str(meta.creation_date) if meta.creation_date else None
               modified_date = str(meta.modification_date) if meta.modification_date else None
               file_computer_id = meta.creator if meta.creator else None

               # combine all pages into one string
               all_text = " ".join([page["text"] for page in doc_content])

               read_doc_obj = self.Processed_Document_Obj(
               title=title,

               paragaphs=all_text,
               author=author,
               time_creation=time_creation,
               modified_date=modified_date,
               file_computer_id=file_computer_id
               )

          elif doc_type == ".DOCX": 
               #ref: https://pytutorial.com/python-docx-tutorial-read-parse-docx-content/

               #read the document. 
               doc=Document(docuemnt)

               #read headers and footer. 
               header_text=""
               for section in doc.sections:
                    header_obj= section.header
                    for paragraph in header_obj.paragraphs:
                         header_text += paragraph.text + "\n"

               #read tables. 
               all_row_data=""
               for i, table in enumerate(doc.tables):
                    print(f"Table {i+1}")
                    for row in table.rows:
                         row_data = [cell.text for cell in row.cells]
                         all_row_data += " ".join(row_data) + "\n"
                         # print(row_data)

               #read paragraphs
               doc_content=""
               for paragraph in doc.paragraphs: #can index into paragraphs also 
                    doc_content+=paragraph.text 
               
               #extracting 

               # Access document properties
               # props = doc.core_properties
               # print(f"Title: {props.title}")
               # print(f"Author: {props.author}")
               # print(f"Created: {props.created}")
               # print(f"Modified: {props.modified}")

               # print("1111"+doc_content)

               # === Metadata ===
               props = doc.core_properties
               read_doc_obj = self.Processed_Document_Obj(
               title=props.title if props.title else None,
               paragaphs=doc_content,
               header_footer=header_text,
               table_content=all_row_data,
               author=props.author if props.author else None,
               time_creation=str(props.created.isoformat()) if props.created else None,
               modified_date=str(props.modified.isoformat()) if props.modified else None,
               file_computer_id=props.last_modified_by if props.last_modified_by else None
               )

          elif doc_type ==".CSV": #output is cast to string
               doc_content=""

               #open csv with content
               with open(docuemnt, mode ='r') as file:    
                    csvFile = csv.DictReader(file)
                    for lines in csvFile:
                         doc_content += str(lines)


               #TEAM: find meta data on the file and the other properties of the object 
               #who made, it at what time, computer ID, title of document... ctrl+hover over obj to see fileds
               # === Metadata ===
               import os
               file_stat = os.stat(docuemnt)
               read_doc_obj = self.Processed_Document_Obj(
               title=os.path.basename(docuemnt),
               paragaphs=doc_content,
               time_creation=str(file_stat.st_ctime),
               modified_date=str(file_stat.st_mtime),
               )
               
          elif doc_type ==".TXT":
               doc_content=""
               #TEAM: metadata please

               with open(docuemnt,"r", encoding="utf-8") as file:
                    doc_content=file.read() #reutrns string 
                    #file.close() 

               # === Metadata ===
               import os
               file_stat = os.stat(docuemnt)
               read_doc_obj = self.Processed_Document_Obj(
               title=os.path.basename(docuemnt),
               paragaphs=doc_content,
               time_creation=str(file_stat.st_ctime),
               modified_date=str(file_stat.st_mtime),
               )
               
          elif doc_type ==".PPTX":
               # ref: https://medium.com/@alice.yang_10652/extract-text-from-powerpoint-ppt-or-pptx-with-python-shapes-tables-notes-smartart-and-more-18e1381018e0
               from pptx import Presentation

               prs = Presentation(docuemnt)

               # === Read content ===
               doc_content = ""
               for slide in prs.slides:
                    for shape in slide.shapes:
                         if hasattr(shape, "text"):
                              doc_content += shape.text + " "

               # === Metadata ===
               props = prs.core_properties
               read_doc_obj = self.Processed_Document_Obj(
                    title=props.title if props.title else None,
                    paragaphs=doc_content,
                    author=props.author if props.author else None,
                    time_creation=str(props.created) if props.created else None,
                    modified_date=str(props.modified) if props.modified else None,
                    file_computer_id=props.last_modified_by if props.last_modified_by else None
               )

          #==== Recurrsion for document files. 
          elif doc_type ==".ZIP":
               print("TODO: File Reader: Zip")
               #ref: https://www.geeksforgeeks.org/python/working-zip-files-python/

               doc_content=""
               #TEAM: metadata please

               #read zip files. 

               with zipfile.ZipFile(docuemnt, "r") as zip_ref:
                    files_in_zip = zip_ref.namelist()
                    for file in files_in_zip:
                    # read documents in a zip file.
                    #with zipfile.ZipFile(docuemnt, "r") as zipf:
                         try:
                              content = zip_ref.read(file)
                              doc_content += content.decode('utf-8') + " "
                         except UnicodeDecodeError:
                              print(f"Skipping binary file in zip: {file}")
                              continue


               read_doc_obj=self.Processed_Document_Obj(title=Path(docuemnt).stem,paragaphs=doc_content)
               pass
          elif doc_type == ".EML":
               mail = mailparser.parse_from_file(docuemnt)

               subject = mail.subject or Path(docuemnt).stem

               sender = ""
               if getattr(mail, "from_", None):
                    try:
                         if isinstance(mail.from_, list) and len(mail.from_) > 0:
                              first_sender = mail.from_[0]
                              if isinstance(first_sender, tuple) and len(first_sender) > 1:
                                   sender = first_sender[1] or first_sender[0] or ""
                              else:
                                   sender = str(first_sender)
                         else:
                              sender = str(mail.from_)
                    except Exception:
                         sender = str(mail.from_)

               plain_parts = []
               if getattr(mail, "text_plain", None):
                    if isinstance(mail.text_plain, list):
                         plain_parts.extend([str(part) for part in mail.text_plain if part])
                    else:
                         plain_parts.append(str(mail.text_plain))

               if getattr(mail, "text_plain_list", None):
                    plain_parts.extend([str(part) for part in mail.text_plain_list if part])

               body_text = "\n".join(part.strip() for part in plain_parts if part and str(part).strip())

               if not body_text:
                    body_text = str(getattr(mail, "body", "") or "")

               attachment_names = []
               attachments = getattr(mail, "attachments", None) or getattr(mail, "attachments_list", None) or []
               for attachment in attachments:
                    if isinstance(attachment, dict):
                         name = attachment.get("filename") or attachment.get("mail_content_type") or ""
                         if name:
                              attachment_names.append(str(name))

               attachment_text = ", ".join(attachment_names)

               combined_text_parts = [
                    f"Email subject: {subject}",
                    f"Email sender: {sender}",
                    f"Email date: {str(getattr(mail, 'date', '') or getattr(mail, 'date_mail', '') or '')}",
                    f"Attachments: {attachment_text}",
                    body_text,
               ]
               doc_content = "\n".join(part for part in combined_text_parts if part and str(part).strip())

               read_doc_obj = self.Processed_Document_Obj(
                    title=subject,
                    paragaphs=doc_content,
                    header_footer="",
                    table_content=attachment_text,
                    author=sender,
                    time_creation=str(getattr(mail, "date", "") or getattr(mail, "date_mail", "") or ""),
                    modified_date=str(getattr(mail, "date", "") or getattr(mail, "date_mail", "") or ""),
                    file_computer_id="",
               )
          else:
               print( CONST["ERR_TXT"])
               return CONST["ERR_CODE"]

          #want to retrive whole document if needed. 
          _bytes=self.__read_document_bytes(docuemnt)
          read_doc_obj.set_docuemnt_bytes(_bytes)

          return read_doc_obj

     def __unzip_zip_files(self):
          entries = Path(str(self.input_files_path)).iterdir()
          
          for item in entries:
               if item.suffix.lower() == ".zip":
                    print(f"Unzipping: {item}")
                    try:
                         with zipfile.ZipFile(item, "r") as zip_ref:
                              zip_ref.extractall(self.input_files_path)
                         print(f"Extracted: {item}")
                    except Exception as e:
                         print(f"{self.err_text}: Failed to unzip {item}: {e}")


     #====== AI section
     #-- Call out to model to get metadata tags. 
     def __call_ollama_on_a_file(self, document):       #private method
          #ref: https://github.com/ollama/ollama-python
          crashes=0
          response=""
          while crashes<self.err_model_crash:
               try:
                    print("sending request to model ")
                    
                    content=f"{CONST['PROMPT']} \n {document}"
                    response=ollama.chat(
                         model=CONST["MODEL_NAME"],               
                         messages=[{
                              "role":"user",
                              "content": content,
                              # "content": f"how are you doing today?"
                              }],
                              stream= True
                         )

                    full_response = ""
                    for chunk in response:
                         token = chunk['message']['content']
                         # print(token, end='', flush=True)
                         full_response += token

                    return full_response

               except Exception as e:
                    crashes += 1
                    print(f"{CONST['ERR_TXT']}: Ollama call: {e}")
                    print("Model Crashed")

          return json.dumps({
               "summary": "AI summary unavailable.",
               "description": "Ollama model call failed.",
               "send_reason": "",
               "keywords": [],
               "topics": [],
               "entities": [],
               "document_type": "unknown",
               "sentiment": "unknown",
               "language": "unknown",
               "date_references": [],
          })

     # parse the response from the model into a structured object
     def __ollama_parse_response_into_object(self, ollama_response ):
          fallback = self.AI_Processed_Document_Obj(
               ai_summary="AI summary unavailable.",
               ai_description="Ollama response could not be parsed.",
               ai_send_reason="",
               ai_keywords=[],
               ai_topics=[],
               ai_entities=[],
               ai_document_type="unknown",
               ai_sentiment="unknown",
               ai_language="unknown",
               ai_date_references=[],
          ).to_json()

          if not ollama_response or not str(ollama_response).strip():
               return fallback

          try:
               parsed = json.loads(ollama_response)
          except (json.JSONDecodeError, TypeError):
               print(f"{CONST['ERR_TXT']}: Ollama returned non-JSON output.")
               return fallback
          return self.AI_Processed_Document_Obj(
               ai_summary=parsed.get("summary", "AI summary unavailable."),
               ai_description=parsed.get("description", ""),
               ai_send_reason=parsed.get("send_reason", ""),
               ai_keywords=parsed.get("keywords", []),
               ai_topics=parsed.get("topics", []),
               ai_entities=parsed.get("entities", []),
               ai_document_type=parsed.get("document_type", "unknown"),
               ai_sentiment=parsed.get("sentiment", "unknown"),
               ai_language=parsed.get("language", "unknown"),
               ai_date_references=parsed.get("date_references", []),
          ).to_json()


     # ===== Start the ollama model =====
     def __start_ollama(self, wait_to_boot=20):
          
          if wait_to_boot <= 0:
               print("Please bring up Ollama LLM manually")
               return False
          try:
               #check model is awake 
               r = httpx.get("http://ollama:11434")
               return r.status_code == 200
          except httpx.ConnectError:
               #bring up model 
               ollama.pull(CONST["MODEL_NAME"]) #download the model 
               ollama.chat(
                    model=CONST["MODEL_NAME"],               
                    messages=[{
                         "role":"user",
                         "content": "Say 'hello' back",
                         }],
                    )
               print(f"Starting AI, please wait: {wait_to_boot} seconds ")
               time.sleep(wait_to_boot)

               self.__start_ollama(wait_to_boot-10)
          

     #====== Save processed data
     def __save_processed_doc_to_sql(self, og_doc, ai_doc, og_doc_hash): #send one doc at a time 
          db=SQL_DataBase()
          db.insert_document(og_doc, ai_doc)
          # print(f"successfuly wrote obj: {db.get_document_by_hash(og_doc_hash)}")          
          # db.DEV_drop_db_table()

         # === Interface compliance: match abstract method names ===
     


     #=== Meta ===
     def controller(self, use_local=True, use_gmail=False, max_emails=10):  #TEAM: can we please order the methods in the same sequence as we see here?
          #== Ai 
          self.__start_ollama()
          
          #== Pre Processing
          #change document names to have _ for processing sake. 
          self.__unzip_zip_files() #find zip files and open unzip them. 

          #=== Process the files
          processed_files=self.__get_files_in_injest_file()
          self.__group_files_by_ext()
          self.__ocr_my_pdf() 

          #== Pre Processing / Ingestion
          # processed_doc_objs=[]
          # for key, value in self.files_grouped_typ_type.items():
          #      for file in value:
          #           doc_obj = self.__read_a_document(key, file)
          #           if doc_obj is not None:
          #                processed_doc_objs.append(doc_obj.to_json())
          #return processed_doc_objs

          #=== Read all documents
          print(f"Files to process: {self.files_grouped_typ_type}") 
          processed_doc_objs = []
          for key, value in self.files_grouped_typ_type.items():
               for file in value:
                    doc_obj = self.__read_a_document(key, file)
                    if doc_obj is not None and doc_obj != CONST["ERR_CODE"]:
                         processed_doc_objs.append(doc_obj)

          #=== Send each document to ollama and save to SQL
          for processed_doc_obj in processed_doc_objs:
               try:
                    ai_processed_doc = self.__call_ollama_on_a_file(processed_doc_obj.to_json())
                    ai_doc_obj = self.__ollama_parse_response_into_object(ai_processed_doc)

                    original_doc = processed_doc_obj.to_json_no_paragraphs()
                    original_doc["stored_filename"] = ""
                    original_doc["relative_path"] = ""
                    original_doc["original_filename"] = ""
                    original_doc["mime_type"] = ""
                    original_doc["source"] = "local"
                    original_doc["sender"] = ""
                    original_doc["email_subject"] = ""
                    original_doc["email_date"] = ""
                    original_doc["extracted_text"] = processed_doc_obj.paragaphs or ""

                    self.my_sql_db.insert_document_with_file_metadata(
                    doc_hash=original_doc["doc_hash"],
                    title=original_doc["title"],
                    author=original_doc["author"],
                    stored_filename=original_doc["stored_filename"],
                    relative_path=original_doc["relative_path"],
                    original_filename=original_doc["original_filename"],
                    mime_type=original_doc["mime_type"],
                    source=original_doc["source"],
                    sender=original_doc["sender"],
                    email_subject=original_doc["email_subject"],
                    email_date=original_doc["email_date"],
                    extracted_text=original_doc["extracted_text"],
                    )

                    self.my_sql_db.update_document(
                    doc_hash=original_doc["doc_hash"],
                    ai_updates=ai_doc_obj,
                    )

                    merged_obj = {**original_doc, **ai_doc_obj}
                    from ..engine_embedding.embedding import Embedding_Engine
                    Embedding_Engine().embed_processed_document(merged_obj)
                    self.my_sql_db.mark_processed(original_doc["doc_hash"])

                    print(f"Saved: {original_doc.get('title', 'unknown')}")
               except Exception as e:
                    print(f"Error processing document: {e}")
          # #=== Send the object to ollama to read over.
          # for processed_document in processed_doc_objs:
          #      response=self.__call_ollama_on_a_file(processed_document)
          #      self.__ollama_parse_response_into_object(response,processed_document)

          # #== save the documents 

          # #=== Send documents to Ollama
          # ai_processed_doc_objs = []
          # for processed_document in processed_doc_objs:
          #      response = self.__call_ollama_on_a_file(processed_document)
          #      ai_doc = self.__ollama_parse_response_into_object(response)
          #      ai_processed_doc_objs.append({
          #           "document": processed_document,
          #           "ai_metadata": ai_doc
          #      })

          #=== Dev/Debug area.  #-- the following files were tested and work
          # root=str(self.input_files_path) + "/"
          # processed_doc_obj= self.__read_a_document(".PDF",root+"temp_ocr.pdf")
          # ai_processed_doc=self.__call_ollama_on_a_file(processed_doc_obj.to_json() )
          # ai_doc_obj=self.__ollama_parse_response_into_object(ai_processed_doc)
          
          # print(processed_doc_obj.to_json_no_paragraphs())
          # print(ai_doc_obj)
          # self.__save_processed_doc_to_sql(processed_doc_obj.to_json_no_paragraphs(),ai_doc_obj, processed_doc_obj.get_hash() )

          #return the documents that're processed to be moved to another folder
          
          return processed_files
     
          # -- Favour please make a seperate object for downloading emails,
               # this object should be handling the processing of the email and feeding it into the AI
          #   if use_local:
          #      processed_doc_objs.extend(self.ingest_local_files())
          
          # if use_gmail:
          #      gmail_docs = self.ingest_gmail(max_emails=max_emails)
          #      for item in gmail_docs:
          #           if "parsed_email" in item:
          #                processed_doc_objs.append(item["parsed_email"])
     


          # self.__save_processed_doc_to_sql(processed_doc_obj.to_json_no_paragraphs(), ai_processed_doc, processed_doc_obj.get_hash())
          

          #== dev util 
          # doc_metadata= self.__read_a_document(".DOCX",root+"temp.docx")
          # doc_metadata= self.__read_a_document(".CSV",root+"temp.csv")
          # doc_metadata= self.__read_a_document(".TXT",root+"ppt_x.txt")
     
     
     
     

     #===== Utility
     class Processed_Document_Obj: # might need to set content size limits so model dosent crash
          #document itself #default "" since we're working with strings. 
          title =""
          docuemnt_bytes=""
          paragaphs =""
          header_footer =""
          table_content =""
          #== meta data
          author =""
          time_creation =""
          modified_date=""
          file_computer_id=""
          
          #== hahses 
          doc_hash=""

          def __init__(self, title="",paragaphs="", header_footer="", 
                              table_content="", author="", time_creation="", 
                              modified_date="", file_computer_id=""):
               self.title=title
               self.paragaphs=paragaphs 
               self.header_footer=header_footer 
               self.table_content=table_content 

               #== meta data
               self.author=author
               self.time_creation=time_creation
               self.modified_date=modified_date
               self.file_computer_id=file_computer_id

          def standardize_text(self, value):
               #make it lower case.#take out punctuation.#remove \t \n #remove special characters

               #set the attribute
               s=getattr(self, value)

               #clean the attribute
               if s is None:
                    return ""
               s = str(s)
               s = s.lower()
               s = re.sub(r'[\t\n]+', ' ', s)                      # replace tabs/newlines with space
               s = re.sub(r'[!@#$%^&*()_}{:\'".,?\-+]+', ' ', s)   # remove listed punctuation
               s = re.sub(r'\s+', ' ', s).strip()                  # collapse spaces and trim
          
               #reassign .
               setattr(self, value, s)
               return s

          def to_json(self):
               # ensure hash is up to date
               #if self.__hash_document == "":
               if self.doc_hash == "":
                    self.__hash_document()

               tmp={
                    "title": self.standardize_text( "title"),
                    "paragraphs":self.standardize_text ("paragaphs"),   #using AI to summarize this
                    "header_footer":self.standardize_text ("header_footer"),
                    "table_content":self.standardize_text ("table_content"),
                    "author":self.standardize_text ("author"),
                    "time_creation":self.standardize_text ("time_creation"),
                    "modified_date":self.standardize_text ("modified_date"),
                    "file_computer_id":self.standardize_text ("file_computer_id"),
                    "doc_hash":self.standardize_text ("doc_hash"),
               }

               self.__hash_document()

               return tmp

          def get_hash(self):
               return self.doc_hash

          def to_json_no_paragraphs(self):
               # ensure hash is up to date
               if self.doc_hash == "":
                    self.__hash_document()

               return {
                    "title": self.standardize_text( "title"),
                    # "paragraphs":self.standardize_text ("paragaphs"),   #using AI to summarize this
                    "document_bytes":self.docuemnt_bytes,
                    "header_footer":self.standardize_text ("header_footer"),
                    "table_content":self.standardize_text ("table_content"),
                    "author":self.standardize_text ("author"),
                    "time_creation":self.standardize_text ("time_creation"),
                    "modified_date":self.standardize_text ("modified_date"),
                    "file_computer_id":self.standardize_text ("file_computer_id"),
                    "doc_hash":self.standardize_text ("doc_hash"),
                    
                    # "free_field_1":"",
                    # "free_field_2":"",
                    # "free_field_3":"",
                         
               }

          def set_docuemnt_bytes(self, docuemnt_bytes):
               self.docuemnt_bytes= docuemnt_bytes


          def __hash_document(self):
               #hash the title, and author? -- quick look up?
               content = str(self.author) + str(self.title)
               self.doc_hash = hashlib.md5(content.encode()).hexdigest()


     class AI_Processed_Document_Obj:
          #== Inheretence

          #AI processed objects. 
          ai_summary=""
          ai_description=""
          ai_send_reason=""
          ai_keywords=""
          ai_topics=""
          ai_entities=""
          ai_document_type=""
          ai_sentiment=""
          ai_language=""
          ai_date_references=""

          def __init__(self,ai_summary, ai_description, ai_send_reason, ai_keywords, ai_topics, ai_entities, ai_document_type, ai_sentiment, ai_language, ai_date_references):
               self.ai_summary=ai_summary
               self.ai_description=ai_description
               self.ai_send_reason=ai_send_reason
               self.ai_keywords=ai_keywords
               self.ai_topics=ai_topics
               self.ai_entities=ai_entities
               self.ai_document_type=ai_document_type
               self.ai_sentiment=ai_sentiment
               self.ai_language=ai_language
               self.ai_date_references=ai_date_references

     
          def to_json(self):
               return {
                    "summary":          self.ai_summary,
                    "description":      self.ai_description,
                    "send_reason":      self.ai_send_reason,
                    "keywords":         self.ai_keywords,
                    "topics":           self.ai_topics,
                    "entities":         self.ai_entities,
                    "document_type":    self.ai_document_type,
                    "sentiment":        self.ai_sentiment,
                    "language":         self.ai_language,
                    "date_references":  self.ai_date_references,
               }
          