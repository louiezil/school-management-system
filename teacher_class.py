class Teacher:
    def __init__(
        self,
        name,
        email,
        password,
        age,
        teacher_id=None,
        is_admin=False,
        super_user =False,
        is_active=True,
        date_created=None,
    ):
        self.name = name
        self.email = email
        self.password = password
        self.age = age
        self.teacher_id = teacher_id
        self.is_admin = is_admin
        self.super_user = super_user
        self.date_created = date_created
        self.is_active = is_active

    def update(self, cursor, conn):
        try:
            cursor.execute(
                "UPDATE teachers SET name = ?,age =? WHERE id = ?",
                (
                    self.name,
                    self.age,
                    self.teacher_id,
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"error updating: {e}")
            return False
