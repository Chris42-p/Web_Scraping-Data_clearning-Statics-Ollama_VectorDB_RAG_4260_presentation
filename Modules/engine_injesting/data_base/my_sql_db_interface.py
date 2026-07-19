# keep all the hardcoded info here to make the code reusable/modular. 


CONST={
#== Meta
     "ERR_CODE":-3,
     "ERR_TXT":"ERR in db: ",


#=== DB 
     "DB_PATH":"4260_BigData_db.db",

     "CREATE_TABLE_SQL":                         #-- Create sql table
"""
CREATE TABLE IF NOT EXISTS documents (
    doc_hash TEXT PRIMARY KEY,
    title TEXT,
    document_bytes BLOB,
    header_footer TEXT,
    table_content TEXT,
    author TEXT,
    time_creation TEXT,
    modified_date TEXT,
    file_computer_id TEXT,
    
    updated_at TEXT,
    processed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ai_analysis (
    doc_hash TEXT PRIMARY KEY,
    summary TEXT,
    description TEXT,
    send_reason TEXT,
    keywords TEXT,
    topics TEXT,
    entities TEXT,
    document_type TEXT,
    sentiment TEXT,
    language TEXT,
    date_references TEXT,
    FOREIGN KEY (doc_hash) REFERENCES documents(doc_hash)
);

CREATE TABLE IF NOT EXISTS users (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     username TEXT UNIQUE NOT NULL,
     password_hash TEXT NOT NULL,
     full_name TEXT,
     email TEXT,
     phone TEXT,
     created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""",

"INSERT_AI_SQL": 
"""
     INSERT INTO ai_analysis
     (doc_hash, summary, description, send_reason, keywords, topics, entities, document_type, sentiment, language, date_references)
     VALUES (:doc_hash, :summary, :description, :send_reason, :keywords, :topics, :entities, :document_type, :sentiment, :language, :date_references)
     ON CONFLICT(doc_hash) DO UPDATE SET
          summary = excluded.summary,
          description = excluded.description,
          send_reason = excluded.send_reason,
          keywords = excluded.keywords,
          topics = excluded.topics,
          entities = excluded.entities,
          document_type = excluded.document_type,
          sentiment = excluded.sentiment,
          language = excluded.language,
          date_references = excluded.date_references
""",

"INSERT_DOCUMENT_SQL": 
"""
     INSERT OR IGNORE INTO documents 
     (doc_hash, title, document_bytes, header_footer, table_content, author, time_creation, modified_date, file_computer_id)
     VALUES (:doc_hash, :title, :document_bytes, :header_footer, :table_content, :author, :time_creation, :modified_date, :file_computer_id)
""",


     "CREATE_TRIGGER_SQL":                        #-- Create SQL trigger to update objs
""" 
CREATE TRIGGER IF NOT EXISTS documents_updated_at
AFTER UPDATE OF title, document_bytes, header_footer, table_content, author,
                time_creation, modified_date, file_computer_id, processed
ON documents
FOR EACH ROW
BEGIN
  UPDATE documents
  SET updated_at = CURRENT_TIMESTAMP
  WHERE doc_hash = NEW.doc_hash;
END;
""",

     "JSON_FIELDS": ["keywords", "topics", "entities", "date_references"],

     "UPDATE_PROCESSED_DOC":
"""
UPDATE documents SET processed =1 WHERE doc_hash 

 
"""
}


