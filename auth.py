from werkzeug.security import generate_password_hash, check_password_hash
from teacher_class import Teacher


def register_teacher(cursor, conn, name, email, age, password):
    try:
        cursor.execute(
            "SELECT * FROM teachers WHERE  email =?",
            (email,),
        )
        if cursor.fetchone():
            print(f"{email} Already Exist in Data....")
            return False  # email exist in data...
        hw_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO teachers(name,password,age,email)VALUES(?,?,?,?)",
            (
                name,
                hw_password,
                age,
                email,
            ),
        )
        conn.commit()
        print(f"{name} saved Into data")
        return True
    except Exception as e:
        print(f"error in register:{e}")
        return False


def login(cursor, email, plain_password):
    try:
        cursor.execute("SELECT * FROM teachers WHERE email = ?", (email,))
        data = cursor.fetchone()
        if not data:
            return None
        (
            teacher_id,
            name,
            email,
            age,
            is_admin,
            super_user,
            date_created,
            is_active,
            password,
        ) = data

        hw_password = password
        check_password = check_password_hash(hw_password, plain_password)
        if not check_password:
            print("incorrect password")
            return None
        if not is_active:
            print("Account De-activated...Contact Hr")
            return False

        teacher = Teacher(
            name=name,
            email=email,
            age=age,
            super_user=super_user,
            teacher_id=teacher_id,
            is_admin=is_admin,
            is_active=is_active,
            date_created=date_created,
            password="",
        )
        return teacher
    except Exception as e:
        print(f"error at Login:{e}")
        return None


# register student


def student_registration(
    cursor, conn, teacher_id, name, age, level, created_by, is_active
):
    cursor.execute(
        "SELECT * FROM students WHERE name = ? AND age =?",
        (
            name,
            age,
        ),
    )
    if cursor.fetchone():
        return False

    try:
        cursor.execute(
            "INSERT INTO students(name,age,level,teacher_id,created_by)VALUES(?,?,?,?,?)",
            (
                name,
                age,
                level,
                teacher_id,
                created_by,
            ),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"error on student registration:{e}")
        return False
