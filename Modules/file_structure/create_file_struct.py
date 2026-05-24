# ============== DESCRIPTION OF PROJECT ==============
# This file is going to be responsible for creating the file stucture for the project. 
# We should create a Dynamic file structure.

# ====================================================

#=== libraries
from pathlib import Path

#=== class interface
from .interface import Interface_FileStructure
from .interface import CONSTS


class FileStructure(Interface_FileStructure):
     #=== metadata
     silence_output=CONSTS["SILENCE"]
     err_code=CONSTS["ERR_CODE"]
     err_text=CONSTS["ERR_TXT"]

     #===== File names =====
     inject_file_name=CONSTS["INPUT_FILE_NAME"] 
     inject_file_path=None
     
     processed_file_name=CONSTS["OUTPUT_FILE_NAME"]
     processed_file_path= None

     #== path exists 
     path_exists="path already exists. "

     #===== Paths =====
     script_path = None
     parent_path = None
     root_dir=None

     def __init__(self):
          #=== paths
          self.get_script_path()
          self.get_parent_path()
          self.get_root_path()


     #=========== File creators ========
     def create_inject_file(self):
          #check if the file exists. 
          path=f"{self.get_root_path()}/{self.inject_file_name}"
          self.inject_file_path=path
          
          if( not Path(path).exists()): #if the path does not exist create it 
               Path(path).mkdir(parents=False, exist_ok=False )    #creates the file if it doesn't exist
          elif (not self.silence_output):
               print(f"{self.path_exists}  {path} ")
     
     def create_processed_file(self):
          path=f"{self.get_root_path()}/{self.processed_file_name}"
          self.processed_file_path=path

          if( not Path(path).exists()): #if the path does not exist create it 
               Path(path).mkdir(parents=False, exist_ok=False )    #creates the file if it doesn't exist
          elif (not self.silence_output):
               print(f"{self.path_exists}  {path} ")

     #==  Getters
     def get_inject_file_path(self):
          if (self.inject_file_name) == None:
               print(f"{self.err_text}: file locations need to be created before location can be given")
               return self.err_code 
          else:
               return self.inject_file_path
     
     def get_processed_file_path(self):
          if (self.processed_file_path) ==None:
               print(f"{self.err_text}: file locations need to be created before location can be given")
               return self.err_code
          return self.processed_file_path


     #=========== Paths ================
     def get_script_path(self): #path of this script
          self.script_path= Path(__file__).resolve()
          return self.script_path
     
     def get_parent_path(self): #path of the parent dir 
          self.parent_path = self.get_script_path().parent
          return self.parent_path
     
     def get_root_path(self):
          self.root_dir=self.parent_path.parent#.parent
          return self.root_dir

     