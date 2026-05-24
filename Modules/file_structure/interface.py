#=========== this is the interface for the file_structure module =======#

from abc import ABC, abstractmethod

#=======Constants for the object=====
CONSTS={
     "INPUT_FILE_NAME": "___ingest_file",
     "OUTPUT_FILE_NAME":"___processed_file",
     "SILENCE":True,


     "ERR_CODE":-1,
     "ERR_TXT":"Error occured",
}

#====== Class intercace =========
class Interface_FileStructure(ABC):
     
     @abstractmethod
     def create_inject_file(self):return
     
     @abstractmethod
     def create_processed_file(self):return

     
     #==== getters ===
     @abstractmethod
     def get_inject_file_path():return
     
     @abstractmethod
     def get_processed_file_path():return

     @abstractmethod
     def get_script_path(self):return

     @abstractmethod
     def get_parent_path(self):return

     @abstractmethod
     def get_root_path(self):return