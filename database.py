import sqlite3


def conn_cursor():
    try:
        conn = sqlite3.connect("main.db", check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"error creating connection:{e}")
        return None, None


"lets create tables"


def create_tables(conn, cursor):
    try:
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS teachers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT ,
                    email TEXT UNIQUE,
                    age INTEGER,
                    is_admin BOOLEAN DEFAULT 0,
                    super_user BOOLEAN DEFAULT 0,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    password TEXT                     
                        )
                        """)
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT ,
                    age INTEGER,
                    level INTEGER,
                    created_by TEXT,
                    teacher_id INTEGER,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id)                         
                    )                          
                    """)
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS grades(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course TEXT ,
                    grade INTEGER,
                    student_id INTEGER,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE                                                    
                    )
                    """)
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"error creating connection:{e}")
        return False


def close_connection(conn):
    if conn:
        conn.close()
        print("connection closed")
        return True


if __name__ == "__main__":
    conn, cursor = conn_cursor()
    create_tables(conn, cursor)
    print("database Initialized")
