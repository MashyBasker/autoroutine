import sqlite3

# Function to connect to the database
def connect_to_database(database_name='timetable.db'):
    return sqlite3.connect(database_name)

# Function to create tables
def create_tables(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
             id INTEGER PRIMARY KEY,
             name TEXT,
             duration INTEGER,
             instructor_id INTEGER,
             room_number TEXT,
             constraints TEXT,
             FOREIGN KEY (instructor_id) REFERENCES instructors(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS instructors (
                 id INTEGER PRIMARY KEY,
                 name TEXT,
                 time_preference TEXT)''')
    conn.commit()

# Function to insert sample data into courses table
def insert_courses_data(conn, courses_data):
    c = conn.cursor()
    c.executemany('INSERT INTO courses (id, name, duration, instructor_id, room_number, constraints) VALUES (?, ?, ?, ?, ?, ?)', courses_data)
    conn.commit()

# Function to insert sample data into instructors table
def insert_instructors_data(conn, instructors_data):
    c = conn.cursor()
    c.executemany('INSERT INTO instructors (id, name, time_preference) VALUES (?, ?, ?)', instructors_data)
    conn.commit()

# Function to retrieve all courses with instructors from the database
def get_all_courses_with_instructors(conn):
    c = conn.cursor()
    c.execute('''SELECT courses.id, courses.name, courses.duration, instructors.name AS instructor, courses.room_number, courses.constraints 
                 FROM courses
                 JOIN instructors ON courses.instructor_id = instructors.id''')
    return c.fetchall()


def get_all_instructors(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM instructors")
    return c.fetchall()


def insert_course_data(course_name, instructor_name, room_number):
    """Insert course data into the database."""
    conn = connect_to_database()
    cursor = conn.cursor()

    # Check if the instructor exists in the database
    cursor.execute("SELECT id FROM instructors WHERE name=?", (instructor_name,))
    result = cursor.fetchone()
    if result:
        instructor_id = result[0]
    else:
        # Insert the new instructor into the database
        cursor.execute("INSERT INTO instructors (name) VALUES (?)", (instructor_name,))
        instructor_id = cursor.lastrowid

    # Insert course data
    cursor.execute("INSERT INTO courses (name, instructor_id, room_number) VALUES (?, ?, ?)",
                   (course_name, instructor_id, room_number))

    conn.commit()
    conn.close()

