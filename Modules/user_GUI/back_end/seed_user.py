from Modules.engine_injesting.data_base.my_sql_db import SQL_DataBase

db = SQL_DataBase()

if not db.get_user_by_username("admin"):
    db.create_user("admin", "password123")
    print("User created")
else:
    print("User already exists")