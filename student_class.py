# text
# Class: Student

# Attributes:
# ├── name
# ├── age
# ├── level
# ├── teacher_id
# ├── student_id (None for new)
# ├── created_by
# └── date_created (None for new)

# Methods:
# ├── save(cursor, conn)
# │   ├── If student_id is None → INSERT
# │   └── Get the new ID
# └── update(cursor, conn)
#     ├── If student_id exists → UPDATE
#     └── Update name, age, level


class Student:
    def __init__(
        self,
        name,
        age,
        level,
        teacher_id,
        created_by,
        student_id=None,
        date_created=None,
    ):
        self.name = name
        self.age = age
        self.level = level
        self.teacher_id = teacher_id
        self.created_by = created_by
        self.student_id = student_id
        self.date_created = date_created

    # def save(self, cursor, conn):
    #     try:
    #         if not self.student_id:
    #             cursor.execute(
    #                 "INSERT INTO students(name,age,level,teacher_id,created_by)VALUES(?,?,?,?,?)",
    #                 (
    #                     self.name,
    #                     self.age,
    #                     self.level,
    #                     self.teacher_id,
    #                     self.created_by,
    #                 ),
    #             )
    #             conn.commit()
    #             return True
    #     except Exception as e:
    #         print(f"error saving student:{e}")
    #         return False

    def update(self, cursor, conn):
        if not self.student_id:
            return False
        try:
            cursor.execute(
                "UPDATE students SET name =?,age= ?,level=? WHERE id =?",
                (
                    self.name,
                    self.age,
                    self.level,
                    self.student_id,
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"error updating student:{e}")
            return False
