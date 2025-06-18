import json
import sqlite3
from random import sample
from quiz_logic import (
    Admin,
    check_exist,
    db_tables,
    exam_settings,
    fetch_table_details,
    grant_permission,
    take_to_session,
    remove_trash,
    scheduled_subjects,
    store_option,
    table_columns,
    techers_changes,
    get_result,
    conn,
    User
)

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

# from waitress import serve
from my_school import School

# from flask_sqlalchemy import SQLAlchemy
import threading
lock = threading.Lock()
current_school = School()
# mode = "production"
mode = "dev"

app = Flask(__name__)
app.secret_key = "df0c992263c6768f1f49f37f73d2b3b3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users5.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)


@app.route("/try_me", methods=["POST"])
def try_me():
    if request.method == "POST":
        print(request.json)
    return jsonify({"error": "Hello now I am working"})

@app.route("/admin/report_gate", methods=["POST", "GET"])
def report_gate():
    if request.method == "GET":
        session.clear()
        return render_template("report-card-gate.html", classes=current_school.classes)
    else:
        json_data: dict = request.get_json()
        username = json_data.get('username')
        
        get_user = get_result(username)
        session['username'] = username
        if get_user is not None:
            return jsonify({'url': "/admin/my-report"})
        else:
            return jsonify({'none': 'user not found'})

@app.route("/admin/my-report", methods=["POST", "GET"])
def report_card():
    username = session["username"]
    result = get_result(username)
    # print(result)
    if result is not None:
        return render_template(
            "my-report.html",
            result = result,
            user_class = User(username).user_class,
            username = username
        )
    else:
        return "user does not exists"


@app.route("/admin", methods=["POST", "GET"])
def admin():
    general_db = sqlite3.connect("USERS.db")
    curs = general_db.cursor()
    curs.execute("CREATE TABLE IF NOT EXISTS Admin_tab(username TEXT, password TEXT)")
    curs.execute(
        "CREATE TABLE IF NOT EXISTS Admin_permissions(SESSION_ID TEXT, SESSION NUMBER, ENROLLMENT TEXT, UPLOADING_RESULTS TEXT, UPLOADING_ATTENDANCE TEXT)"
    )
    classes = ["PRIMARY_4", "PRIMARY_5", "JSS_1", "JSS_2", "JSS_3"]
    for clas in classes:
        curs.execute(
            f"CREATE TABLE IF NOT EXISTS {clas}_SETTINGS(CLASS TEXT, SUBJECT TEXT, EXAM_TYPE, DURATION NUMBER, NUMBER_OF_QUESTIONS NUMBER, MARK_PER_QUESTION NUMBER)"
        )
    general_db.commit()
    general_db.close()
    if request.method == "GET":
        if "admin" in session:
            return render_template("adminPage.html")
        else:
            return redirect(url_for("loginForm"))


@app.route("/staff", methods=["GET", "POST"])
def staff():
    if request.method == "GET":
        if "teacher" in session:
            # print(session["teacher"])
            username = session["teacher"]
            role_table = check_exist("ROLE_ASSIGNMENT", "USERNAME", username)
            # print(1234)
            teachers_list = role_table[0][1].split()
            teachers_name = teachers_list[0] + " " + teachers_list[1]
            print(role_table)
            return render_template(
                "teachers-page.html",
                role_details=role_table,
                teachers_name=teachers_name,
            )
        else:
            return redirect(url_for("loginForm"))
    else:
        if "scores" in request.form:
            obtained_string = request.form["scores"]
            # print(obtained_string)
            new_list = (
                obtained_string.replace("(", "")
                .replace(")", "")
                .replace("'", "")
                .replace("'", "")
                .split(", ")
            )

            score_table = new_list[1] + "_" + new_list[0] + "_SCORES"
            student_data = fetch_table_details(score_table)
            student_data_columns = table_columns(score_table)
            # print(student_data, "STD DATA PLEASE")
            session["selected_table"] = score_table
            score_table.split("_")[0]

            allowable_column = student_data_columns.index(
                current_school.current_test.upper()
            )
            print(allowable_column, 'I am alllowing you')
            informations = []
            lst:list = [6, 7, 8]
            for information in student_data:
                index = 0
                empt = []
                for info in information:
                    em = []
                    if index in lst:
                        print(index)
                        em.append(info)
                        em.append("yes")
                    else:
                        em.append(info)
                        em.append(index)
                    empt.append(em)
                    index += 1
                informations.append(empt)
            # print(informations)
            return render_template(
                "input-scores.html",
                tables_column=student_data_columns,
                student_list=informations,
            )
        elif "attendance" in request.form:
            obtained_string = request.form["attendance"]
            new_list = (
                obtained_string.replace("(", "")
                .replace(")", "")
                .replace("'", "")
                .replace("'", "")
                .split(", ")
            )

            print(new_list[0])
            table_name = new_list[0] + "_ATTENDANCE"
            # fetch_table_details(table_name)
            student_data = remove_trash(table_name)
            student_data_columns = table_columns(table_name)

            session["selected_table"] = table_name
            table_name.split("_")[0]

            allowable_column = student_data_columns.index("total_attendance")

            informations = []

            # student_data = remove_trash(student_data)
            # print(student_data)
            for information in student_data:
                index = 0
                empt = []
                for info in information:
                    em = []
                    if index == allowable_column:
                        em.append(info)
                        em.append("yes")
                    else:
                        em.append(info)
                        em.append(index)
                    empt.append(em)
                    index += 1
                informations.append(empt)
            # informations = remove_trash(informations)
            print(informations)

            return render_template(
                "input-scores.html",
                student_list=informations,
                tables_column=student_data_columns,
                attend="attendance",
            )


