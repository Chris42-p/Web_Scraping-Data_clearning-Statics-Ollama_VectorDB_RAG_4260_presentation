from data_base.my_sql_db import SQL_DataBase

def test_db_object_can_be_created():
    db=SQL_DataBase()
    assert db is not None

#og_doc={'title': '', 'header_footer': '', 'table_content': '', 'author': '', 'time_creation': '', 'modified_date': '', 'file_computer_id': '', 'doc_hash': ''}

#ai_doc={"summary": "Overview of document content", "description": "Detailed description of the content", "send_reason": "Why this communication was sent", "keywords": ["example", "usage"], "topics": ["data", "document"], "entities": [], "document_type": "", "sentiment": "", "language": "", "date_references": []}


#db=SQL_DataBase()
# db.DEV_drop_db_table()

# db.insert_document(og_doc, ai_doc)
# print(db.get_first_document())

