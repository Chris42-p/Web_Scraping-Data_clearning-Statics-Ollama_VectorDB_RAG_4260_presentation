# going to use this to orchistrate the exeuction of the scripts. 

import json

from Modules.file_structure import FileStructure
from Modules.engine_injesting import Injest_Engine
from Modules.engine_embedding import Embedding_Engine


#==== File Structure ====
def create_file_structure():
     #==== Create ===
     injest_location=FileStructure()
     injest_location.create_inject_file()
     injest_location.create_processed_file()

     #=== Get paths
     input_files_path=injest_location.get_inject_file_path()
     output_files_path=injest_location.get_processed_file_path()

     return input_files_path,output_files_path

def injest_files(input_files_path,output_files_path):
     return Injest_Engine(input_files_path,output_files_path).controller()

def move_processed_files(files_to_move):
     FileStructure().move_processed_files(files_to_move) #TODO: havent implemented

def embed_into_VecDB_files():
     Embedding_Engine().embed_unprocessed_document()

def send_VecDB_query(query, num_results):
     response =Embedding_Engine().send_query(query,num_results)
     print(response)

#use this method to control the execution of the application. 
def main():

     #==== Get the documents and process them ====
     input_files_path,output_files_path= create_file_structure()
     processed_doc=injest_files (input_files_path,output_files_path) #muted for development - there are DB entries already. 
     
     embed_into_VecDB_files()
     send_VecDB_query("testing document", 4)

     # move_processed_files(processed_doc)



main()