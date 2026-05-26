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
import ollama                              #https://github.com/ollama/ollama-python
from pypdf import PdfReader                #sudo apt install python3-pypdf 
from docx import Document               #sudo apt install python3-docx 
import spire.presentation                  #pip3 install spire.presentation --break-system-packages
import mailparser                          #pip install mail-parser --break-system-packages
import csv
import zipfile  
import hashlib
import re

#=== local imports
from .injest_interface import Interface_InjestionEngine
from .injest_interface import CONST



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

               read_doc_obj= self.Processed_Document_Obj(paragaphs=doc_content[0]["text"]) #TEAM: please fill it in. 
          elif doc_type == ".DOCX": 
               #ref: https://pytutorial.com/python-docx-tutorial-read-parse-docx-content/

               #read the document. 
               doc=Document(docuemnt)

               #read headers and footer. 
               header=""
               for section in doc.sections:
                    header= section.header
                    for paragraph in header.paragraphs:
                         header+=paragraph.text


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

               print("1111"+doc_content)

               read_doc_obj=self.Processed_Document_Obj(paragaphs=doc_content)

               pass
          elif doc_type ==".CSV": #output is cast to string
               doc_content=""

               #open csv with content
               with open(docuemnt, mode ='r') as file:    
                    csvFile = csv.DictReader(file)
                    for lines in csvFile:
                         doc_content += str(lines)


               #TEAM: find meta data on the file and the other properties of the object 
               #who made, it at what time, computer ID, title of document... ctrl+hover over obj to see fileds
               read_doc_obj=self.Processed_Document_Obj(paragaphs=doc_content)
               pass
          elif doc_type ==".TXT":
               doc_content=""
               #TEAM: metadata please

               with open(docuemnt,"r") as file:
                    doc_content=file.read() #reutrns string 
                    file.close() 

               read_doc_obj=self.Processed_Document_Obj(paragaphs=doc_content)
               pass
          elif doc_type ==".PPTX":
               # ref: https://medium.com/@alice.yang_10652/extract-text-from-powerpoint-ppt-or-pptx-with-python-shapes-tables-notes-smartart-and-more-18e1381018e0

               doc_content=""
               #TEAM: metadata please

               #if i want to get the OCRed images out then i need to convert pptx to pdf then ocr pdf : soffice --headless --convert-to pdf slide.pptx && ocrmypdf --force-ocr slide.pdf slide_ocr.pdf



               read_doc_obj=self.Processed_Document_Obj(paragaphs=doc_content)
               pass


          #==== Recurrsion for document files. 
          elif doc_type ==".ZIP":
               print("TODO: File Reader: Zip")
               #ref: https://www.geeksforgeeks.org/python/working-zip-files-python/

               doc_content=""
               #TEAM: metadata please

               #read zip files. 

               with zipfile.ZipFile(docuemnt, "r") as zip_ref:
                    files_in_zip=zip_ref.printdir()
               
               
               for file in files_in_zip:
                    #read documents in a zip file. 
                    with zipfile.ZipFile(docuemnt, "r") as zipf:
                         content = zipf.read(file)
                         doc_content=content.decode()


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

          return read_doc_obj

     def __unzip_zip_files(self):
          #get list of files, 
          # path(for file in files).suffix() =="zip" : cmd= "unzip to __injest"
          pass


     #========== Call out to model to get metadata tags. 
     def __call_ollama_on_a_file(self, document, ollama_off):       #private method
          if ollama_off ==True:
               #Ollama is offline-- boot it. 
               #check if ollama is running -- start otherwise.  
               #check if computer has enough ram to boot ollama 14b param 
               #activate ollama 
               first_run=False     

          crashes=0
          response=""
          while crashes<self.err_model_crash:
               try:
                    print("sending request to model ")

                    response=ollama.chat(
                         model=CONST["MODEL_NAME"],               
                         messages=[{
                              "role":"user",
                              "content": f"{CONST['PROMPT']} \n {document}"
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

          return response     


     #=== Meta ===
     def controller(self):  #TEAM: can we please order the methods in the same sequence as we see here?
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
                    # processed_doc_objs+= self.__read_a_document(key, file).to_json()

          # #=== Send the object to ollama to read over.
          ollama_off=0 
          # for processed_document in processed_doc_objs:
          #      self.__call_ollama_on_a_file(processed_document)


          #=== Dev/Debug area.  #-- the following files were tested and work
          root="/home/chris/Desktop/4260_presentation/Modules/___ingest_file/"
          doc_metadata= self.__read_a_document(".PDF",root+"temp.pdf")
          # doc_metadata= self.__read_a_document(".DOCX",root+"temp.docx")
          # doc_metadata= self.__read_a_document(".CSV",root+"temp.csv")
          # doc_metadata= self.__read_a_document(".TXT",root+"ppt_x.txt")
          x=doc_metadata.to_json()
          response_obj=self.__call_ollama_on_a_file(x, ollama_off) 

          print(response_obj)

          # print(x)



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

               return {
                    "title": self.standardize_text( "title"),
                    "paragraphs":self.standardize_text ("paragaphs"),  
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
          doc_obj="" #processed_doc_obj -- instances. 

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

          def __init__(self,
                    #    doc_obj:Processed_Document_Obj
                       doc_obj,ai_summary, ai_description, ai_send_reason, ai_keywords, ai_topics, ai_entities, ai_document_type, ai_sentiment, ai_language, ai_date_references):
               self.doc_obj= doc_obj
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

               pass
          





