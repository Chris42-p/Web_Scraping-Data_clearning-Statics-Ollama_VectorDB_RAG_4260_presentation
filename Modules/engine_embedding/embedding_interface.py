

from abc import ABC, abstractmethod

CONST={
#====== Chroma DB 
     #== DB Meta
     "CHROMA_DB_DIR":"data_base",
     "CHROMA_DB_NAME":"chroma_db",
     "CHROMA_DB_TABLE_NAME":"documents",

     #== DB config.  -- 1-500 range 
     "CHROMA_DB_CONFIG_space":"cosine", 
     "CHROMA_DB_CONFIG_ef_construction":400, #quality of embedding
     "CHROMA_DB_CONFIG_ef_search":30, #quality of search 
     "CHROMA_DB_CONFIG_max_neighbors":32, #node graph size
     "CHROMA_DB_CONFIG_num_threads":4,  #num cpu to process on
     "CHROMA_DB_CONFIG_resize_factor":1.3, #size of storage for db increase
     "CHROMA_DB_CONFIG_batch_size":150,  #how many vectors processed together
     "CHROMA_DB_CONFIG_sync_threshold":1000, # how many vectors processed before write to disk
}




class Embedding_Interface(ABC):

     @abstractmethod
     def embed_unprocessed_document(self): pass

     @abstractmethod
     def send_query(self, query):pass
     
