#=== Libraries. 
import chromadb
from pathlib import Path


#=== Local objs
from .embedding_interface import Embedding_Interface, CONST
from ..engine_injesting.data_base.my_sql_db import SQL_DataBase


class Embedding_Engine(Embedding_Interface):

     #get the objects from the DB one at a time .
     def __init__(self):
          self.collection = self.__get_DB_connection()


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
          db_client=chromadb.PersistentClient(path=str(db_path))
          collection = db_client.get_or_create_collection(
               name=CONST["CHROMA_DB_TABLE_NAME"],
               metadata={"hnsw:space": CONST["CHROMA_DB_CONFIG_space"]},
               #configuration={
                    #"hnsw":{ #for descriptions of each please look at the interface
                         #"space": CONST["CHROMA_DB_CONFIG_space"], 
                         #"ef_construction":CONST["CHROMA_DB_CONFIG_ef_construction"], 
                         #"ef_search":CONST["CHROMA_DB_CONFIG_ef_search"], 
                         #"max_neighbors":CONST["CHROMA_DB_CONFIG_max_neighbors"], 
                         #"num_threads":CONST["CHROMA_DB_CONFIG_num_threads"], 
                         #"resize_factor":CONST["CHROMA_DB_CONFIG_resize_factor"], 
                         #"batch_size":CONST["CHROMA_DB_CONFIG_batch_size"], 
                         #"sync_threshold":CONST["CHROMA_DB_CONFIG_sync_threshold"], 
                    #}
               #}
          )
          return collection

     def __get_DB_connection(self):
          #create the database. 
          db_path=self.__create_db_dir_n_path()
          collection=self.__create_persistent_data_base(db_path)
          return collection
     
     # == Safe text for search.
     def __safe_text(self, value):
          if value is None:
               return ""
          if isinstance(value, list):
               return ", ".join(str(v).strip() for v in value if v is not None and str(v).strip())
          if isinstance(value, dict):
               return str(value)
          return str(value).strip()
     
     # == Build the search text from the object
     def __build_search_text(self, obj: dict) -> str:
          parts = [
               f"Title: {self.__safe_text(obj.get('title'))}",
               f"Original filename: {self.__safe_text(obj.get('original_filename'))}",
               f"Source: {self.__safe_text(obj.get('source'))}",
               f"Sender: {self.__safe_text(obj.get('sender'))}",
               f"Email subject: {self.__safe_text(obj.get('email_subject'))}",
               f"Summary: {self.__safe_text(obj.get('summary'))}",
               f"Description: {self.__safe_text(obj.get('description'))}",
               f"Keywords: {self.__safe_text(obj.get('keywords'))}",
               f"Topics: {self.__safe_text(obj.get('topics'))}",
               f"Entities: {self.__safe_text(obj.get('entities'))}",
               f"Reason sent: {self.__safe_text(obj.get('send_reason'))}",
               f"Document type: {self.__safe_text(obj.get('document_type'))}",
               f"Extracted text: {self.__safe_text(obj.get('extracted_text'))}",
          ]

          text = "\n".join(part for part in parts if part and part.strip())

          max_chars = 12000
          return text[:max_chars]

     # == Build metadata for the object
     def __build_metadata(self, obj: dict) -> dict:
          return {
               "doc_hash": self.__safe_text(obj.get("doc_hash")),
               "title": self.__safe_text(obj.get("title")),
               "original_filename": self.__safe_text(obj.get("original_filename")),
               "source": self.__safe_text(obj.get("source")),
               "sender": self.__safe_text(obj.get("sender")),
               "email_subject": self.__safe_text(obj.get("email_subject")),
               "author": self.__safe_text(obj.get("author")),
               "document_type": self.__safe_text(obj.get("document_type")),
               "sentiment": self.__safe_text(obj.get("sentiment")),
               "language": self.__safe_text(obj.get("language")),
               "modified_date": self.__safe_text(obj.get("modified_date")),
               "time_creation": self.__safe_text(obj.get("time_creation")),
          }

     # == Implement abstract methods
     def embed_processed_document(self, obj: dict):
          doc_hash = self.__safe_text(obj.get("doc_hash")).strip()
          if not doc_hash:
               raise ValueError("Missing doc_hash for embedding")

          document_text = self.__build_search_text(obj).strip()
          if not document_text:
               raise ValueError(f"No searchable content found for doc_hash={doc_hash}")

          metadata = self.__build_metadata(obj)

          self.collection.upsert(
               ids=[doc_hash],
               documents=[document_text],
               metadatas=[metadata],
          )

     def __get_unprocessed_SQL_objs(self):
          return SQL_DataBase().get_unprocessed_documents()

     def __mark_db_obj_processed(self, doc_hash):
          SQL_DataBase().mark_processed(doc_hash)

     # == Implement abstract methods
     def embed_unprocessed_document(self):
          while True:
               unprocessed_obj = self.__get_unprocessed_SQL_objs()
               if unprocessed_obj is None:
                    break

               print(f"embedding document titled: {unprocessed_obj.get('title', 'Untitled')}")
               self.embed_processed_document(unprocessed_obj)
               self.__mark_db_obj_processed(unprocessed_obj["doc_hash"])

     # == Implement abstract methods
     def send_query(self, query_txt: str, num_results_return: int):
          query_txt = (query_txt or "").strip()
          if not query_txt:
               return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

          num_results_return = max(1, int(num_results_return))

          return self.collection.query(
               query_texts=[query_txt],
               n_results=num_results_return,
          )

     def get_document(self, doc_hash: str):
          return self.collection.get(ids=[doc_hash])

          
     def delete_document(self, doc_hash: str):
          self.collection.delete(ids=[doc_hash])

     #== Create entries. 
     #def __create_chromaDB_entry(self, collection, obj, hash):
     #     query_text=f""" 
     #     {obj["summary"] }
     #    {obj["description"] }

     #     document title: {"".join( obj["title"]) }
     #     keywords: {"".join(obj["keywords"]) }
     #     topic: {"".join(obj["topics"])}
     #     entities: {"".join(obj["entities"]) }
     #     reason sent: {"".join(obj["send_reason"])}
     #     """

     #     collection.upsert( #update or insert  #-- emails have threats 
     #          ids=[ hash ],
     #          documents=[query_text],
     #          metadatas=[{
     #               "title": obj.get("title", ""),
     #               "header_footer": obj["header_footer"],
     #               "table_content": obj["table_content"],
     #               "author": obj["author"],
     #               "time_creation": obj["time_creation"],
     #               "modified_date": obj["modified_date"],
     #               "file_computer_id": obj["file_computer_id"],
     #               "send_reason": obj["send_reason"],
     #               "document_type": obj["document_type"],
     #               "sentiment": obj["sentiment"],
     #               "language": obj["language"],
     #               "date_references": ", ".join(obj["date_references"]) if obj["date_references"] else ""
     #          }]
     #     )

#== Read values 
     #def __query_chromaDB(self,collection,  _query, num_results_return):
     #     return collection.query(
     #          query_texts=[_query],
     #          n_results=num_results_return
     #     )


#==== SQL DB obj control 
     #== Get the obj
     #def __get_unprocessed_SQL_objs(self) :
      #    return SQL_DataBase().get_unprocessed_documents()
     
     #== mark the obj as processed
     #def __mark_db_obj_processed(self, hash):
     #     SQL_DataBase().mark_processed(hash)


     #=== Embedder 
     #def embed_unprocessed_document(self):    
     #     collection=self.__get_DB_connection()

     #    while True:
     #          unprocessed_obj=self.__get_unprocessed_SQL_objs()
     #          if unprocessed_obj == None:
     #               break
               
     #          print(f"embedding document titled:  {unprocessed_obj['title']}")
     #          hash=unprocessed_obj["doc_hash"]
     #          self.__create_chromaDB_entry(collection, unprocessed_obj,hash)
     #          self.__mark_db_obj_processed(hash)
          
                    
     #=== Read 
     #def send_query(self, query_txt:str,num_results_return:int):
     #     collection=self.__get_DB_connection()
     #     return self.__query_chromaDB(collection,query_txt, num_results_return)

          
