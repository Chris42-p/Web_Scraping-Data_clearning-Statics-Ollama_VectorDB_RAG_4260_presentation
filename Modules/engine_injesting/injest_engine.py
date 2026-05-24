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
import ollama

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
     def __get_files_in_injest_files(self,path= None):
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
               self.__get_files_in_injest_files(next_dir)

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
     def __read_a_document(self,doc_type, docuemnt): #private method
          if doc_type ==".PDF":
               pass
          elif doc_type == ".DOCX":
               pass
          elif doc_type ==".CSV":
               pass
          elif doc_type ==".EML":
               pass
          elif doc_type ==".TXT":
               pass
          elif doc_type ==".PPTX":
               pass
          elif doc_type ==".ZIP":
               pass






          #be able to open one 
          pass

     #========== Call out to model to get metadata tags. 
     def __call_ollama_on_a_file():       #private method
          
          pass
     

     #=== Meta ===

     def controller(self):
          #=== Process the files
          self.__get_files_in_injest_files()
          self.__group_files_by_ext()
          self.__ocr_my_pdf()

          #=== injest documents

          # for value, key in self.files_grouped_typ_type():
          #      self.__read_a_document(key,value)
          #      self.__call_ollama_on_a_file()







