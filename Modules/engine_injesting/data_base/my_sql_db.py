import sqlite3 
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import closing
from werkzeug.security import generate_password_hash, check_password_hash


#=== Interface Import
from .my_sql_db_interface import CONST


class SQL_DataBase():

     #=== DB CONFIG 
     DB_PATH=""
     CREATE_TABLE=CONST["CREATE_TABLE_SQL"]
     CREATE_TRIGGER=CONST["CREATE_TRIGGER_SQL"]
     JSON_FIELDS=CONST["JSON_FIELDS"]

     #Tables 
     OG_DOC=CONST["INSERT_DOCUMENT_SQL"]
     AI_DOC=CONST["INSERT_AI_SQL"]
     


     #=== Tracking 
     id_list=[] #track entries in db 


     def __init__(self):
          base_path=Path(__file__).parent
          self.DB_PATH=f"{base_path}/{CONST['DB_PATH']}"

          self.__initialize()

#== Create    
     #-- DB initalize  
     def __get_conn(self ) -> sqlite3.Connection:
          conn = sqlite3.connect(self.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
          conn.row_factory = sqlite3.Row
          return conn

     def __initialize(self) -> None:
          with self.__get_conn() as conn:
               conn.executescript(f"{self.CREATE_TABLE}\n{self.CREATE_TRIGGER}")
               self.__ensure_document_columns(conn)
               conn.commit()

          #with conn:
          #     conn.executescript(
          #          f"{self.CREATE_TABLE}\n{self.CREATE_TRIGGER}"  # Fix 8: use correct attr names (not _SQL suffix)
          #     )
          #     conn.commit()
          
          #self.get_conn = conn

     #== User Management create, authenticate, and retrieve user info
     def create_user(
          self,
          username: str,
          password: str,
          full_name: str,
          email: str | None,
          phone: str | None,
          ) -> None:
          """Create a new user with a hashed password."""
          password_hash = generate_password_hash(password)

          try:
               with self.__get_conn() as conn:
                    conn.execute(
                         """
                         INSERT INTO users (username, password_hash, full_name, email, phone)
                         VALUES (?, ?, ?, ?, ?)
                         """,
                         (username, password_hash, full_name, email, phone),
                    )
                    conn.commit()
          except sqlite3.IntegrityError as e:
               raise ValueError(f"Username '{username}' already exists") from e
     
     #== User authentication and retrieval
     def authenticate_user(self, username: str, password: str) -> dict | None:
          """Authenticate a user and return their info if valid."""
          with self.__get_conn() as conn:
               row = conn.execute(
                    """
                    SELECT id, username, password_hash
                    FROM users 
                    WHERE username = ?
                    """,
                    (username,)
               ).fetchone()

          if row is None:
               return None

          if not check_password_hash(row["password_hash"], password):
               return None

          return {
               "id": row["id"], 
               "username": row["username"]
          }

     #== User retrieval by username
     def get_user_by_username(self, username: str) -> dict | None:
          with self.__get_conn() as conn:
               row = conn.execute(
                    """
                    SELECT id, username, full_name, email, phone, created_at
                    FROM users
                    WHERE username = ?
                    """,
                    (username,)
               ).fetchone()

               return dict(row) if row else None
     

     def create_feedback_table(self) -> None:
          with self.__get_conn() as conn:
               conn.execute("""
                    CREATE TABLE IF NOT EXISTS app_feedback (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id INTEGER NOT NULL UNIQUE,
                         rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                         comment TEXT,
                         created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                         updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                         FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
               """)
               conn.commit()

     def save_or_update_feedback(self, user_id: int, rating: int, comment: str | None) -> None:
          with self.__get_conn() as conn:
               existing = conn.execute(
                    "SELECT id FROM app_feedback WHERE user_id = ?",
                    (user_id,)
               ).fetchone()

               if existing:
                    conn.execute("""
                         UPDATE app_feedback
                         SET rating = ?, comment = ?, updated_at = CURRENT_TIMESTAMP
                         WHERE user_id = ?
                    """, (rating, comment or "", user_id))
               else:
                    conn.execute("""
                         INSERT INTO app_feedback (user_id, rating, comment)
                         VALUES (?, ?, ?)
                    """, (user_id, rating, comment or ""))
               conn.commit()

     def get_feedback_for_user(self, user_id: int) -> dict | None:
          with self.__get_conn() as conn:
               row = conn.execute("""
                    SELECT id, user_id, rating, comment, created_at, updated_at
                    FROM app_feedback
                    WHERE user_id = ?
               """, (user_id,)).fetchone()
               return dict(row) if row else None
     
#== write
     def insert_document(self, og_doc: dict, ai_doc: dict) -> None:
          # serialize any list fields to JSON strings before storing
          # parse if passed in as a JSON string
          if isinstance(ai_doc, str):
               ai_doc = json.loads(ai_doc)

          ai_serialized = ai_doc.copy()
          
          for field in CONST["JSON_FIELDS"]:
               if field in ai_serialized and isinstance(ai_serialized[field], list):
                    ai_serialized[field] = json.dumps(ai_serialized[field])

          # both inserts share the same doc_hash, wrap in one transaction
          with self.__get_conn() as conn:
               conn.execute(self.OG_DOC, og_doc)
               conn.execute(self.AI_DOC, {"doc_hash": og_doc["doc_hash"], **ai_serialized})
               conn.commit()

#== update
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

#==delte
     def delete_document(self, doc_hash: str) -> None:
          """Delete a document and its ai_analysis by doc_hash."""
          with self.__get_conn() as conn:
               conn.execute("DELETE FROM ai_analysis WHERE doc_hash = ?", (doc_hash,))
               conn.execute("DELETE FROM documents WHERE doc_hash = ?", (doc_hash,))
               conn.commit()

#== read
     def get_document_by_hash(self, doc_hash: str) -> dict | None:
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

     def get_unprocessed_documents(self) ->dict |None:
          sql = """
               SELECT d.*, a.summary, a.description, a.send_reason, a.keywords,
                         a.topics, a.entities, a.document_type, a.sentiment,
                         a.language, a.date_references
               FROM documents d
               LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
               WHERE d.processed = 0
               LIMIT 1
          """
          with self.__get_conn() as conn:
               row = conn.execute(sql).fetchone()
               return self.__deserialize_row(row) if row else None

     

#== Util 
     def mark_processed(self, doc_hash: str) -> None:

          with self.__get_conn() as conn:
               conn.execute("UPDATE documents SET processed = 1 WHERE doc_hash = ?",(doc_hash,))
               conn.commit()


     def __deserialize_row(self, row: sqlite3.Row) -> dict | None:
          
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



     def get_first_document(self) -> dict | None: #might delete this method
          # Get the first document joined with its ai_analysis.
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


     def get_reports(self) -> list[dict]:
          sql = """
               SELECT
                    d.doc_hash,
                    d.title,
                    d.author,
                    d.time_creation,
                    d.modified_date,
                    d.original_filename,
                    d.mime_type,
                    a.summary,
                    a.description,
                    a.send_reason,
                    a.keywords,
                    a.topics,
                    a.entities,
                    a.document_type,
                    a.sentiment,
                    a.language,
                    a.date_references
               FROM documents d
               INNER JOIN ai_analysis a
                    ON d.doc_hash = a.doc_hash
               WHERE a.summary IS NOT NULL
               AND TRIM(a.summary) <> ''
               ORDER BY d.modified_date DESC, d.time_creation DESC
          """
          with self.__get_conn() as conn:
               rows = conn.execute(sql).fetchall()
               return [self.__deserialize_row(row) for row in rows]
          
     def get_reports_count(self) -> int:
          sql = """
               SELECT COUNT(*)
               FROM documents d
               INNER JOIN ai_analysis a
                    ON d.doc_hash = a.doc_hash
               WHERE a.summary IS NOT NULL
               AND TRIM(a.summary) <> ''
          """
          with self.__get_conn() as conn:
               row = conn.execute(sql).fetchone()
               return int(row[0]) if row else 0

     #== Meta
          #===!! danger !!===
     #def DEV_drop_db_table(self):
     #     with self.__get_conn() as conn:
     #          conn.execute("DROP TABLE IF EXISTS documents")
     #          conn.commit()

     def __ensure_document_columns(self, conn: sqlite3.Connection) -> None:
        rows = conn.execute("PRAGMA table_info(documents)").fetchall()
        existing_columns = {row["name"] for row in rows}

        required_columns = {
               "stored_filename": "TEXT",
               "relative_path": "TEXT",
               "original_filename": "TEXT",
               "mime_type": "TEXT",
        }

        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                conn.execute(
                    f"ALTER TABLE documents ADD COLUMN {column_name} {column_type}"
               )

     def insert_document_with_file_metadata(
          self,
          doc_hash: str,
          title: str,
          author: str,
          stored_filename: str,
          relative_path: str,
          original_filename: str,
          mime_type: str,
     ) -> None:
          with self.__get_conn() as conn:
               conn.execute(
                """
                    INSERT INTO documents (
                    doc_hash,
                    title,
                    author,
                    stored_filename,
                    relative_path,
                    original_filename,
                    mime_type
               )
               VALUES (?, ?, ?, ?, ?, ?, ?)
               """,
               (
                    doc_hash,
                    title,
                    author,
                    stored_filename,
                    relative_path,
                    original_filename,
                    mime_type,
               ),
          )
          conn.commit()

     def DEV_drop_db_table(self):
          with self.__get_conn() as conn:
               conn.execute("DROP TABLE IF EXISTS ai_analysis")
               conn.execute("DROP TABLE IF EXISTS documents")
               conn.execute("DROP TABLE IF EXISTS users")
               conn.commit()
         