@app.route("/input_scores")
def input_scores():
    return render_template("input-scores.html")


@app.route("/exams_settings", methods=["POST", "GET"])
def exams_settings():
    if "admin" in session:
        if request.method == "POST":
            selected_class = request.form["class"]
            selcted_subject = request.form["subject"]
            number_of_questions = request.form["questNumb"]
            mark_per_question = request.form["questionMark"]
            duration = request.form["duration"]
            exam_type = request.form["testType"]
            print(exam_type, selected_class)

            general_db = sqlite3.connect("USERS.db")
            curs = general_db.cursor()

            initial_obj = curs.execute(
                f"SELECT * FROM {selected_class}_SETTINGS WHERE SUBJECT=?",
                (selcted_subject,),
            )
            initial_state = initial_obj.fetchall()
            if initial_state:
                curs.execute(
                    f"UPDATE {selected_class}_SETTINGS SET DURATION=?, NUMBER_OF_QUESTIONS=?, EXAM_TYPE=?, MARK_PER_QUESTION=? WHERE SUBJECT=?",
                    (
                        duration,
                        number_of_questions,
                        exam_type,
                        mark_per_question,
                        selcted_subject,
                    ),
                )
            else:
                curs.execute(
                    f"INSERT INTO {selected_class}_SETTINGS VALUES(?, ?, ?, ?, ?, ?)",
                    (
                        selected_class,
                        selcted_subject,
                        exam_type,
                        duration,
                        number_of_questions,
                        mark_per_question,
                    ),
                )
            general_db.commit()
            general_db.close()
            return render_template(
                "examsSettings.html",
                success="Changes had been made successfully",
                subjects=current_school.overall_subjects,
                shool_classes=current_school.classes,
                current_test=current_school.current_test,
                school_test=current_school.tests,
            )
        else:
            return render_template(
                "examsSettings.html",
                subjects=current_school.overall_subjects,
                shool_classes=current_school.classes,
                current_test=current_school.current_test,
                school_test=current_school.tests,
            )
    else:
        return redirect(url_for("loginForm"))


@app.route("/assign_role", methods=["POST", "GET"])
def assign_role():
    print("admin" in session)
    if "admin" in session:
        teacher_details = fetch_table_details("TEACHERS_DETAILS")
        # print(teacher_details)
        teachers_names = []

        for detail in teacher_details:
            complete_name = (
                detail[1] + " " + detail[2] + " " + detail[3] + " - " + detail[-2]
            )
            teachers_names.append(complete_name)
        print(teachers_names)
        if request.method == "GET":
            try:
                print("here try")
                role_details = fetch_table_details("ROLE_ASSIGNMENT")
            except sqlite3.OperationalError:
                print("here except")
                return render_template(
                    "role.html",
                    teachers_names=teachers_names,
                    subjects=current_school.overall_subjects,
                    shool_classes=current_school.classes,
                )
            return render_template(
                "role.html",
                teachers_names=teachers_names,
                role_details=role_details,
                subjects=current_school.overall_subjects,
                shool_classes=current_school.classes,
            )
        else:
            teachers_name = request.form["teacherName"]
            role = request.form["roleAssigned"]
            assigned_class = request.form["class"]
            mr_admin = Admin()
            reg_number = teachers_name.split(" ")[-1]
            mr_admin.assign_to(reg_number, teachers_name, role, assigned_class)

            role_details = fetch_table_details("ROLE_ASSIGNMENT")
            return render_template(
                "role.html",
                teachers_names=teachers_names,
                role_details=role_details,
                subjects=current_school.overall_subjects,
                shool_classes=current_school.classes,
            )
    else:
        return redirect(url_for("loginForm"))


