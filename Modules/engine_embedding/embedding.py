#=== Libraries. 
import chromadb
from pathlib import Path
import json


#=== Local objs
from .embedding_interface import Embedding_Interface
from ..engine_injesting.data_base.my_sql_db import SQL_DataBase
from .embedding_interface import CONST



class Embedding_Engine(Embedding_Interface):

     #get the objects from the DB one at a time .
     def __init__(self, ):
          pass


#== Create the chroma DB
     def __create_db_dir_n_path(self):
          # mkdir if not exists
          base_path = Path(__file__).parent / CONST["CHROMA_DB_DIR"] 
          base_path.mkdir(parents=True, exist_ok=True) # create dir
          #create DB path 
          db_path=base_path /CONST["CHROMA_DB_NAME"]
          return (db_path)

     def __create_persistent_data_base(self, db_path):
          #https://cookbook.chromadb.dev/core/configuration/#hnsw-index-configuration
          db_client=chromadb.PersistentClient(db_path)
          collection = db_client.get_or_create_collection(
               name=CONST["CHROMA_DB_TABLE_NAME"],
               configuration={
                    "hnsw":{ #for descriptions of each please look at the interface
                         "space": CONST["CHROMA_DB_CONFIG_space"], 
                         "ef_construction":CONST["CHROMA_DB_CONFIG_ef_construction"], 
                         "ef_search":CONST["CHROMA_DB_CONFIG_ef_search"], 
                         "max_neighbors":CONST["CHROMA_DB_CONFIG_max_neighbors"], 
                         "num_threads":CONST["CHROMA_DB_CONFIG_num_threads"], 
                         "resize_factor":CONST["CHROMA_DB_CONFIG_resize_factor"], 
                         "batch_size":CONST["CHROMA_DB_CONFIG_batch_size"], 
                         "sync_threshold":CONST["CHROMA_DB_CONFIG_sync_threshold"], 
                    }
               }
          )
          return collection

     def __get_DB_connection(self):
          #create the database. 
          db_path=self.__create_db_dir_n_path()
          collection=self.__create_persistent_data_base(db_path)
          return collection
     
#== Create entries. 
     def __create_chromaDB_entry(self, collection, obj, hash):
          query_text=f""" 
{obj["summary"] }
{obj["description"] }

document title: {"".join( obj["title"]) }
keywords: {"".join(obj["keywords"]) }
topic: {"".join(obj["topics"])}
entities: {"".join(obj["entities"]) }
reason sent: {"".join(obj["send_reason"])}
          """

          collection.upsert( #update or insert  #-- emails have threats 
               ids=[ hash ],
               documents=[query_text],
               metadatas=[{
                    "title": obj.get("title", ""),
                    "header_footer": obj["header_footer"],
                    "table_content": obj["table_content"],
                    "author": obj["author"],
                    "time_creation": obj["time_creation"],
                    "modified_date": obj["modified_date"],
                    "file_computer_id": obj["file_computer_id"],
                    "send_reason": obj["send_reason"],
                    "document_type": obj["document_type"],
                    "sentiment": obj["sentiment"],
                    "language": obj["language"],
                    "date_references": obj["date_references"],
               }]
          )

#== Read values 
     def __query_chromaDB(self,collection,  _query, num_results_return):
          return collection.query(
               query_texts=[_query],
               n_results=num_results_return
          )


#==== SQL DB obj control 
     #== Get the obj
     def __get_unprocessed_SQL_objs(self) :
          return SQL_DataBase().get_unprocessed_documents()
     
     #== mark the obj as processed
     def __mark_db_obj_processed(self, hash):
          SQL_DataBase().mark_processed(hash)


     #=== Embedder 
     def embed_unprocessed_document(self):    
          collection=self.__get_DB_connection()

          while True:
               unprocessed_obj=self.__get_unprocessed_SQL_objs()
               if unprocessed_obj == None:
                    break
               
               print(f"embedding document titled:  {unprocessed_obj['title']}")
               hash=unprocessed_obj["doc_hash"]
               self.__create_chromaDB_entry(collection, unprocessed_obj,hash)
               self.__mark_db_obj_processed(hash)
          
                    
     #=== Read 
     def send_query(self, query_txt:str,num_results_return:int):
          collection=self.__get_DB_connection()
          return self.__query_chromaDB(collection,query_txt, num_results_return)

          
