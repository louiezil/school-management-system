from flask import Flask, session, redirect, url_for, render_template, request
from functools import wraps
from database import conn_cursor, create_tables
from auth import register_teacher, login, student_registration
from actions import (
    get_student,
    get_teacher,
    teacher_students,
    get_teachers,
    get_students,
    permission_grant,
    activation,
    deletion,
    delete_student,
)
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "the_random_secret"

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
except Exception as e:
    print(f"error:{e}")


def Login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "teacher_id" not in session:
            return redirect(url_for("Login"))
        return f(*args, **kwargs)

    return decorated_function


# def owner_required(f):
#     @wraps(f)
#     def owner_decorator(*args, **kwargs):
#         teacher_id = session["teacher_id"]  #'current user'
#         target_id = kwargs.get(
#             "teacher_id",
#         )
#         is_admin = session.get("is_admin", False)
#         if is_admin:
#             return f(*args, **kwargs)
#         elif target_id == teacher_id:
#             return f(*args, **kwargs)
#         else:
#             return "Account Ownership required...", 404

#     return owner_decorator


@app.route("/login", methods=["POST", "GET"])
def Login():
    if "teacher_id" in session:
        return redirect(url_for("dashBoard", teacher_id=session["teacher_id"]))
    error = None
    if request.method == "POST":
        email = request.form["email"]
        if not email:
            error = "Email cant be Empty"
        elif len(email) < 12:
            error = "length of Email too short"
        else:
            password = request.form["password"]
            if not password:
                error = "Password cant be Empty"
            elif len(password) < 5:
                error = "Min length required"
        if not error:
            logged_In = login(cursor, email, password)
            if logged_In:
                session["teacher_id"] = logged_In.teacher_id
                session["name"] = logged_In.name
                session["is_admin"] = logged_In.is_admin
                session["is_active"] = logged_In.is_active
                session["super_user"] = logged_In.super_user

                return redirect(url_for("dashBoard", teacher_id=session["teacher_id"]))
            elif logged_In is False:
                error = "Account De-activated"
            else:
                error = "email or Password Incorrect"

    return render_template("login.html", error=error)


