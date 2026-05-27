import sqlite3 
import json
from typing import Optional, Dict, Any, List
from contextlib import closing

#=== Interface Import
from .my_sql_db_interface import CONST

class SQL_DataBase():

     #=== DB CONFIG 
     DB_PATH=CONST["DB_PATH"]
     CREATE_TABLE=CONST["CREATE_TABLE_SQL"]
     CREATE_TRIGGER=CONST["CREATE_TRIGGER_SQL"]
     JSON_FIELDS=CONST["JSON_FIELDS"]

     #Tables 
     OG_DOC=CONST["INSERT_DOCUMENT_SQL"]
     AI_DOC=CONST["INSERT_AI_SQL"]
     


     #=== Tracking 
     id_list=[] #track entries in db 


     def __init__(self):
          self.__initialize()

#== Create    
     #-- DB initalize  
     def __get_conn(self ) -> sqlite3.Connection:
          conn = sqlite3.connect(self.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
          conn.row_factory = sqlite3.Row
          return conn

     def __initialize(self) -> None:
          conn=self.__get_conn()

          with conn:
               conn.executescript(
                    f"{self.CREATE_TABLE}\n{self.CREATE_TRIGGER}"  # Fix 8: use correct attr names (not _SQL suffix)
               )
               conn.commit()
          
          self.get_conn = conn

#== Write
     def insert_document(self, og_doc: dict, ai_doc: dict) -> None:
          # serialize any list fields to JSON strings before storing
           # parse if passed in as a JSON string
          if isinstance(ai_doc, str):
               ai_doc = json.loads(ai_doc)

          ai_serialized = ai_doc.copy()
          
          for field in ["keywords", "topics", "entities", "date_references"]:
               if field in ai_serialized and isinstance(ai_serialized[field], list):
                    ai_serialized[field] = json.dumps(ai_serialized[field])

          # both inserts share the same doc_hash, wrap in one transaction
          with self.__get_conn() as conn:
               conn.execute(self.OG_DOC, og_doc)
               conn.execute(self.AI_DOC, {"doc_hash": og_doc["doc_hash"], **ai_serialized})
               conn.commit()

     def update_document(self, doc_hash: str, doc_updates: dict = None, ai_updates: dict = None) -> None:
          """Update fields in either or both tables by doc_hash."""
          with self.__get_conn() as conn:

               if doc_updates:
                    # serialize any list fields
                    for field in self.JSON_FIELDS:
                         if field in doc_updates and isinstance(doc_updates[field], list):
                              doc_updates[field] = json.dumps(doc_updates[field])

                    fields = ", ".join(f"{k} = :{k}" for k in doc_updates.keys())
                    sql = f"UPDATE documents SET {fields} WHERE doc_hash = :doc_hash"
                    conn.execute(sql, {**doc_updates, "doc_hash": doc_hash})

               if ai_updates:
                    # serialize any list fields
                    for field in self.JSON_FIELDS:
                         if field in ai_updates and isinstance(ai_updates[field], list):
                              ai_updates[field] = json.dumps(ai_updates[field])

                    fields = ", ".join(f"{k} = :{k}" for k in ai_updates.keys())
                    sql = f"UPDATE ai_analysis SET {fields} WHERE doc_hash = :doc_hash"
                    conn.execute(sql, {**ai_updates, "doc_hash": doc_hash})

               conn.commit()

     def delete_document(self, doc_hash: str) -> None:
          """Delete a document and its ai_analysis by doc_hash."""
          with self.__get_conn() as conn:
               conn.execute("DELETE FROM ai_analysis WHERE doc_hash = ?", (doc_hash,))
               conn.execute("DELETE FROM documents WHERE doc_hash = ?", (doc_hash,))
               conn.commit()

     def get_document(self, doc_hash: str) -> dict | None:
          """Get a single document joined with its ai_analysis by doc_hash."""
          sql = """
               SELECT d.*, a.summary, a.description, a.send_reason, a.keywords,
                         a.topics, a.entities, a.document_type, a.sentiment, 
                         a.language, a.date_references
               FROM documents d
               LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
               WHERE d.doc_hash = ?
          """
          with self.__get_conn() as conn:
               row = conn.execute(sql, (doc_hash,)).fetchone()
               return self.__deserialize_row(row)

     def get_first_document(self) -> dict | None:
          """Get the first document joined with its ai_analysis."""
          sql = """
               SELECT d.*, a.summary, a.description, a.send_reason, a.keywords,
                         a.topics, a.entities, a.document_type, a.sentiment,
                         a.language, a.date_references
               FROM documents d
               LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
               LIMIT 1
          """
          with self.__get_conn() as conn:
               row = conn.execute(sql).fetchone()
               return self.__deserialize_row(row)

     def __deserialize_row(self, row: sqlite3.Row) -> dict | None:
          """Convert a sqlite3.Row to a dict, deserializing any JSON fields."""
          if row is None:
               return None
          
          result = dict(row)
          
          for field in self.JSON_FIELDS:
               if field in result and result[field] is not None:
                    try:
                         result[field] = json.loads(result[field])
                    except (json.JSONDecodeError, TypeError):
                         pass  # leave as-is if it can't be parsed
          
          return result

     #== Meta
          #===!! danger !!===
     def DEV_drop_db_table(self):
          with self.__get_conn() as conn:
               conn.execute("DROP TABLE IF EXISTS documents")
               conn.commit()

         