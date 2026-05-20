# ============== DESCRIPTION OF PROJECT ==============
# This file is going to be responsible for creating the file stucture for the project. 
# We should create a Dynamic file structure.

# ====================================================
from pathlib import Path

class FileStructure:
     #===== File names =====
     inject_file_name="___ingest"
     processed_file_name="___processed"

     #== path exists 
     path_exists="path already exists. "

     #===== Paths =====
     script_path = None
     parent_path = None
     root_dir=None

     def __init__(self):
          #==== get patths====
          self.get_script_path()
          self.get_parent_path()
          self.get_root_path()

          #=== create file structure ===
          self.create_inject_file()
          self.create_processed_file()

     #=========== File creators ========
     def create_inject_file(self):
          #check if the file exists. 
          path=f"{self.get_root_path()}/{self.inject_file_name}"
          if( not Path(path).exists()): #if the path does not exist create it 
               Path(path).mkdir(parents=False, exist_ok=False )    #creates the file if it doesn't exist
          else:
               print(f"{self.path_exists}  {path} ")


     def create_processed_file(self):
          path=f"{self.get_root_path()}/{self.processed_file_name}"
          if( not Path(path).exists()): #if the path does not exist create it 
               Path(path).mkdir(parents=False, exist_ok=False )    #creates the file if it doesn't exist
          else:
               print(f"{self.path_exists}  {path} ")


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
     

FileStructure()