@app.route("/register", methods=["POST", "GET"])
def register():
    if not session:
        return redirect(url_for("Login"))
    if not session.get("is_admin"):
        return "Access Granted Only to Admin", 403
    error = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        age_str = request.form["age"]

        if not name:
            error = "name cant be empty"
        elif len(name) < 3:
            error = "name too short"
        elif not email:
            error = "email cant be Empty"
        elif len(email) < 12:
            error = "email length too short"
        elif not password:
            error = "password cant be Empty"
        elif len(password) < 5:
            error = "password length too short"
        else:
            try:
                age = int(age_str)
                if age < 18:
                    error = "Min Age Required 18+"
            except ValueError as e:
                error = "Age Requires A digit"

        if not error:
            registration = register_teacher(cursor, conn, name, email, age, password)
            if registration:
                return redirect(url_for("Login"))
            error = "Email Already Exist in Data..."
    return render_template("register.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("Login"))


@app.route("/teacher/profile/<int:teacher_id>")
@Login_required
def dashBoard(teacher_id):
    if session.get("is_admin") and teacher_id == session["teacher_id"]:
        return redirect(url_for("admin_dashboard", teacher_id=teacher_id))

    teacher_data = get_teacher(cursor, teacher_id)
    if teacher_data.super_user:
        return "cant view a super User", 403
    if not session.get("is_admin") and (teacher_data.is_admin):
        return "cant View an Admin profile "
    students_disc, total_students = teacher_students(cursor, teacher_id)
    if not teacher_data:
        return "No data Found", 403
    return render_template(
        "dashboard.html",
        profile=teacher_data,
        teacher_students=students_disc,
        total_students=total_students,
    )


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard/students/<int:student_id>")
@Login_required
def student_profile(student_id):
    student_data = get_student(cursor, student_id)
    if not student_data:
        return "No student Found", 404
    if student_data.teacher_id != session["teacher_id"] and not session.get("is_admin"):
        return "Student Not On Your List..."
    # we get the grades later
    return render_template("student.html", name=student_data.name, student=student_data)


@app.route("/dashboard/students/<int:student_id>/update", methods=["POST", "GET"])
@Login_required
def update(student_id):
    error = None
    student = get_student(cursor, student_id)
    if not student:
        return "Not found", 404
    if student.teacher_id != session["teacher_id"] and not session.get("is_admin"):
        return "Not your student", 403

    if request.method == "POST":
        updated_name = request.form["name"]
        level_str = request.form["level"]
        age_str = request.form["age"]
        if (
            not updated_name
        ):  # in case he deletes the prefill and send and empty box here ..hah
            error = "name is empty"
        elif len(updated_name) < 4:
            error = "name is too short"
        else:

            try:
                level = int(level_str)
                if level not in [100, 200, 300, 400]:
                    error = "level input incorrect"
            except Exception as e:
                error = "level must be a digit"

            try:
                age = int(age_str)
                if age < 18:
                    error = "Min Age Required 18+"
            except Exception as e:
                error = "Age must be a digit"
        if error:
            pass
        elif student.teacher_id != session["teacher_id"] and not session.get(
            "is_admin"
        ):
            error = "student not on Your List..."
        else:
            student.name = updated_name
            student.level = level
            student.age = age
            student.update(
                cursor,
                conn,
            )
            return redirect(url_for("student_profile", student_id=student.student_id))

    return render_template(
        "update.html",
        error=error,
        name=student.name,
        level=student.level,
        age=student.age,
    )


@app.route("/dashboard/register_student", methods=["POST", "GET"])
@Login_required
def register_student():
    error = None
    teacher_id = session["teacher_id"]
    teacher_name = session["name"]
    is_active = session["is_active"]

    if request.method == "POST":
        name = request.form["name"]
        level_str = request.form["level"]
        age_str = request.form["age"]
        if not name:  # in case of empty box
            error = "name is empty"
        elif len(name) < 4:
            error = "name is too short"
        else:

            try:
                level = int(level_str)
                if level not in [100, 200, 300, 400]:
                    error = "level input incorrect"
            except Exception as e:
                error = "level must be a digit"

            try:
                age = int(age_str)
                if age < 18:
                    error = "Min Age Required 18+"
            except Exception as e:
                error = "Age must be a digit"
        if not error:
            student_registered = student_registration(
                cursor,
                conn,
                teacher_id,
                name,
                age,
                level,
                created_by=teacher_name,
                is_active=is_active,
            )
            if student_registered:
                return redirect(url_for("dashBoard", teacher_id=teacher_id))
            else:
                error = "Student Already Exist In School Data"
    return render_template("register_student.html", error=error)


@app.route("/delete/student/<int:student_id>", methods=["POST", "GET"])
@Login_required
def delete_stud(student_id):

    student = get_student(cursor, student_id)
    if not student:
        return "No student Found...", 403

    if student.teacher_id == session.get("teacher_id") or session.get("super_user"):

        deleted = delete_student(cursor, conn, student_id)
        if deleted:
            return redirect(url_for("dashBoard", teacher_id=session.get("teacher_id")))
        return "failed Operation On sever...", 404
    else:
        return "Student Ownership required..", 403


# ################################################################################


def admin_required(f):
    @wraps(f)
    def admin_decorator(*args, **kwargs):
        is_admin = session.get("is_admin")
        if not is_admin:
            return "this page requires Admin Access", 404
        return f(*args, **kwargs)

    return admin_decorator


# admin dashboard
# STEP 2: /admin dashboard
# ├── Shows stats (total teachers, total students)
# ├── Links to Teachers / Students
# └── Only admins can access


@app.route("/admin/dashboard/<int:teacher_id>")
@Login_required
@admin_required
def admin_dashboard(teacher_id):
    profile = get_teacher(cursor, teacher_id)
    if not profile:
        return "Profile Not found", 403
    if session.get("teacher_id") != teacher_id:
        return "View Of Other Admin Profile Only by Super_user"
    teachers = get_teachers(cursor, teacher_id)
    students = get_students(cursor)

    return render_template(
        "admin_dashboard.html",
        teachers=teachers,
        students=students,
        profile=profile,
    )


@app.route("/permission/<int:teacher_id>", methods=["POST", "GET"])
@Login_required
@admin_required
def Toggle_permission(teacher_id):
    teacher = get_teacher(cursor, teacher_id)
    if teacher.super_user:
        return "this is a Super_user"
    elif teacher.is_admin and not session.get("super_user"):
        return "Admin Stripping Reserved for Super_user Only", 403
    else:
        granted = permission_grant(cursor, conn, teacher_id)
        if granted:
            return redirect(url_for("dashBoard", teacher_id=teacher_id))
        return "failed Operation on sever..page not Available", 404


@app.route("/activation/<int:teacher_id>", methods=["POST", "GET"])
@Login_required
@admin_required
def activate(teacher_id):
    teacher = get_teacher(cursor, teacher_id)
    if teacher.is_admin:
        return " Admin De-activation is Reserved for a Super_user"
    if teacher.super_user:
        return "this User is a Super User", 403
    activated = activation(cursor, conn, teacher_id)
    if activated:
        return redirect(url_for("dashBoard", teacher_id=teacher_id))
    else:
        return "failed Operation on sever..page not Available", 404


@app.route("/deletion/<int:teacher_id>", methods=["POST", "GET"])
@Login_required
@admin_required
def delete(teacher_id):
    teacher = get_teacher(cursor, teacher_id)

    if teacher.super_user:
        return "this User is a Super User", 403
    if teacher.is_admin:
        return " Admin Deletion is Reserved for a Super_user"
    deleted = deletion(cursor, conn, teacher_id)
    if not deleted:
        return "failed Operation", 404
    else:
        return redirect(url_for("admin_dashboard", teacher_id=session["teacher_id"]))


@app.route("/Update/<int:teacher_id>", methods=["POST", "GET"])
@Login_required
@admin_required
def update_teacher_details(teacher_id):
    if teacher_id == session["teacher_id"]:
        return redirect(url_for("admin_dashboard", teacher_id=session["teacher_id"]))
    error = None
    teacher = get_teacher(cursor, teacher_id)

    if not teacher:
        return "teacher Not found ", 403
    if teacher.super_user:
        return "this User is a Super User", 403
    if teacher.is_admin:
        return "Admin Edition is Reserved for a Super_user"
    if request.method == "POST":
        name = request.form["name"]
        age_str = request.form["age"]

        if not name:
            error = "name is Empty"
        elif len(name) < 4:
            error = " name too short"
        else:
            try:
                age = int(age_str)
                if age < 18:
                    error = "Min Age required 18+"
            except Exception as e:
                error = " Age requires a Digit"
        if not error:
            # updated = update_teacher(cursor,conn,name,age,teacher_id)

            teacher.name = name
            teacher.age = age
            if teacher.update(cursor, conn):
                print(1)
                return redirect(url_for("dashBoard", teacher_id=teacher_id))

    return render_template("teacher_update.html", error=error, teacher=teacher)


if __name__ == "__main__":
    import os

    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(debug=debug)