@app.route("/handle_role")
def handle_role():
    return


@app.route("/admin/Permissions", methods=["GET"])
def permissions():
    if "admin" in session:
        return render_template("Permissions.html")
    else:
        return redirect(url_for("loginForm"))


@app.route("/handle_permissions", methods=["POST"])
def handle_permissions():
    print(request.form)

    _session = request.form["session"]
    enrollment = request.form["enroll"]
    upload_result = request.form["upload_result"]
    upload_attendance = request.form["upload_attendance"]
    grant_permission(_session, enrollment, upload_result, upload_attendance)
    return jsonify({"success": "Permissions are granted successfully"})


@app.route("/making_query", methods=["POST", "GET"])
def making_query():
    database_table = db_tables()
    # print(database_table)
    if request.method == "POST":
        selected_table = request.form["table"]
        session["selected_table"] = selected_table
        print(selected_table)
        tables_column = table_columns(selected_table)
        print(tables_column)
        return render_template(
            "makingQuery.html",
            database_table=database_table,
            selected_table=selected_table,
            table_columns=tables_column,
            informations=fetch_table_details(selected_table),
        )

    return render_template("makingQuery.html", database_table=database_table)


@app.route("/process_query", methods=["POST"])
def process_query():
    recieved_data = json.loads(request.data.decode("utf-8"))
    changing_list = recieved_data["listData"]
    print(changing_list)
    data_list = []
    for data in changing_list:
        data_list.append(tuple(data))
    print(data_list)
    techers_changes(data_list, session["selected_table"])
    return jsonify({"success": "You have successfully made a change"})


