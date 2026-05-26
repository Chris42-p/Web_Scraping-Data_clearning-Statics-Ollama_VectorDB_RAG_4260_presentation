# going to use this to orchistrate the exeuction of the scripts. 


from Modules.file_structure import FileStructure

from Modules.engine_injesting import Injest_Engine

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
     processed_doc_obj=Injest_Engine(input_files_path,output_files_path)
     
     print(processed_doc_obj)
     # need to trigger file_structure engine to move the files to _processed_files ... maybe after they are injested into the db?





#use this method to control the execution of the application. 
def main():
     input_files_path,output_files_path= create_file_structure()
     
     injest_files (input_files_path,output_files_path)
     


main()