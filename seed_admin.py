from database import conn_cursor, create_tables
from werkzeug.security import generate_password_hash


def fresh_user():
    conn, cursor = conn_cursor()
    create_tables(conn, cursor)

    name = "louie"
    age = 23
    email = f"{name}@gmail.com"
    password = "password"
    is_admin = True
    super_user = True
    hw_password = generate_password_hash(password)
    try:
        cursor.execute(
            "SELECT * FROM teachers WHERE name = ? AND super_user =?",
            (name, super_user),
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO teachers(name,age,email,is_admin,super_user,password)VALUES(?,?,?,?,?,?)",
                (
                    name,
                    age,
                    email,
                    is_admin,
                    super_user,
                    hw_password,
                ),
            )
            conn.commit()
            print("super user created success")
            return True
        print("user Already Exist")
        pass
    except Exception as e:
        print(f"error:{e}")
        return False


if __name__ == "__main__":
    fresh_user()