@app.route("/quiz", methods=["POST", "GET"])
def quiz():
    # print(session)
    try:

        username = session["username"]
        Student = User(username=username)
        user_image = Student.user_image
        status = ""
        ongoing_questions = ""
        user_session = ""
        quest_index = 0
        questions = session["questions"]
        # print(questions, 16278282)
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM CBT_SESSION WHERE USERNAME=?", (username,))
            user_session = cursor.fetchone()
            status = user_session[3]
            ongoing_questions = eval(user_session[1])
        except TypeError:
            questions = session["questions"]

        exam_time = 0

        try:
            questions = session["questions"]
        except KeyError:
            return render_template("loginForm.html")

        user_questions = session.get("user_questions")
        # if user_questions is None:
        session["user_questions"] = sample(questions, session["exams_settings"][4])

        for user_question in session["user_questions"]:
            number_of_options = len(user_question[1])
            new_options = sample(user_question[1], number_of_options)
            user_question.remove(user_question[1])
            user_question.insert(1, new_options)

        user_questions = session["user_questions"]
        session["answers"] = []
        answers = session["answers"]
        for question in user_questions:
            answers.append(question[2])

        session.modified = True
        # if "username" in session:
        # not_submitted = "True"
        # session["status"] = [username, not_submitted]
        Student = User(username)

        full_name = (
            Student.first_name + " " + Student.surname + " " + Student.middle_name
        )
        user_class = Student.user_class
        user_class = user_class[:-1] + " " + user_class[-1]
        # print(user_class, "USER CLASS")
        regNo = Student.reg_number
        subject = session["selected_subject"]
        # print('_' in subject)
        if "_" in subject:
            subject = subject.replace("_", " ")

        user_questions = session.get("user_questions")

        if "remaining_questions" not in session:
            remaining_questions = len(user_questions)
        elif "remaining_questions" in session:
            remaining_questions = session["remaining_questions"]

        if remaining_questions > 0:
            remaining_questions = "REMAINING QUESTIONS: " + str(remaining_questions)
        else:
            remaining_questions = "ALL QUESTIONS ANSWERED"
        # print(status, " I am stats")
        if "score" not in session:
            session["score"] = 0
        if status == "ONGOING":
            user_questions = ongoing_questions
            quest_index = user_session[4] - 1
            session["user_questions"] = user_questions
            # selected_answer = user_questions[quest_index][3]
            remaining_questions: int = 0
            exam_time = user_session[2]
            for question in user_questions:
                # print(question)
                if question[3] == None:
                    remaining_questions += 1

            if remaining_questions > 0:
                remaining_questions = "REMAINING QUESTIONS: " + str(remaining_questions)
            else:
                remaining_questions = "ALL QUESTIONS ANSWERED"
            # print(ongoing_questions, "ONGOING QUEST")
        else:
            quest_index = 0
            user_questions = user_questions
            exam_time = session["exams_settings"][3]
            take_to_session(username, user_questions, exam_time, 1, subject)

        index = 0
        shaded_questions = []
        for question in user_questions:
            if question[3] != None:
                shaded_questions.append(index)
            index += 1

        options = user_questions[quest_index][1]
        return render_template(
            "basec.html",
            exam_time=exam_time,
            question=user_questions[quest_index][0],
            quest_inst=user_questions[quest_index][-1],
            name=full_name,
            regNo=regNo,
            subject=subject,
            remaining_questions=remaining_questions,
            user_questions=user_questions,
            username=username,
            number_of_quest=len(user_questions),
            options=options,
            answer=user_questions[quest_index][2],
            quest_number=quest_index + 1,
            number_of_questions=len(user_questions),
            user_class=user_class.upper(),
            selected_option=user_questions[quest_index][3],
            user_image=user_image,
            shaded_questions=shaded_questions,
            index=len(options),
            option_tools="1234",
            string=str,
            option_boxes=["A", "B", "C", "D", "E", "F", "G"],
            len=len,
        )
    except KeyError:
        return redirect(url_for("loginForm"))


@app.route("/random_navigation")
def random_navigation():
    return jsonify({"user_questions": session["user_questions"]})


@app.route("/cbt_session", methods=["POST"])
def cbt_session():
    cursor = conn.cursor()
    if request.method == "POST":
        print(request.form)
        captured_time = request.form["leave_time"]
        username = request.form["username"]
        print(session)
        captured_time = captured_time.split(":")
        session_time = int(captured_time[0]) + int(captured_time[1]) / 60
        try:
            lock.acquire(True)
            cursor.execute(
                f"UPDATE CBT_SESSION SET USER_TIME=? WHERE USERNAME=?",
                (session_time, username),
            )
            conn.commit()
        finally:
            lock.release()

        return ("", 204)


@app.route("/navigation", methods=["GET", "POST"])
def load_questions():
    user_questions = session.get("user_questions")

    if "score" and "answers" not in session:
        session["score"] = 0
        session["answers"] = []

    if request.method == "POST":
        # print(request.get_json())
        quest_index = request.get_json().get("quest_index")
        current_btn = request.get_json().get("currentBtn")

        # next_index = quest_index
        next_index = (
            quest_index + 1
            if current_btn == "Next"
            else quest_index - 1 if current_btn == "Previous" else int(current_btn) - 1
        )

        next_question = user_questions[next_index]
        show_selected = next_question[3]
        session.modified = True
        #####################################################################################
        if next_index < len(user_questions):
            new_question = user_questions[next_index]
            return jsonify(
                {
                    "question": new_question,
                    "show_selected": show_selected,
                    "number_of_quest": len(user_questions),
                }
            )
        else:
            return jsonify({"message": "End of question"})


@app.route("/remaining_questions", methods=["GET"])
def rem_quest():
    user_questions = session.get("user_questions")
    selected_opt = request.args.get("selected_opt")
    quest_index = int(request.args.get("question_index"))
    captured_time = request.args.get("captured_time").split(":")
    # print(captured_time, "Hi I am captured time")
    current_question = user_questions[quest_index]

    store_option(current_question, selected_opt)

    total_time = int(captured_time[0]) + int(captured_time[1]) / 60
    # print(total_time)
    take_to_session(
        session["username"],
        user_questions,
        total_time,
        quest_index + 1,
        session["selected_subject"],
    )
    session.modified = True
    print('hello world')
    
    

    remaining_questions: int = 0
    for question in user_questions:
        if question[3] == None:
            remaining_questions += 1
    session["remaining_questions"] = remaining_questions

    if request.method == "GET":
        request.args.get("rem_quest")
        return jsonify(
            {
                "alert": "Remaining questions recieved successflly!",
                "remQuest": remaining_questions,
            }
        )


