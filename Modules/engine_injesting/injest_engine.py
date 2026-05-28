#=== This is the injestion engine ====== 


# take the file location, get the list of documents. 

# run it via edr2pdf to make it readable 
# check the type of doucment it is 
# open the document 

# feed the document into LLM for meta data. 
# get the medata data tags 

#========================

#=== libraries===
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

#=== local imports
from .injest_interface import Interface_InjestionEngine
from .injest_interface import CONST
from .data_base.my_sql_db import SQL_DataBase






class Injest_Engine(Interface_InjestionEngine):
     #=== Meta Data ====
     err_text=CONST["ERR_TXT"]
     err_code=CONST["ERR_CODE"]
     err_model_crash=CONST["MODEL_CRASH_RETRY"]

     #=== File locations ====
     input_files_path=None
     output_files_path=None
     
     #=== Items in the injest files ====
     files_in_dir=[] #files in dir
     dir_in_dir=[]   #directories in injest directory
     files_grouped_typ_type=CONST["DOCUMENT_TYPES"] # .PDF, .DOCX, .CSV, .EML, .TXT, .PPTX, .ZIP  -- dict keys



     def __init__(self, input_files_path,output_files_path):
          self.input_files_path=input_files_path
          self.output_files_path=output_files_path
          
          #activate the class
          self.controller()

     #======= Process files 
     #get the path of the files that're in the dir. 
     def __get_files_in_injest_file(self,path= None):
          if path== None:
               path= self.input_files_path
          
          #check that these are files. 
          entries=Path(f"{path}").iterdir()
          for item in entries:
               if item.is_dir() and (item not in self.dir_in_dir):
                    self.dir_in_dir.append(str(item))
               elif (item not in self.files_in_dir): #the item is a file 
                    self.files_in_dir.append(str(item))

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

     #OCR my PDF -- make the text readable to machines.  
     def __ocr_my_pdf(self): #optical character recognition. #---- there is a bug  

          for file in self.files_grouped_typ_type[".PDF"]:
               if file.split(".")[1]=="pdf": 
                    #has this file already been processed?  -- need to look at this one 
                    path=Path(file).stem.lower()
                    if ("_ocr" in path): #or (f"{file_name}_ocr" in path) : ##check if the file name with _ocr excists, if it does then the file has been processed skip it. 
                         print(f"skipping processed file: {file}")
                         continue       

                    temp=file.split("/")
                    output_dir= "/".join(temp[:len(temp)-1])

                    #== File names
                    file_name=temp[-1].split(".")[0]
                    output_file_name="{0}/{1}_ocr.pdf".format(output_dir, file_name) 

                    cmd="ocrmypdf --optimize 1 --force-ocr {0} {1}".format(str(file), str(output_file_name)) 
                    
                    #OCR the doc 
                    try:
                         subprocess.run(cmd.split(" "),check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                         print(f"Processed {file}")
                    except subprocess.CalledProcessError as e:
                         print(f"{self.err_text}:injestion engine: {e.stdout} ")

     #open the file and read their content. 
     def __read_a_document(self,doc_type, docuemnt): #recurrsion on .zip & .eml
          read_doc_obj=None   

          if doc_type ==".PDF":
               #ref: https://www.geeksforgeeks.org/python/working-with-pdf-files-in-python/
               reader= PdfReader(str(docuemnt)) 

               #read text/OCR
               doc_content = []
               for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""   # returns OCR text layer if present
                    doc_content.append({"page": i, "text": text})
               
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
               header=""
               for section in doc.sections:
                    header= section.header
                    for paragraph in header.paragraphs:
                         header=paragraph.text

               #read tables. 
               all_row_data=""
               for i, table in enumerate(doc.tables):
                    print(f"Table {i+1}")
                    for row in table.rows:
                         all_row_data+=[cell.text for cell in row.cells]
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
               author=props.author if props.author else None,
               time_creation=str(props.created) if props.created else None,
               modified_date=str(props.modified) if props.modified else None,
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

               with open(docuemnt,"r") as file:
                    doc_content=file.read() #reutrns string 
                    file.close() 

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
                    with zipfile.ZipFile(docuemnt, "r") as zipf:
                         content = zipf.read(file)
                         try:
                              doc_content += content.decode('utf-8')
                         except UnicodeDecodeError:
                              print(f"Skipping binary file in zip: {file}")
                              continue


               read_doc_obj=self.Processed_Document_Obj(paragaphs=doc_content)
               pass
          elif doc_type ==".EML":
               print("TODO: File Reader: .EML")
               
               # ref: claude

               import mailparser

               mail = mailparser.parse_from_file(docuemnt)

               print(mail.subject)
               print(mail.from_)
               print(mail.body)          # full body
               print(mail.attachments)   # all attachments


               doc_content=""
               #TEAM: metadata please

               read_doc_obj=self.Processed_Document_Obj(paragaphs=doc_content)
               pass
          else:
               print( CONST["ERR_TXT"])
               return CONST["ERR_CODE"]

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
                    crashes+=1
                    print(f"{CONST['ERR_TXT']}: Ollama call:  {e}"  )
                    print("Model Crashed")               

          return "" #return empty string if the model keeps crashing.

     def __ollama_parse_response_into_object(self, ollama_response ):
          ollama_response= json.loads(ollama_response)
          return self.AI_Processed_Document_Obj(
               ai_summary =ollama_response["summary"] ,
               ai_description =ollama_response["description"] ,
               ai_send_reason =ollama_response["send_reason"] ,
               ai_keywords =ollama_response["keywords"] ,
               ai_topics =ollama_response["topics"] ,
               ai_entities =ollama_response["entities"] ,
               ai_document_type =ollama_response["document_type"] ,
               ai_sentiment =ollama_response["sentiment"] ,
               ai_language =ollama_response["language"] ,
               ai_date_references =ollama_response["date_references"] ,
          ).to_json()

     def __start_ollama(self):
          pass

     #====== Save processed data
     def __save_processed_doc_to_sql(self, og_doc, ai_doc, og_doc_hash): #send one doc at a time 
          db=SQL_DataBase()
          db.insert_document(og_doc, ai_doc)
          print(f"successfuly wrote obj: {db.get_document(og_doc_hash)}")          

          # db.DEV_drop_db_table()

     #=== Meta ===
     def controller(self):  #TEAM: can we please order the methods in the same sequence as we see here?
          #== Ai 
          self.__start_ollama()
          
          #== Pre Processing
          #change document names to have _ for processing sake. 
          self.__unzip_zip_files() #find zip files and open unzip them. 

          #=== Process the files
          self.__get_files_in_injest_file()
          self.__group_files_by_ext()
          self.__ocr_my_pdf() 

          # #=== Read the documents
          # processed_doc_objs=[]
          # for key, value in self.files_grouped_typ_type.items():
          #      for file in value:
          #           processed_doc_objs+= self.__read_a_document(key, file)

          # #=== Send the object to ollama to read over.
          # for processed_document in processed_doc_objs:
          #      response=self.__call_ollama_on_a_file(processed_document)
          #      self.__ollama_parse_response_into_object(response,processed_document)

          #== save the documents 


          #=== Dev/Debug area.  #-- the following files were tested and work
          root=str(self.input_files_path) + "/"
          processed_doc_obj= self.__read_a_document(".PDF",root+"temp_ocr.pdf")
          ai_processed_doc=self.__call_ollama_on_a_file(processed_doc_obj.to_json() )
          self.__save_processed_doc_to_sql(processed_doc_obj.to_json_no_paragraphs(), ai_processed_doc, processed_doc_obj.get_hash())
          

          #== dev util 
          # doc_metadata= self.__read_a_document(".DOCX",root+"temp.docx")
          # doc_metadata= self.__read_a_document(".CSV",root+"temp.csv")
          # doc_metadata= self.__read_a_document(".TXT",root+"ppt_x.txt")
          
          # print(f"\n\n{processed_doc_obj.to_json_no_paragraphs()} \n\n")
          # print(f"{ai_processed_doc}") 


     #===== Utility

     class Processed_Document_Obj: # might need to set content size limits so model dosent crash
          #document itself #default "" since we're working with strings. 
          title =""
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

          def __init__(self, title="", paragaphs="", header_footer="", 
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
               if self.__hash_document == "":
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
               if self.__hash_document == "":
                    self.__hash_document()

               return {
                    "title": self.standardize_text( "title"),
                    # "paragraphs":self.standardize_text ("paragaphs"),   #using AI to summarize this
                    "header_footer":self.standardize_text ("header_footer"),
                    "table_content":self.standardize_text ("table_content"),
                    "author":self.standardize_text ("author"),
                    "time_creation":self.standardize_text ("time_creation"),
                    "modified_date":self.standardize_text ("modified_date"),
                    "file_computer_id":self.standardize_text ("file_computer_id"),
                    "doc_hash":self.standardize_text ("doc_hash"),
               }


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
                    "ai_metadata": {
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
               }

          




