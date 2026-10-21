import sqlite3

class DB:
    """
    Generic python db manager with sqlite3
    
    """
    def __init__(self, name: str, path: str):
        """
        Initializes the DB manager and creates the connection to the sqlite3 db

        ARGS:
            name: name of the database
            path: absolute path to the database (alternatively, you can use "." if your working directory is correct)
        """
        self.name = name
        self.path = path

        self.connect()
        self.connection.row_factory = sqlite3.Row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_traceback):
        print(f"Execution type: {exc_type}")
        print(f"Execution value: {exc_val}")
        print(f"Traceback: {exc_traceback}")
        self.close()

    def connect(self):
        """
        Opens the connection with the database
        """
        try:
            self.connection = sqlite3.connect(f"{self.path}/{self.name}")
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            raise RuntimeError(f"sqlite error opening table: {e}")

    def close(self):
        """
        Closes the connection with the database
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

    def _execute(self, query: str, values: tuple=None) -> sqlite3.Cursor:
        """
        Internal method to execute SQL queries

        ARGS:
            query: a string of the query to be executed
            values: optional argument for if the query has values to accompany it
        """
        try:
            if values is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, values)

            # Commit current transaction
            self.connection.commit()

            return self.cursor

        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"sqlite error executing: {e}")

    def execute_query(self, query: str) -> list[sqlite3.Row]:
        """
        Executes a 'SELECT' query and returns a list of rows

        ARGS:
            query: 'SELECT' query to execute
        """

        response = self._execute(query)
        return response.fetchall()

    def insert_into(self, table: str, values: dict[str, any]) -> int:
        """
        Inserts the record into the given table

        ARGS:
            table: name of the table to be inserted into
            values: dictionary of records to be inserted with
                key: columns
                value: data 
        """
        columns = ", ".join(values.keys())

        data = tuple(values.values())
        placeholders = ", ".join(["?"] * len(data))

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self._execute(query, data)
        return self.cursor.lastrowid

    def delete_from(self, table_name: str, conditions: dict) -> int:
        """
        Deletes the records from the specified table

        ARGS:
            table_name: name of the table to be deleted from
            conditions: a dictionary of conditions used to form the WHERE 
        """
        if not conditions:
            raise ValueError("Conditions cannot be empty for a delete operation to prevent data loss")

        keys = list(conditions.keys())
        values = list(conditions.values())

        where_clause = " AND ".join([f"{k} = ?" for k in keys])

        query = f"DELETE FROM {table_name} WHERE {where_clause}"

        return self._execute(query, values).rowcount

    def create_table(self, table: str, schema_list: list):
        """
        Creates a table in the database

        ARGS:
            table: name of the table to be created
            schema: schema definition 
        """

        schema = ", ".join(schema_list)

        query = f"CREATE TABLE IF NOT EXISTS {table} ({schema})"
        self._execute(query)

def main():
    db = DB("test.db", ".")
    print(db.execute_query("SELECT * FROM tester1"))

    test_data = {
        "Username": "andy",
    }
    test_data2 = {
        "Username": "greg",
    }
    test_data3 = {
        "Username": "samantha",
    }

    db.create_table("tester1", ("ID INTEGER PRIMARY KEY AUTOINCREMENT", " Username TEXT(25)"))
    db.insert_into("tester1", test_data)
    db.insert_into("tester1", test_data2)
    print(db.execute_query("SELECT * FROM tester1"))
    
    db.close()



if __name__ == "__main__":
    main()