@app.route("/submit", methods=["POST"])
def submit():
    confirm = (
        "Are you sure you want to submit? Once you submitted you cannot come back again"
    )
    remaining_questions = len(session["user_questions"])
    if "remaining_questions" in session:
        remaining_questions = session["remaining_questions"]
    if remaining_questions > 0:
        confirm = f"Are you sure you want to submit? You still have {remaining_questions} questions remaining. Once you submitted you cannot come back again"
    if remaining_questions == 1:
        confirm = f"Are you sure you want to submit? You have only {remaining_questions} question left. Once you submitted you cannot come back again"
    return jsonify({"confirm": confirm})


@app.route("/ok_submit", methods=["POST"])
def ok_submit():
    cursor = conn.cursor()
    Student = User(session["username"])
    Student.save_score(session["selected_subject"], session["user_questions"])

    try:
        lock.acquire(True)
        cursor.execute(
            "UPDATE CBT_SESSION SET USER_QUESTIONS=?, STATUS=? WHERE USERNAME=?",
            (str(session["user_questions"]), "SUBMITTED", session["username"]),
        )
        conn.commit()
    finally:
        lock.release()

    return redirect(url_for("loginForm"))

@app.route("/timer_finished", methods=["POST"])
def timer_finished():
    cursor = conn.cursor()
    Student = User(session["username"])
    Student.save_score(session["selected_subject"], session["user_questions"])
    try:
        lock.acquire(True)
        cursor.execute(
            "UPDATE CBT_SESSION SET USER_QUESTIONS=?, STATUS=? WHERE USERNAME=?",
            (str(session["user_questions"]), "SUBMITTED", session["username"]),
        )
        conn.commit()
    finally:
        lock.release()

    session.clear()

    return jsonify({"notification": "Time has stopped successfully!"})

@app.route("/", methods=["GET", "POST"])
def loginForm():
    if request.method == "GET":
        if session:
            session.clear()
        # print(scheduled_subjects())
        return render_template("loginForm.html", subject_list=scheduled_subjects())

@app.route("/handle_login", methods=["POST", "GET"])
def handle_login():
    if request.method == "POST":

        username = request.form["username"].upper()
        password = request.form["password"].upper()
        subject = request.form["subject"]
        session["selected_subject"] = subject
        session["username"] = username
        # print(username)
        if username.lower() == "admin" and password.lower() == "admin":
            session["admin"] = username
            # print("yes I am admin")
            return jsonify({"message": "admin"})
        if username.lower() == "admin@gmail.com" and password.lower() != "admin":
            return jsonify({"error": "Incorrect password"})

        try:
            New_user = User(username)
        except TypeError:
            return jsonify({"error": "User does not exists."})

        if New_user.is_registered():
            if New_user.check_user_type() == "STUDENT":
                if New_user.check_password(password) == "CORRECT":
                    if New_user.verify_subject(subject):
                        if New_user.cheched_written(subject):
                            open_subject = (
                                subject.lower()
                                + "_"
                                + New_user.user_class.lower()
                                + ".json"
                            )
                            # open_subject = subject.lower() + "_" + New_user.user_class.lower() + "_exam" + '.json'
                            with open(open_subject, encoding="utf-8") as f_obj:
                                questions_dict = json.load(f_obj)
                                questions = questions_dict["banks"]
                                questions = questions[:20]
                                # print(len(questions), "under login")

                                for question in questions:
                                    question.append(None)

                                    if len(question) == 4:
                                        question.append("")

                                session["questions"] = questions
                                session["exams_settings"] = exam_settings(
                                    username, subject
                                )
                                return jsonify({"quiz": "quiz"})
                        else:
                            return jsonify(
                                {"error": "You have already taken this test/exam"}
                            )
                    else:
                        return jsonify({"error": "No scheduled for this subject"})
                else:
                    return jsonify({"error": "Incorrect password"})
            else:
                session["teacher"] = New_user.username
                return jsonify({"staff": "staff"})
        else:
            return jsonify(
                {
                    "error": "Sorry you have not registered or make sure your username is correct"
                }
            )

