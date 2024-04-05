import psycopg2

class DatabaseHandler:
    def __init__(self, dbname, user, host="localhost", port=5432) -> None:
        """
        Initialize the PostgreSQL database
        """
        self.conn = psycopg2.connect (
            dbname=dbname,
            user=user,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()
    
    def fetch_courses(self):
        """
        Fetch course data from the courses database
        """
        self.cursor.execute("SELECT * FROM courses")
        return self.cursor.fetchall()
    
    def fetch_instructors(self):
        """
        Fetch instructor data from the courses database
        """
        self.cursor.execute("SELECT * FROM instructors")
        return self.cursor.fetchall()
    
    def close_connection(self):
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    dbname = "courses"
    user = "postgres"
    host="localhost"
    port=5432

    db_handler = DatabaseHandler(dbname, user, host, port)
    courses = db_handler.fetch_courses()
    print("Courses:")
    for c in courses:
        print(c)
    instructors = db_handler.fetch_instructors()
    print("\nInstructors:")
    for i in instructors:
        print(i)
    db_handler.close_connection()

    
