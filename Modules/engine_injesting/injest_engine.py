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

#=== local imports
from .injest_interface import Interface_InjestionEngine
from .injest_interface import CONST



class Injest_Engine(Interface_InjestionEngine):
     #=== Meta Data ====
     err_text=CONST["ERR_TXT"]
     err_code=CONST["ERR_CODE"]

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

                    cmd="ocrmypdf --optimize 1 --skip-text {0} {1}".format(str(file), str(output_file_name)) 

                    #OCR the doc 
                    try:
                         subprocess.run(cmd.split(" "),check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                         print(f"Processed {file}")
                    except subprocess.CalledProcessError as e:
                         print(f"{self.err_text}: {e.stdout} ")

     #open the file and read their content. 
     def __read_a_document(self,doc_type, docuemnt): #recurrsion on .zip & .eml
          read_doc_obj=None   

          if doc_type ==".PDF":
               #ref: https://www.geeksforgeeks.org/python/working-with-pdf-files-in-python/

               reader= PdfReader(str(docuemnt)) 

               #Read text on page
               doc_content=""          
               num_pages=len(reader.pages)     
               for page in range(num_pages):
                    doc_content+=f"{page}: {reader.pages[page].extract_text()}"
          
               #OCR images?
               
               #Tables being absorbed?

               #== Meta==
               #Who made it, at what time?
               #does it have creaters computer ID?

               read_doc_obj= self.Processed_Document_Obj(paragaphs=doc_content) #TEAM: please fill it in. 
          elif doc_type == ".DOCX": 
               #ref: https://pytutorial.com/python-docx-tutorial-read-parse-docx-content/

               doc=Document(docuemnt)
               #read headers and footer. 
               for section in doc.sections:
                    header= section.header
                    for paragraph in header.paragraphs:
                         print(f"Header: {paragraph.text}")

               #read tables. 
               for i, table in enumerate(doc.tables):
                    print(f"Table {i+1}")
                    for row in table.rows:
                         row_data=[cell.text for cell in row.cells]
                         print(row_data)

               #read paragraphs
               doc_content=""
               for paragraph in doc.paragraphs: #can index into paragraphs also 
                    doc_content+=paragraph.text 
               
               #extracting 

               # Access document properties
               props = doc.core_properties
               print(f"Title: {props.title}")
               print(f"Author: {props.author}")
               print(f"Created: {props.created}")
               print(f"Modified: {props.modified}")

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
               


               read_doc_obj=self.Processed_Document_Obj(paragaphs=doc_content)
               pass


          #==== Recurrsion for document files. 
          elif doc_type ==".ZIP":
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


          #what's the document's hash
          read_doc_obj.hash_document()

          return read_doc_obj



     #========== Call out to model to get metadata tags. 
     def __call_ollama_on_a_file(self, document):       #private method

          response=ollama.chat(
               mode=CONST["MODEL_NAME"],               
               messages=[{
                    "role":"user",
                    "content": f"{CONST['PROMPT']} \n {document}"
                    
                    }]
               )

          print(response)
          return response     


     #=== Meta ===
     def controller(self):
          #=== Process the files
          self.__get_files_in_injest_file()
          
          #TEAM: need to process zip file, like for directories, otherwise the files are inaccessible # this would be control order for method

          self.__group_files_by_ext()
          self.__ocr_my_pdf()

          #=== injest documents
          for key, value in self.files_grouped_typ_type.items():
               for file in value:
                    doc_str = self.__read_a_document(key, file)       

     #===== Utility

     class Processed_Document_Obj:
          #document itself
          title =None
          paragaphs =None
          header_footer =None
          table_content =None

          #== meta data
          author =None
          time_creation =None
          modified_date=None
          file_computer_id=None

          #== hahses 
          doc_hash=None

          def __init__(self, title=None, paragaphs=None, header_footer=None, 
                              table_content=None, author=None, time_creation=None, 
                              modified_date=None, file_computer_id=None):
               self.title=title
               self.paragaphs=paragaphs 
               self.header_footer=header_footer 
               self.table_content=table_content 

               #== meta data
               self.author=author
               self.time_creation=time_creation
               self.modified_date=modified_date
               self.file_computer_id=file_computer_id

          def get_object(self):
               return {} #create the object later 

          def hash_document(self):
               #hash the title, and author? -- quick look up?

               content = str(self.paragaphs) + str(self.title)
               self.doc_hash = hashlib.md5(content.encode()).hexdigest()







