from Modules.engine_injesting.data_base.my_sql_db import SQL_DataBase

db = SQL_DataBase()

with db._SQL_DataBase__get_conn() as conn:
    conn.execute(
        """
        UPDATE documents
        SET stored_filename = ?,
            relative_path = ?,
            original_filename = ?,
            mime_type = ?
        WHERE doc_hash = ?
        """,
        (
            "temp.pdf",
            "temp.pdf",
            "temp.pdf",
            "application/pdf",
            "62459f256a77c20d109c917547495e84",
        ),
    )
    conn.commit()

    row = conn.execute(
        """
        SELECT doc_hash, title, stored_filename, relative_path, original_filename, mime_type
        FROM documents
        WHERE doc_hash = ?
        """,
        ("62459f256a77c20d109c917547495e84",),
    ).fetchone()

    print(dict(row))