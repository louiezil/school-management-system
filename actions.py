from teacher_class import Teacher
from student_class import Student


def get_teacher(cursor, teacher_id):
    try:
        cursor.execute("SELECT * FROM teachers WHERE id = ?", (teacher_id,))
        data = cursor.fetchone()
        if not data:
            return None
        teacher_data = Teacher(
            name=data[1],
            email=data[2],
            password=data[8],
            age=data[3],
            teacher_id=data[0],
            is_admin=data[4],
            super_user=data[5],
            date_created=data[6],
            is_active=data[7]
        ) 
        return teacher_data
    except Exception as e:
        print(f"error getting teacher:{e}")
        return None


def teacher_students(cursor, teacher_id):
    try:
        cursor.execute(
            "SELECT * FROM students WHERE teacher_id = ?", (teacher_id,)
        )  # lets pull all his students
        teacher_students = cursor.fetchall()
        students_dic = {}
        if teacher_students:
            for (
                student_id,
                name,
                age,
                level,
                created_by,
                teacher_id,
                created_at,
            ) in teacher_students:
                students_dic[name] = {
                    "id": student_id,
                    "age": age,
                    "level": level,
                    "created_by": created_by,
                    "created_at": created_at,
                }  # for ease in than in tuple 01234
        total_students = len(students_dic)
        return students_dic, total_students
    except Exception as e:
        print(f"error fetching students:{e}")
        return None, None


def get_student(cursor, student_id):
    try:
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        data = cursor.fetchone()
        student = Student(
            name=data[1],
            age=data[2],
            level=data[3],
            teacher_id=data[5],
            created_by=data[4],
            student_id=data[0],
            date_created=data[6],
        )
        return student
    except Exception as e:
        print(f"error fetching name : {e}")
        return None


def get_teachers(cursor, excluded_id):
    try:
        cursor.execute("SELECT * FROM teachers ")
        data = cursor.fetchall()
        teachers_disc = {}
        for (
            teacher_id,
            name,
            email,
            age,
            is_admin,
            super_user,
            date_created,
            is_active,
            password,
        ) in data:
            if excluded_id == teacher_id:  # only admin get this function
                continue
            teachers_disc[name] = {
                "id": teacher_id,
                "age": age,
                "email": email,
                "is_admin": is_admin,
                'super_user':super_user,
                "is_active": is_active,
                "date_created": date_created,
                # "password": None,
            }
        return teachers_disc
    except Exception as e:
        print(f"error fetching all teachers:{e}")
        return None


def get_students(cursor):
    try:
        cursor.execute("SELECT * FROM students")
        data = cursor.fetchall()
        students_disc = {}
        for (
            student_id,
            name,
            age,
            level,
            created_by,
            teacher_id,
            date_created,
        ) in data:
            students_disc[student_id] = {
                "name": name,
                "age": age,
                "level": level,
                "created_by": created_by,
                "teacher_id": teacher_id,
                "date_created": date_created,
            }
        return students_disc
    except Exception as e:
        print(f"error all students:{e} ")
        return None


def permission_grant(cursor, conn, teacher_id):
    try:
        cursor.execute("SELECT is_admin FROM teachers WHERE id =?", (teacher_id,))
        is_admin = cursor.fetchone()
        if is_admin[0] :
            cursor.execute(
                "UPDATE teachers SET is_admin = ? WHERE id = ?",
                (
                    False,
                    teacher_id,
                ),
            )
            conn.commit()
            return True
        else:
            cursor.execute(
                "UPDATE teachers SET is_admin = ? WHERE id = ?",
                (
                    True,
                    teacher_id,
                ),
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"error with permission change:{e}")
        return False


def activation(cursor, conn, teacher_id):
    try:
        cursor.execute("SELECT is_active FROM teachers WHERE id = ?", (teacher_id,))
        is_active = cursor.fetchone()
        print(is_active[0])
        if is_active[0] == 1:
            cursor.execute(
                "UPDATE teachers SET is_active = ? WHERE id =?",
                (
                    False,
                    teacher_id,
                ),
            )
            conn.commit()
            return True
        else:
            cursor.execute(
                "UPDATE teachers SET is_active = ? WHERE id =?",
                (
                    True,
                    teacher_id,
                ),
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"error with Activation : {e}")
        return False


def deletion(cursor, conn, teacher_id):
    try:
        cursor.execute("DELETE FROM teachers WHERE id = ? ", (teacher_id,))
        conn.commit()
        return True

    except Exception as e:
        print(f"error with delete: {e}")
        return False


# def update_teacher(cursor, conn, name, age, teacher_id):
#     cursor.execute(
#         "UPDATE teachers SET name =?,age = ? WHERE id =?",
#         (
#             name,
#             age,
#             teacher_id,
#         ),
#     )


def delete_student(cursor, conn, student_id):
    try:
        cursor.execute("DELETE FROM students WHERE id = ? ", (student_id,))
        conn.commit()
        print("del success")
        return True

    except Exception as e:
        print(f"error with delete: {e}")
        return False