@app.route("/register")
def registrationForm():
    # print(fetch_table_details("Admin_permissions"))
    if fetch_table_details("Admin_permissions")[0][2] == "allow":
        return render_template("registrationForm.html")
    else:
        return redirect(url_for("loginForm"))

@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    if request.method == "GET":
        print("Yes sirrrr")
        return render_template("imageUpload.html")

    if request.method == "POST":
        try:
            username = request.form["username"]
            New_user = User(username=username)

            if New_user.is_registered() is True:
                encoded_image = New_user.upload_image()

                return render_template(
                    "imageUpload.html",
                    image=encoded_image,
                    success="Image uploaded successfully",
                )
            else:
                return render_template("imageUpload.html", error="Incorrect username")
        except TypeError:
            return render_template("imageUpload.html", error="Incorrect username")

@app.route("/process_registeration", methods=["POST"])
def process_registeration():
    if request.method == "POST":
        first_name = request.form["firstName"]
        surname = request.form["surname"]
        middle_name = request.form["middleName"]
        collected_user_class = request.form["classes"].upper()
        user_class = collected_user_class
        gender = request.form["gender"]
        dob = request.form["dob"]
        reg_number = request.form["regNo"]
        create_password = request.form["createpassword"]
        confirm_password = request.form["confirmpassword"]
        user_type = request.form["userType"].upper()

        # new_user = Student('Abdullahi')
        # db.session.add(new_user)
        # return {"hi": "jkl"}
        # db.commit()
        # register_user(first_name, surname, middle_name, collected_user_class, gender, dob, reg_number, create_password, confirm_password, user_type)
        reg_number = str(reg_number)
        if len(reg_number) == 2:
            reg_number = "0" + reg_number
        elif len(reg_number) == 1:
            reg_number = "00" + reg_number

        initial_year = 2024 - int(collected_user_class[-1]) + 1
        username = (
            collected_user_class[0]
            + user_type[0]
            + str(initial_year)[-2:]
            + str(reg_number)
        )

        # print(user_class)
        image_upload = ""

        user_score = ""
        "Yes sirrrr"
        gen_connect = sqlite3.connect("USERS.db")
        gen_cursor = gen_connect.cursor()

        gen_cursor.execute(
            """CREATE TABLE IF NOT EXISTS USERS(
            id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, gender TEXT, dob TEXT, img_upload BLOB, user_type TEXT, user_class TEXT, reg_number TEXT, username TEXT, user_Password TEXT)"""
        )
        # gen_cursor.executescript()
        fetch_reg_numbers = gen_cursor.execute(
            "SELECT * FROM USERS WHERE username=?", (username,)
        )
        fetch_reg_numbers = fetch_reg_numbers.fetchone()
        if create_password == confirm_password and fetch_reg_numbers == None:
            # print(reg_number+"I am reg number")
            if user_type == "STUDENT" and reg_number != "":

                gen_cursor.execute(
                    f"""CREATE TABLE IF NOT EXISTS {user_class}_DETAILS(
                                    id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, gender TEXT, dob TEXT, img_upload BLOB, user_type TEXT, user_class TEXT, reg_number TEXT, username TEXT, user_Password TEXT)"""
                )
                print(user_class)
                gen_cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {user_class}_ATTENDANCE(id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, reg_number TEXT, total_attendance NUMBER, number_of_times_present NUMBER, number_of_times_absent NUMBER, form_teacher_comment TEXTT)"
                )

                junior_subjects = current_school.junior_subjects

                primary_subjects = current_school.primary_subjects

                offered_subjects = ""
                if collected_user_class[0].upper() == "J":
                    offered_subjects = junior_subjects
                else:
                    offered_subjects = primary_subjects

                for subject in offered_subjects:
                    table_name = (
                        subject.upper() + "_" + collected_user_class.upper() + "_SCORES"
                    )

                    gen_cursor.execute(
                        f"CREATE TABLE IF NOT EXISTS {table_name}(id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, reg_number TEXT, username TEXT, FIRST_CA NUMBER, SECOND_CA NUMBER, EXAM NUMBER, PPT NUMBER, TOTAL NUMBER)"
                    )

                    gen_cursor.execute(
                        f"INSERT INTO {table_name} (first_name, surname, middle_name, reg_number, username, FIRST_CA, SECOND_CA, EXAM, PPT, TOTAL) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            first_name.upper(),
                            surname.upper(),
                            middle_name.upper(),
                            reg_number,
                            username,
                            user_score,
                            user_score,
                            user_score,
                            user_score,
                            user_score,
                        ),
                    )

                gen_cursor.execute(
                    "INSERT INTO USERS (first_name, surname, middle_name, gender, dob, img_upload, user_type, user_class, reg_number, username, user_Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        first_name.upper(),
                        surname.upper(),
                        middle_name.upper(),
                        gender.upper(),
                        dob,
                        image_upload,
                        user_type,
                        user_class.upper(),
                        reg_number,
                        username,
                        create_password,
                    ),
                )
                gen_cursor.execute(
                    f"INSERT INTO {user_class.upper()}_DETAILS (first_name, surname, middle_name, gender, dob, img_upload, user_type, user_class, reg_number, username, user_Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        first_name.upper(),
                        surname.upper(),
                        middle_name.upper(),
                        gender.upper(),
                        dob,
                        image_upload,
                        user_type,
                        user_class.upper(),
                        reg_number,
                        username,
                        create_password,
                    ),
                )

                gen_cursor.execute(
                    f"INSERT INTO {user_class.upper()}_ATTENDANCE (first_name, surname, middle_name, reg_number) VALUES(?, ?, ?, ?)",
                    (
                        first_name.upper(),
                        surname.upper(),
                        middle_name.upper(),
                        reg_number,
                    ),
                )

                gen_connect.commit()
                gen_connect.close()
                # Student = User(username)
                # register_student(first_name, surname, middle_name, collected_user_class, gender, dob, reg_number, create_password, confirm_password, user_type)
                return jsonify(
                    {
                        "success": f"Dear {first_name} {surname} {middle_name}, you have registered successfully. Your username is {username}"
                    }
                )
            elif user_type == "TEACHER":
                try:
                    teachers_list = gen_cursor.execute(
                        f"SELECT * FROM USERS WHERE user_type = ?", (user_type,)
                    )
                    teachers_list = teachers_list.fetchall()
                    print(teachers_list)
                    username = (
                        collected_user_class[0]
                        + user_type[0]
                        + "00"
                        + str(len(teachers_list) + 1)
                    )

                except sqlite3.OperationalError:
                    username = collected_user_class[0] + user_type[0] + "001"

                gen_cursor.execute(
                    f"INSERT INTO USERS (first_name, surname, middle_name, gender, dob, img_upload,user_type, user_class, username, user_Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        first_name.upper(),
                        surname.upper(),
                        middle_name.upper(),
                        gender.upper(),
                        dob,
                        image_upload,
                        user_type,
                        user_class.upper(),
                        username,
                        create_password,
                    ),
                )
                gen_cursor.execute(
                    f"""CREATE TABLE IF NOT EXISTS TEACHERS_DETAILS(
                                    id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, gender TEXT, dob TEXT, user_type TEXT, user_class TEXT, username TEXT, user_Password TEXT)"""
                )
                gen_cursor.execute(
                    f"INSERT INTO TEACHERS_DETAILS (first_name, surname, middle_name, gender, dob, user_type, user_class, username, user_Password) VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        first_name.upper(),
                        surname.upper(),
                        middle_name.upper(),
                        gender.upper(),
                        dob,
                        user_type,
                        user_class.upper(),
                        username,
                        create_password,
                    ),
                )
                gen_connect.commit()
                gen_connect.close()
                return jsonify(
                    {
                        "success": f"Dear {first_name.upper()} {surname.upper()} {middle_name.upper()}, you have registered successfully. Your username is {username}"
                    }
                )
            else:
                return jsonify({"error": "Ensure you fill all the required fields!"})
        elif create_password != confirm_password:
            error = "Create password is not thesame as confirm password"
            return jsonify({"error": error})
        elif fetch_reg_numbers is not None:
            error = "User with register number already exists in the class"
            return jsonify({"error": error})

if __name__ == "__main__":
    if mode == "dev":
        app.run(host="0.0.0.0", port=80, debug=True)
    # elif mode == "production":
    #     serve(app,
    #           host='0.0.0.0',
    #           port=80,
    #           threads=5
    #           )
