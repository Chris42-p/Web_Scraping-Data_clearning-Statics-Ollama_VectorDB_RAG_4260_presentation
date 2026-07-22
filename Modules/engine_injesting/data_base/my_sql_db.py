import sqlite3 
import json
import os
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
          conn.execute("PRAGMA foreign_keys = ON")
          return conn

     def __initialize(self) -> None:
          with self.__get_conn() as conn:
               conn.executescript(f"{self.CREATE_TABLE}\n{self.CREATE_TRIGGER}")
               self.__ensure_document_columns(conn)
               self.__ensure_user_columns(conn)
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


     # == Ensure user table has required columns
     def __ensure_user_columns(self, conn: sqlite3.Connection) -> None:
          rows = conn.execute("PRAGMA table_info(users)").fetchall()
          existing_columns = {row["name"] for row in rows}

          required_columns = {
               "full_name": "TEXT",
               "email": "TEXT",
               "phone": "TEXT",
          }

          for column_name, column_type in required_columns.items():
               if column_name not in existing_columns:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")

#== write
     def insert_document(self, og_doc: dict, ai_doc: dict) -> None:
          # serialize any list fields to JSON strings before storing
          # parse if passed in as a JSON string
          if isinstance(ai_doc, str):
               ai_doc = json.loads(ai_doc)

          ai_serialized = ai_doc.copy()
          
          for field in CONST["JSON_FIELDS"]:
               if field in ai_serialized:
                    ai_serialized[field] = self.__prepare_db_value(ai_serialized[field])

          # both inserts share the same doc_hash, wrap in one transaction
          with self.__get_conn() as conn:
               conn.execute(self.OG_DOC, og_doc)
               conn.execute(self.AI_DOC, {"doc_hash": og_doc["doc_hash"], **ai_serialized})
               conn.commit()

#== update
     def update_document(
          self,
          doc_hash: str,
          doc_updates: dict = None,
          ai_updates: dict = None
          ) -> None:

          with self.__get_conn() as conn:

               # -------------------------
               # Update documents table
               # -------------------------
               if doc_updates:

                    normalized_doc_updates = {
                         key: self.__prepare_db_value(value)
                         for key, value in doc_updates.items()
                    }

                    fields = ", ".join(
                         f"{k} = :{k}"
                         for k in normalized_doc_updates.keys()
                    )

                    sql = f"""
                         UPDATE documents
                         SET {fields}
                         WHERE doc_hash = :doc_hash
                    """

                    conn.execute(
                         sql,
                         {
                              **normalized_doc_updates,
                              "doc_hash": doc_hash
                         }
                    )


               # -------------------------
               # Update ai_analysis table
               # -------------------------
               if ai_updates:

                    allowed_ai_fields = {
                         "summary",
                         "description",
                         "send_reason",
                         "keywords",
                         "topics",
                         "entities",
                         "document_type",
                         "sentiment",
                         "language",
                         "date_references",
                    }


                    normalized_ai_updates = {
                         key: self.__prepare_db_value(value)
                         for key, value in ai_updates.items()
                         if key in allowed_ai_fields
                    }


                    # Make sure ai_analysis row exists
                    conn.execute(
                         """
                         INSERT OR IGNORE INTO ai_analysis (doc_hash)
                         VALUES (?)
                         """,
                         (doc_hash,)
                    )


                    if normalized_ai_updates:

                         fields = ", ".join(
                              f"{k} = :{k}"
                              for k in normalized_ai_updates.keys()
                         )

                         sql = f"""
                              UPDATE ai_analysis
                              SET {fields}
                              WHERE doc_hash = :doc_hash
                         """

                         conn.execute(
                              sql,
                              {
                              **normalized_ai_updates,
                              "doc_hash": doc_hash
                              }
                         )


               conn.commit()

     #==delte
     def delete_document(self, doc_hash: str) -> None:
          ingest_root = Path(__file__).resolve().parents[2] / "___ingest_file"
          self.delete_document_and_related(
               doc_hash,
               str(ingest_root)
          )


     def delete_document_by_id_or_hash(self, doc_hash: str) -> None:
          self.delete_document_and_related(doc_hash)

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

     def get_documents_summary_list(self) -> list[dict]:
          sql = """
               SELECT
                    d.doc_hash,
                    d.title,
                    d.author,
                    d.time_creation,
                    d.modified_date,
                    d.stored_filename,
                    d.relative_path,
                    d.original_filename,
                    d.mime_type,
                    d.source,
                    d.sender,
                    d.processed_at,
                    d.updated_at,
                    d.email_subject,
                    d.email_date,
                    d.extracted_text,
                    a.document_type,
                    a.summary,
                    a.description
               FROM documents d
               LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
               ORDER BY COALESCE(d.processed_at, d.modified_date, d.time_creation) DESC
          """
          with self.__get_conn() as conn:
               rows = conn.execute(sql).fetchall()

          documents = []
          for row in rows:
               item = dict(row)
               documents.append({
                    "id": item.get("doc_hash", ""),
                    "doc_hash": item.get("doc_hash", ""),
                    "title": item.get("title", ""),
                    "from": item.get("sender") or item.get("author") or "Unknown",
                    "date": (
                         item.get("email_date")
                         or item.get("modified_date")
                         or item.get("time_creation")
                         or item.get("processed_at")
                         or item.get("updated_at")
                         or ""
                    ),
                    "type": item.get("document_type") or item.get("mime_type", ""),
                    "summary": (
                         item.get("summary")
                         or item.get("description")
                         or item.get("extracted_text", "")[:500]
                         or "No summary available."
                    ),
                    "description": item.get("description", ""),
                    "snippet": (
                         item.get("summary")
                         or item.get("description")
                         or item.get("extracted_text", "")[:300]
                         or "No summary available."
                    ),
                    "stored_filename": item.get("stored_filename", ""),
                    "relative_path": item.get("relative_path", ""),
                    "original_filename": item.get("original_filename", ""),
                    "mime_type": item.get("mime_type", ""),
                    "source": item.get("source", ""),
                    "sender": item.get("sender", ""),
                    "email_subject": item.get("email_subject", ""),
                    "email_date": item.get("email_date", ""),
                    "extracted_text": item.get("extracted_text", ""),
               })
          return documents
     
     def search_documents(self, query: str, limit: int = 5) -> list[dict]:
          sql = """
               SELECT
                    d.doc_hash,
                    d.title,
                    d.author,
                    d.original_filename,
                    d.mime_type,
                    d.source,
                    d.sender,
                    d.email_subject,
                    d.email_date,
                    d.time_creation,
                    d.modified_date,
                    d.extracted_text,
                    a.summary,
                    a.description,
                    a.document_type,
                    a.sentiment,
                    a.language
               FROM documents d
               LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
               WHERE
                    COALESCE(d.title, '') LIKE ?
                    OR COALESCE(d.original_filename, '') LIKE ?
                    OR COALESCE(d.sender, '') LIKE ?
                    OR COALESCE(d.email_subject, '') LIKE ?
                    OR COALESCE(d.extracted_text, '') LIKE ?
                    OR COALESCE(a.summary, '') LIKE ?
                    OR COALESCE(a.description, '') LIKE ?
               ORDER BY COALESCE(d.email_date, d.modified_date, d.time_creation) DESC
               LIMIT ?
          """
          like_query = f"%{query}%"
          with self.__get_conn() as conn:
               rows = conn.execute(
                    sql,
                    (like_query, like_query, like_query, like_query, like_query, like_query, like_query, limit),
               ).fetchall()
          return [self.__deserialize_row(row) for row in rows]


     def get_document_details_by_hash(self, doc_hash: str) -> dict | None:
          sql = """
               SELECT
                    d.doc_hash,
                    d.title,
                    d.author,
                    d.time_creation,
                    d.modified_date,
                    d.stored_filename,
                    d.relative_path,
                    d.original_filename,
                    d.mime_type,
                    d.source,
                    d.sender,
                    d.email_subject,
                    d.email_date,
                    d.extracted_text,
                    a.summary,
                    a.description,
                    a.send_reason,
                    a.keywords,
                    a.topics,
                    a.entities,
                    a.document_type,
                    a.sentiment,
                    d.processed_at,
                    d.updated_at,
                    a.language,
                    a.date_references
               FROM documents d
               LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
               WHERE d.doc_hash = ?
               LIMIT 1
          """
          with self.__get_conn() as conn:
               row = conn.execute(sql, (doc_hash,)).fetchone()

          item = self.__deserialize_row(row)
          if not item:
               return None

          return {
               "id": item.get("doc_hash", ""),
               "doc_hash": item.get("doc_hash", ""),
               "title": item.get("title", ""),
               "from": item.get("sender") or item.get("author") or "Unknown",
               "date": (
               item.get("email_date")
                    or item.get("modified_date")
                    or item.get("time_creation")
                    or item.get("processed_at")
                    or item.get("updated_at")
                    or ""
               ),
               "type": item.get("document_type") or item.get("mime_type", ""),
               "summary": (
                    item.get("summary")
                    or item.get("description")
                    or item.get("extracted_text", "")[:500]
                    or "No summary available."
               ),

               "description": item.get("description", ""),
               "snippet": (
                    item.get("summary")
                    or item.get("description")
                    or item.get("extracted_text", "")[:300]
                    or "No summary available."
               ),
               "stored_filename": item.get("stored_filename", ""),
               "relative_path": item.get("relative_path", ""),
               "original_filename": item.get("original_filename", ""),
               "mime_type": item.get("mime_type", ""),
               "source": item.get("source", ""),
               "sender": item.get("sender", ""),
               "email_subject": item.get("email_subject", ""),
               "email_date": item.get("email_date", ""),
               "extracted_text": item.get("extracted_text", ""),
               "keywords": item.get("keywords", []),
               "topics": item.get("topics", []),
               "entities": item.get("entities", []),
               "sentiment": item.get("sentiment", ""),
               "language": item.get("language", ""),
               "date_references": item.get("date_references", []),
          }

     #== Util 
     def mark_processed(self, doc_hash: str) -> None:
          with self.__get_conn() as conn:
               conn.execute(
                    "UPDATE documents SET processed = 1, processed_at = CURRENT_TIMESTAMP WHERE doc_hash = ?",
                    (doc_hash,),
               )
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
                    d.source,
                    d.sender,
                    d.email_subject,
                    d.email_date,
                    d.extracted_text,
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
               ORDER BY COALESCE(d.email_date, d.modified_date, d.time_creation) DESC
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


     
     def search_reports(self, query: str, limit: int = 5) -> list[dict]:
        sql = """
            SELECT
                d.doc_hash,
                d.title,
                d.author,
                d.original_filename,
                d.mime_type,
                d.source,
                d.sender,
                d.email_subject,
                d.email_date,
                d.time_creation,
                d.modified_date,
                d.extracted_text,
                a.summary,
                a.description,
                a.document_type,
                a.sentiment,
                a.language
            FROM documents d
            LEFT JOIN ai_analysis a
                ON d.doc_hash = a.doc_hash
            WHERE
                COALESCE(d.title, '') LIKE ?
                OR COALESCE(d.original_filename, '') LIKE ?
                OR COALESCE(d.sender, '') LIKE ?
                OR COALESCE(d.email_subject, '') LIKE ?
                OR COALESCE(d.extracted_text, '') LIKE ?
                OR COALESCE(a.summary, '') LIKE ?
                OR COALESCE(a.description, '') LIKE ?
            ORDER BY COALESCE(d.email_date, d.modified_date, d.time_creation) DESC
            LIMIT ?
        """
        like_query = f"%{query}%"
        with self.__get_conn() as conn:
            rows = conn.execute(
                sql,
                (
                    like_query,
                    like_query,
                    like_query,
                    like_query,
                    like_query,
                    like_query,
                    like_query,
                    limit,
                ),
            ).fetchall()
            return [self.__deserialize_row(row) for row in rows]
        
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
               "source": "TEXT",
               "sender": "TEXT",
               "email_subject": "TEXT",
               "email_date": "TEXT",
               "extracted_text": "TEXT",
               "processed_at": "TEXT",
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
          source: str | None = None,
          sender: str | None = None,
          email_subject: str | None = None,
          email_date: str | None = None,
          extracted_text: str | None = None,
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
                    mime_type,
                    source,
                    sender,
                    email_subject,
                    email_date,
                    extracted_text
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(doc_hash) DO UPDATE SET
                    title = excluded.title,
                    author = excluded.author,
                    stored_filename = excluded.stored_filename,
                    relative_path = excluded.relative_path,
                    original_filename = excluded.original_filename,
                    mime_type = excluded.mime_type,
                    source = excluded.source,
                    sender = excluded.sender,
                    email_subject = excluded.email_subject,
                    email_date = excluded.email_date,
                    extracted_text = excluded.extracted_text
                    """,
                    (
                    doc_hash,
                    title,
                    author,
                    stored_filename,
                    relative_path,
                    original_filename,
                    mime_type,
                    source,
                    sender,
                    email_subject,
                    email_date,
                    extracted_text,
                    ),
               )
               conn.commit()


     def save_report_history(self, user_id: int, question: str, answer: str, matches: list[dict]) -> int:
          matches_json = json.dumps(matches)
          with self.__get_conn() as conn:
               cursor = conn.execute(
                    """
                    INSERT INTO report_history (user_id, question, answer, matches_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, question, answer, matches_json),
               )
               conn.commit()
               return int(cursor.lastrowid)


     def get_report_history_for_user(self, user_id: int) -> list[dict]:
          with self.__get_conn() as conn:
               rows = conn.execute(
                    """
                    SELECT id, question, answer, matches_json, created_at
                    FROM report_history
                    WHERE user_id = ?
                    ORDER BY created_at DESC, id DESC
                    """,
                    (user_id,),
               ).fetchall()

          history = []
          for row in rows:
               item = dict(row)
               try:
                    item["matches"] = json.loads(item.get("matches_json") or "[]")
               except json.JSONDecodeError:
                    item["matches"] = []
               history.append(item)

          return history
     

     def clear_report_history_for_user(self, user_id: int) -> None:
          with self.__get_conn() as conn:
               try:
                    conn.execute(
                         """
                         DELETE FROM report_history_documents
                         WHERE history_id IN (
                              SELECT id
                              FROM report_history
                              WHERE user_id = ?
                         )
                         """,
                         (user_id,),
                    )
                    print("Deleted from report_history_documents")
               except Exception as exc:
                    print("Failed deleting report_history_documents:", repr(exc))
                    raise

               try:
                    conn.execute(
                         "DELETE FROM report_history WHERE user_id = ?",
                         (user_id,),
                    )
                    print("Deleted from report_history")
               except Exception as exc:
                    print("Failed deleting report_history:", repr(exc))
                    raise

               conn.commit()
     

     def get_report_history_item(self, history_id: int, user_id: int) -> dict | None:
          with self.__get_conn() as conn:
               row = conn.execute(
                    """
                    SELECT id, question, answer, matches_json, created_at
                    FROM report_history
                    WHERE id = ? AND user_id = ?
                    LIMIT 1
                    """,
                    (history_id, user_id),
               ).fetchone()

          if not row:
               return None

          item = dict(row)
          try:
               item["matches"] = json.loads(item.get("matches_json") or "[]")
          except json.JSONDecodeError:
               item["matches"] = []

          return item
     
     def document_exists(self, doc_hash: str) -> bool:
          with self.__get_conn() as conn:
               row = conn.execute(
                    "SELECT 1 FROM documents WHERE doc_hash = ? LIMIT 1",
                    (doc_hash,),
               ).fetchone()
               return row is not None
          
     def get_existing_document_brief(self, doc_hash: str) -> dict | None:
          with self.__get_conn() as conn:
               row = conn.execute(
                    """
                    SELECT doc_hash, title, original_filename, source, processed_at, updated_at
                    FROM documents
                    WHERE doc_hash = ?
                    LIMIT 1
                    """,
                    (doc_hash,),
               ).fetchone()
          return dict(row) if row else None

     def ensure_document_metadata_columns(self) -> None:
          required_columns = {
               "stored_filename": "TEXT",
               "relative_path": "TEXT",
               "original_filename": "TEXT",
               "mime_type": "TEXT",
               "source": "TEXT",
               "sender": "TEXT",
               "email_subject": "TEXT",
               "email_date": "TEXT",
               "extracted_text": "TEXT",
          }

          with self.__get_conn() as conn:
               existing = {
                    row["name"]
                    for row in conn.execute("PRAGMA table_info(documents)").fetchall()
               }

               for column_name, column_type in required_columns.items():
                    if column_name not in existing:
                         conn.execute(f"ALTER TABLE documents ADD COLUMN {column_name} {column_type}")

               conn.commit()

     def delete_document_and_related(self, doc_hash: str, ingest_root: str | None = None) -> dict:
          with self.__get_conn() as conn:
               row = conn.execute(
                    """
                    SELECT doc_hash, relative_path, stored_filename
                    FROM documents
                    WHERE doc_hash = ?
                    LIMIT 1
                    """,
                    (doc_hash,),
               ).fetchone()

               if not row:
                    return {"deleted": False, "message": "Document not found."}

               document = dict(row)

               if ingest_root:
                    relative_path = document.get("relative_path") or document.get("stored_filename") or ""
                    if relative_path:
                         file_path = Path(ingest_root) / relative_path
                         try:
                              if file_path.exists() and file_path.is_file():
                                   file_path.unlink()
                         except Exception as exc:
                              print(f"Failed to delete stored file for {doc_hash}: {exc}")

               for sql in [
                    "DELETE FROM embeddings WHERE doc_hash = ?",
                    "DELETE FROM ai_analysis WHERE doc_hash = ?",
                    "DELETE FROM report_history_documents WHERE doc_hash = ?",
                    "DELETE FROM documents WHERE doc_hash = ?",
               ]:
                    try:
                         conn.execute(sql, (doc_hash,))
                    except Exception as exc:
                         print(f"Delete step skipped for {doc_hash}: {exc}")

               conn.commit()

               return {
                    "deleted": True,
                    "doc_hash": doc_hash,
                    "message": "Document and related data deleted successfully.",
               }
          
     def __prepare_db_value(self, value):
          if isinstance(value, (dict, list)):
               return json.dumps(value)
          return value


     def DEV_drop_db_table(self):
          with self.__get_conn() as conn:
               conn.execute("DROP TABLE IF EXISTS ai_analysis")
               conn.execute("DROP TABLE IF EXISTS documents")
               conn.execute("DROP TABLE IF EXISTS users")
               conn.commit()
         