import base64
from flask import session, request
import json
from functools import reduce
import sqlite3
from threading import Lock
from typing import List, Tuple, Any
import pathlib
from my_school import School

lock = Lock()

# from image_resize import image
conn = sqlite3.connect("USERS.db", check_same_thread=False)
# verify_subject


def user_details(username: str) -> Tuple:
    try:
        lock.acquire(True)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE username=?", (username,))
    finally:
        lock.release()

    reg_details = cursor.fetchone()
    return reg_details


def get_user_image(username: str) -> str:
    path = pathlib.Path(f"user resized images\{username}.jpg")
    # check if path exists
    if path.exists() == True:
        return path
    # return image


def take_to_session(
    username: str,
    user_questions: List,
    user_time: int,
    current_number: int,
    current_subject: str,
) -> str:
    try:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS CBT_SESSION(USERNAME TEXT, USER_QUESTIONS TEXT, USER_TIME INTEGER, STATUS TEXT, CURRENT_NUMBER INTEGER, CURRENT_SUBJECT TEXT)"
        )
    finally:
        lock.release()
    # exist = None
    # print(user_questions)
    user_dict = str(user_questions)
    # print(user_dict)
    # try:
    try:
        lock.acquire(True)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CBT_SESSION WHERE USERNAME=?", (username,))
        user_fetch = cursor.fetchall()
    finally:
        lock.release()
    current = "ONGOING"

    try:
        lock.acquire(True)
        cursor = conn.cursor()
        if len(user_fetch):
            cursor.execute(
                "UPDATE CBT_SESSION SET USER_QUESTIONS=?, STATUS=?, USER_TIME=?, CURRENT_NUMBER=?, CURRENT_SUBJECT=? WHERE USERNAME=?",
                (
                    user_dict,
                    current,
                    user_time,
                    current_number,
                    current_subject,
                    username,
                ),
            )
        else:
            cursor.execute(
                "INSERT INTO CBT_SESSION (USERNAME , USER_QUESTIONS , USER_TIME, STATUS, CURRENT_NUMBER, CURRENT_SUBJECT) VALUES(?, ?, ?, ?, ?, ?)",
                (
                    username,
                    user_dict,
                    user_time,
                    current,
                    current_number,
                    current_subject,
                ),
            )
        # print(len(user_fetch))

        conn.commit()
    finally:
        lock.release()

    return "session committed successfully!!!"


# get_user_image("PS21004")
def exam_settings(username: str, selected_subject: str) -> Tuple:
    username = username.upper()
    cursor = conn.cursor()
    cursor.execute("SELECT user_class from USERS WHERE username=?", (username,))
    user_class = cursor.fetchone()[0]
    setting_table = user_class + "_SETTINGS"

    cursor.execute(
        f"SELECT * FROM {setting_table} WHERE SUBJECT=?", (selected_subject,)
    )
    collected_subject = cursor.fetchone()
    return collected_subject


def check_query(username: str) -> Tuple:
    cursor = conn.cursor()
    if username != "":
        initial_obj = cursor.execute(
            "SELECT * FROM USERS WHERE username=?", (username,)
        )
    else:
        initial_obj = cursor.execute("SELECT * FROM USERS")

    initial_state = initial_obj.fetchall()
    return initial_state


def query_information(table_name: str) -> Tuple:
    try:
        lock.acquire(True)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        informations = cursor.fetchall()
    finally:
        lock.release()

    return informations


def db_tables() -> List:
    empt_list = []
    try:
        lock.acquire(True)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
    finally:
        lock.release()

    for table in tables:
        # empt_list2.append(table[0])
        if "_" in table[0]:
            edit_name = table[0].replace("_", " ")
            empt_list.append(edit_name)
        else:
            empt_list.append(table[0])

    return empt_list


# table_name: str, column_name: str, target_column: str
def techers_changes(new_list: List, table_name: str) -> bool:
    # my_list = []
    cursor = conn.cursor()
    try:
        for detail in new_list:
            target_column = detail[-1].strip().replace(" ", "_")
            # print(target_column)

            column_name = detail[1].strip().replace(" ", "_")
            # print(column_name)
            cursor.execute(
                f"UPDATE {table_name} SET {column_name}=? WHERE {target_column}=?",
                (detail[0], detail[2]),
            )
        conn.commit()
        print("WELDONE")
    except IndexError:
        print("No data inputed!!")
        pass


# new_list = [('STUDENT', 'USER TYPE ', 2, '2', 'ID '), ('STUDENT', 'USER TYPE ', 3, '3', 'ID ')]
# techers_changes(new_list, "USERS")


def grant_permission(
    _session: str, enrollment: str, upload_result: str, upload_attendance: str
) -> str:
    cursor = conn.cursor()
    if fetch_table_details("Admin_permissions") == []:
        cursor.execute(
            "INSERT INTO Admin_permissions (SESSION_ID, SESSION, ENROLLMENT, UPLOADING_RESULTS, UPLOADING_ATTENDANCE) VALUES(?, ?, ?, ?, ?)",
            (00, _session, enrollment, upload_result, upload_attendance),
        )
        conn.commit()
    else:
        session_id = fetch_table_details("Admin_permissions")[0][0]
        cursor.execute(
            "UPDATE Admin_permissions SET SESSION=?, ENROLLMENT=?, UPLOADING_RESULTS=?, UPLOADING_ATTENDANCE=? WHERE SESSION_ID=?",
            (_session, enrollment, upload_result, upload_attendance, session_id),
        )
        conn.commit()

    return "PERMISSION DONE"


def fetch_table_details(tabel_name: str):
    cursor = conn.cursor()
    lock.acquire(True)
    cursor.execute(f"SELECT * FROM {tabel_name}")
    lock.release()
    return cursor.fetchall()


non_editable = []


def moderate_scores(
    value: int, subject: str, class_name: str, test_type: str, username: str = "*"
):
    cursor = conn.cursor()
    subject_table = f"{subject}_{class_name}_SCORES".upper()
    tobe_moderate = []
    max_value = 0
    if username == "*":
        cursor.execute(f"SELECT USERNAME, {test_type} FROM {subject_table}")
        tobe_moderate = cursor.fetchall()
    else:
        cursor.execute(
            f"SELECT USERNAME, {test_type} FROM {subject_table} WHERE USERNAME=?",
            (username,),
        )
        tobe_moderate = cursor.fetchall()

    if test_type.upper() == "EXAM":
        max_value = 60
    else:
        max_value = 20

    for user_detail in tobe_moderate:
        overall_score = 0
        try:
            overall_score = user_detail[1] + value
        except TypeError:
            overall_score = value
        if overall_score < max_value:
            cursor.execute(
                f"UPDATE {subject_table} SET {test_type}=? WHERE USERNAME=?",
                (overall_score, user_detail[0]),
            )
            conn.commit()
        else:
            cursor.execute(
                f"UPDATE {subject_table} SET {test_type}=? WHERE USERNAME=?",
                (max_value, user_detail[0]),
            )
            conn.commit()


# print("moderating scores")
# moderate_scores(10, "IRK","PRIMARY_4", "EXAM", "*")
# schl = School()
# for clas in ["JSS_1", "JSS_2"]:
#     for sub in schl.junior_subjects:
#         moderate_scores(10, sub.upper(), clas, "EXAM", "*")
# print("moderation ends now")


def scheduled_subjects() -> List:
    cursor = conn.cursor()
    empt_list2 = []
    all_tables = db_tables()
    # print(all_tables)
    lock.acquire(True)
    my_list = [table for table in all_tables if "SETTINGS" in table]
    for setting in my_list:
        setting = setting.replace(" ", "_")
        cursor.execute(f"SELECT * FROM {setting}")
        scheduled = cursor.fetchall()

        empt_list2.append(scheduled)

    lock.release()
    empt_list2 = [schedule for schedule in empt_list2 if schedule != []]

    final_list = []

    for lst in empt_list2:
        for sub_lst in lst:
            final_list.append(sub_lst)

    return final_list


def list_remove(list_name: List, value: Any) -> List:
    x = 0
    while value in list_name:
        for element in list_name:
            if element == value:
                list_name.remove(element)
                list_name.insert(x, "")
            x += 1

    return list_name


def remove_trash(table_name: str) -> List:
    details = fetch_table_details(table_name)

    im_details = []
    x = 0
    # print(details)
    for detail in details:
        detail = list(detail)
        new_det = list_remove(detail, None)
        im_details.append(new_det)

    return im_details


# "JSS_3_ATTENDANCE"

# print(remove_trash("JSS_2_ATTENDANCE"))


def table_columns(table_name):
    cursor = conn.cursor()
    lock.acquire(True)
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    lock.release()
    # print(columns)

    columns_list = []
    for x in columns:
        columns_list.append(x[1])
    return columns_list


def store_option(current_question, selected_opt):
    del current_question[3]
    current_question.insert(3, selected_opt)
    # print(current_question)


def fetch_by_class(class_name: str) -> List:
    cursor = conn.cursor()
    lock.acquire(True)
    cursor.execute("SELECT * FROM USERS WHERE user_class = ?", (class_name,))

    lock.release()
    return cursor.fetchall()


# print(fetch_by_class("JSS_2"))
def make_total(score_list: Tuple) -> int:
    total = 0
    # print(score_list)
    for x in score_list[:-1]:
        try:
            x = int(x)
        except ValueError:
            x = 0
        total += x

    return total


def make_total_tup(score_list: Tuple) -> int:
    total = 0
    # print(score_list)
    for x in list(score_list):
        try:
            x = int(x)
        except ValueError:
            x = 0
        total += x

    return total


def stb_score(username, test_type, subject, class_name):
    cursor = conn.cursor()
    max_score = 20
    subject_table = f"{subject}_{class_name}_SCORES".upper()

    cursor.execute(f"SELECT USERNAME, {test_type} FROM {subject_table}")
    tobe_moderate = cursor.fetchall()
    if test_type.upper() == "EXAM":
        max_score = 20
    # print(tobe_moderate)
    for user_detail in tobe_moderate:
        user_score = user_detail[1]
        try:
            if type(user_score) == str:
                user_score = 0
        except TypeError:
            pass
        #     user_score = 0
        if user_score > max_score:
            cursor.execute(
                f"UPDATE {subject_table} SET {test_type}=? WHERE USERNAME=?",
                (max_score, user_detail[0]),
            )
            conn.commit()


# schl = School()
# for clas in ["PRIMARY_4", "PRIMARY_5"]:
#     for sub in schl.primary_subjects:
#         stb_score("*", "EXAM", sub, clas)
# print("moderation ends now")
# stb_score("*", "EXAM", "MATHEMATICS", "JSS_2")


def make_report_sheet(class_name: str) -> bool:
    cursor = conn.cursor()
    jss_2_table = [
        table
        for table in db_tables()
        if class_name.replace("_", " ") in table
        if "SETTINGS" and "DETAILS" not in table
    ]
    jss_2_table.sort()

    fetch_details = fetch_table_details(class_name + "_ATTENDANCE")
    # print(fetch_details)
    compiled_results = []
    my_school = School()
    # try:
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {class_name}_INFO_SHEET(id INTEGER PRIMARY KEY, USERNAME TEXT UNIQUE, FIRST_NAME TEXT, SURNAME TEXT, LAST_NAME TEXT, REGISTER_NUMBER NUMBER, MAX_ATTENDANCE NUMBER, 
    GENDER TEXT, CLASS TEXT, TERM TEXT, NUMBER_OF_PRESENT_DAYS NUMBER, NUMBER_OF_STUDENT NUMBER, TERM_ENDED TEXT, NUMBER_OF_ABSENT_DAYS NUMBER) """
    )
    # except sqlite3.OperationalError:
    #     pass
    current_school = School()
    try:
        for std_info in fetch_by_class(class_name):
            # print("Testing progress")
            empt = ""
            cursor.execute(
                f"""INSERT INTO {class_name}_INFO_SHEET (USERNAME, FIRST_NAME, SURNAME,
            LAST_NAME, REGISTER_NUMBER, MAX_ATTENDANCE, GENDER, CLASS, TERM, 
            NUMBER_OF_PRESENT_DAYS, NUMBER_OF_STUDENT, TERM_ENDED, NUMBER_OF_ABSENT_DAYS) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    std_info[-2],
                    std_info[1],
                    std_info[2],
                    std_info[3],
                    std_info[-3],
                    empt,
                    std_info[4],
                    std_info[-4],
                    current_school.current_term,
                    empt,
                    len(fetch_by_class(class_name)),
                    current_school.term_ended,
                    empt,
                ),
            )
    except sqlite3.IntegrityError:
        pass
        # for std_info in fetch_by_class(class_name):
        #     empt = ""
        #     cursor.execute(f"""UPDATE {class_name}_INFO_SHEET SET (USERNAME, FIRST_NAME, SURNAME,
        #     LAST_NAME, REGISTER_NUMBER, MAX_ATTENDANCE, GENDER, CLASS, TERM,
        #     NUMBER_OF_PRESENT_DAYS, NUMBER_OF_STUDENT, TERM_ENDED, NUMBER_OF_ABSENT_DAYS) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        #     """, (std_info[-2], std_info[1], std_info[2], std_info[3], std_info[-3], empt, std_info[4], std_info[-4],
        #     current_school.current_term, empt, len(fetch_by_class(class_name)), current_school.term_ended, empt))

    offered_subjects = my_school.primary_subjects

    offered_subjects.sort()

    if "JS" in class_name.upper():
        offered_subjects = my_school.junior_subjects

    # compiled_results = []

    for offer_subj in offered_subjects:
        offer_subj = offer_subj.upper() + "_" + class_name + "_SCORES"
        cursor.execute(
            f"SELECT username, first_name, surname, middle_name, FIRST_CA, SECOND_CA, EXAM, PPT FROM {offer_subj}"
        )
        # print("going through scores")

        # print(cursor.fetchall())
        # print("scores executin done")

        for std in cursor.fetchall():
            std = list(std)
            # print(std)
            ppt_score = std[-1]
            exam_score = std[-2]
            overall_exam = make_total_tup((ppt_score, exam_score))
            # print(ppt_score,exam_score,overall_exam)

            del std[-1]
            del std[-1]
            std.append(overall_exam)
            std.append(offer_subj.replace("_" + class_name + "_SCORES", ""))
            compiled_results.append(std)
    # print(compiled_results)

    query = f"CREATE TABLE IF NOT EXISTS {class_name}_SCORE_SHEET(id INTEGER PRIMARY KEY, USERNAME TEXT UNIQUE, FIRST_NAME TEXT, SURNAME TEXT, MIDDLE_NAME TEXT,"

    for subject in offered_subjects:
        query += " " + subject.upper() + "_FIRST_CA" + " TEXT,"
        query += " " + subject.upper() + "_SECOND_CA" + " TEXT,"
        query += " " + subject.upper() + "_EXAM" + " TEXT,"

    query = query[:-1] + ")"
    # print(query)
    cursor.execute(query)
    # except sqlite3.IntegrityError:
    #     pass

    for std_info in fetch_details:
        reg_number = int(std_info[4])
        cursor.execute(
            f"""UPDATE {class_name}_INFO_SHEET SET MAX_ATTENDANCE=?,  
        NUMBER_OF_PRESENT_DAYS=?, NUMBER_OF_STUDENT=?, TERM_ENDED=?, NUMBER_OF_ABSENT_DAYS=? WHERE REGISTER_NUMBER=?
        """,
            (
                std_info[5],
                std_info[6],
                len(fetch_details),
                my_school.term_ended,
                std_info[7],
                reg_number,
            ),
        )

    try:
        cursor.execute(f"ALTER TABLE {class_name}_SCORE_SHEET ADD COLUMN TOTAL NUMBER;")
        cursor.execute(
            f"ALTER TABLE {class_name}_SCORE_SHEET ADD COLUMN POSITION TEXT;"
        )
    except sqlite3.OperationalError:
        pass

    fetch_class = fetch_table_details(class_name + "_DETAILS")
    # print(fetch_class)
    try:
        for detail in fetch_class:
            cursor.execute(
                f"INSERT INTO {class_name}_SCORE_SHEET (username, first_name, surname, MIDDLE_NAME) VALUES(?, ?, ?, ?)",
                (detail[-2], detail[1], detail[2], detail[3]),
            )
    except sqlite3.IntegrityError:
        pass
    # FETCHING THE SCORES TO THE BROAD SHEET

    for indiv_subj in compiled_results:
        cursor.execute(
            f"UPDATE {class_name}_SCORE_SHEET SET {indiv_subj[-1]}_FIRST_CA=?, {indiv_subj[-1]}_SECOND_CA=?, {indiv_subj[-1]}_EXAM=? WHERE USERNAME=?",
            (indiv_subj[-4], indiv_subj[-3], indiv_subj[-2], indiv_subj[0]),
        )

    # CALCULATING AND INSERTING TOTAL SCORES
    std_scr = []

    for std in fetch_table_details(class_name + "_SCORE_SHEET"):
        scores = std[5:-2]
        # print(scores)
        std_scr.append(make_total(scores))
        cursor.execute(
            f"UPDATE {class_name}_SCORE_SHEET SET TOTAL=? WHERE USERNAME=?",
            (make_total(scores), std[1]),
        )

    # DECIDING POSITION
    std_scr = list(set(std_scr))
    std_scr.sort(reverse=True)

    my_dict = {}

    position = 1

    for score in std_scr:
        my_dict[str(score)] = position

        suffix = ""
        if str(position)[-1] == "1" and position != 11:
            suffix = "st"
        elif str(position)[-1] == "2" and position != 12:
            suffix = "nd"
        elif str(position)[-1] == "3" and position != 13:
            suffix = "rd"
        else:
            suffix = "th"
        real_position = str(position) + suffix
        position += 1
        cursor.execute(
            f"UPDATE {class_name}_SCORE_SHEET SET POSITION=? WHERE TOTAL=?",
            (real_position, score),
        )

    conn.commit()


# make_report_sheet("JSS_1")


def decide_grade(total_score: int) -> List:
    if total_score >= 70:
        return ["A", "Distinction"]
    elif total_score < 70 and total_score >= 60:
        return ["B", "Very Good"]
    elif total_score < 60 and total_score >= 50:
        return ["C", "Good"]
    elif total_score < 50 and total_score >= 45:
        return ["D", "Pass"]
    elif total_score < 45 and total_score >= 38:
        return ["E", "Weak"]
    elif total_score < 38:
        return ["F", "Fail"]


def process_results(class_name: str) -> List:
    cursor = conn.cursor()
    jss_2_table = [
        table
        for table in db_tables()
        if class_name.replace("_", " ") in table
        if "SETTINGS" not in table
    ]
    jss_2_table.sort()

    compiled_list = []
    fetched_class = fetch_by_class(class_name=class_name)
    # print(fetched_class)

    new_tables = [table for table in jss_2_table if "SCORES" in table]
    # print(new_tables)
    # print(new_tables)
    for std_details in fetched_class:
        # print(12435475885)
        # print(std_details)
        # print(18399393838)
        username = std_details[-2]
        empt = []
        for table in new_tables:
            # print(table)
            cursor.execute(
                f"SELECT * FROM {table.replace(' ', '_')} WHERE USERNAME=?", (username,)
            )
            # print(list(cursor.fetchone()))
            try:
                fetched_detail = list(cursor.fetchone())
                # print(fetched_detail)
            except TypeError:
                pass
            modified_class = class_name.replace("_", " ")
            replace_str = " " + modified_class + " SCORES"
            total_exam = make_total_tup((fetched_detail[-3], fetched_detail[-2]))
            fetched_detail.insert(0, table.replace(replace_str, ""))
            fetched_detail.insert(-1, total_exam)
            scores = fetched_detail[6:11]
            fetched_detail[-1] = make_total_tup(scores)
            fetched_detail.append(decide_grade(fetched_detail[-1]))
            # print(fetched_detail, "12839")
            # print(make_total(scores))
            empt.append(fetched_detail)

        cursor.execute(
            f"SELECT TOTAL, POSITION FROM {class_name}_SCORE_SHEET WHERE USERNAME=?",
            (username,),
        )
        broad_score = cursor.fetchone()

        # print(broad_score, 1322222222222222222222222222222222222243526262)
        empt.append(broad_score)
        compiled_list.append(empt)
        # print(compiled_list)
    # print(compiled_list, "compile list")
    return compiled_list


# process_results("JSS_1")
# make_report_sheet("JSS_1")
# print(scheduled_subjects())


class User:
    def __init__(self, username: str) -> None:
        self.username = username.upper()
        self.first_name = user_details(username)[1]
        self.surname = user_details(username)[2]
        self.middle_name = user_details(username)[3]
        self.gender = user_details(username)[4]
        self.dob = user_details(username)[5]
        self.user_image = get_user_image(username)
        self.use_type = user_details(username)[7]
        self.user_class = user_details(username)[8]
        self.reg_number = user_details(username)[9]
        self.user_password = user_details(username)[10]

    def is_registered(self) -> bool:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM USERS WHERE username=?", (self.username,))
        fetched_user = cursor.fetchone()

        if fetched_user is None:
            return False
        return True

    def cheched_written(self, selected_subject: str) -> bool:
        cursor = conn.cursor()
        selected_subject = selected_subject.upper()
        user_class = self.user_class.upper()
        # user_class = user_class[:-1] + "_" + user_class[-1]
        user_setting_table = user_class + "_SETTINGS"
        print(user_setting_table, "class table")
        cursor.execute(
            f"SELECT EXAM_TYPE from {user_setting_table} WHERE SUBJECT=?",
            (selected_subject,),
        )
        try:

            exam_type = cursor.fetchone()[0]
            print(exam_type)
        except TypeError:
            return f"The test {selected_subject} had not been scheduled"

        subject = session["selected_subject"]
        user_class_score = subject.upper() + "_" + user_class + "_SCORES"
        cursor.execute(
            f"SELECT {exam_type} FROM {user_class_score} WHERE username=?",
            (self.username,),
        )
        initial_score = cursor.fetchone()[0]
        print(initial_score, "scoreeee")
        # print(initial_score)
        if initial_score == "":
            return True
        return False

    def logout(self):
        session.clear()

    def check_user_type(self) -> str:
        if self.username.lower() == "admin@gmail.com":
            return "ADMIN"
        elif self.username[1].upper() == "T":
            return "TEACHER"
        elif self.username[1].upper() == "S":
            return "STUDENT"

    def check_password(self, password: str) -> str:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_Password FROM USERS WHERE username=?", (self.username,)
        )
        fetched_user = cursor.fetchone()

        if password.upper() == fetched_user[0].upper():
            return "CORRECT"
        return "INCORRECT"

    def verify_subject(self, selected_subject: str) -> bool:
        cursor = conn.cursor()
        # print(session["selected_subject"])

        try:
            user_class = self.user_class.upper()
            # user_class = user_class[:-1] + "_" + user_class[-1]
        except TypeError:
            return False
        # print(user_class, "userclass")
        setting_table = user_class + "_SETTINGS"
        print(setting_table, 909090)

        cursor.execute(
            f"SELECT SUBJECT FROM {setting_table} WHERE SUBJECT=?", (selected_subject,)
        )
        collected_subject = cursor.fetchone()

        if collected_subject is None:
            return False
        return True

    def start_quiz(self, open_subject: str):
        open_subject = "pre_test_questions.json"
        with open(open_subject, encoding="utf-8") as f_obj:
            questions_dict = json.load(f_obj)
            questions = questions_dict["banks"]
            questions = questions[:19]

            for question in questions:
                question.append(None)
                if len(question) == 4:
                    question.append("")

            session["questions"] = questions

    def save_score(self, selected_subject: str, questions: List) -> str:
        ############### COMPUTING USER SCORE #############
        cursor = conn.cursor()
        user_score = 0
        compare_list = []
        print(questions)
        for question in questions:
            if question[2] == question[3]:
                user_score += 1
                compare_list.append(question[2])
                compare_list.append(question[3])

        user_score = user_score * exam_settings(self.username, selected_subject)[-1]
        # print(compare_list)

        ################ SAVING USER SCORE ###############
        user_class = self.user_class.upper()
        user_class = user_class
        user_setting_table = user_class.title() + "_SETTINGS"
        # print(user_setting_table)
        cursor.execute(
            f"SELECT EXAM_TYPE FROM {user_setting_table} WHERE SUBJECT=?",
            (selected_subject,),
        )

        exam_type = cursor.fetchone()[0]
        # print(exam_type, "873828")
        subject = session["selected_subject"]
        user_subject_score = subject.upper() + "_" + user_class + "_SCORES"
        # print(user_subject_score)
        # cursor.execute(f"SELECT {exam_type} FROM {user_subject_score} WHERE username=?", (self.username,))
        cursor.execute(
            f"UPDATE {user_subject_score} SET {exam_type}=? WHERE username=?",
            (user_score, self.username),
        )
        conn.commit()

    def upload_image(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE username = ?", (self.username,))
        check_user = cursor.fetchone()
        # print(check_user)
        if "image" in request.files:
            image_file = request.files["image"]
            print(image_file, "I am image file")
            if image_file.filename != "":
                # Read the image file
                image_data = image_file.read()

                # Encode the image data to base64
                encoded_image = base64.b64encode(image_data).decode("utf-8")

                cursor.execute(
                    "UPDATE USERS SET img_upload = ? WHERE username = ?",
                    (encoded_image, self.username),
                )
                print("I works fine and well")
                conn.commit()
                # conn.close()

                return encoded_image


def get_results(class_name: str, username: str = "*") -> List:
    cursor = conn.cursor()
    make_report_sheet(class_name)
    class_results = process_results(class_name)
    # print(class_results)
    if username == "*":
        return class_results
    else:
        user_to_return = []

        for std_result in class_results:
            # print(std_result[-7])
            if std_result[0][-8] == username:
                user_to_return.append(std_result)

        # info_sheet = fetch_table_details(class_name + "_INFO_SHEET")
        reg_num = int(User(username).reg_number)
        # print("reg number beginng")
        # print(reg_num)

        info_sheet = class_name + "_INFO_SHEET"
        cursor.execute(
            f"SELECT MAX_ATTENDANCE, NUMBER_OF_PRESENT_DAYS, NUMBER_OF_ABSENT_DAYS, GENDER, NUMBER_OF_STUDENT FROM {info_sheet} WHERE REGISTER_NUMBER=?",
            (reg_num,),
        )
        _attendance = list(cursor.fetchone())
        _attendance.append(class_name.replace("_", " "))
        print(user_to_return)
        user_to_return[0].append(_attendance)
        print(user_to_return)
        return user_to_return


def check_exist(table_name: str, check_by: str, value: str) -> List:
    cursor = conn.cursor()
    data = cursor.execute(f"SELECT * FROM {table_name} WHERE {check_by}=?", (value,))
    return data.fetchall()


class Admin:
    def assign_to(
        self, username: str, teachers_name: str, role_assigned: str, assigned_class: str
    ):
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS ROLE_ASSIGNMENT(USERNAME TEXT,NAME TEXT, ROLE TEXT, ASSIGNED_CLASS TEXT, ROLE_NAME TEXT)"
        )
        role_id = role_assigned + assigned_class
        fetch_user = check_exist("ROLE_ASSIGNMENT", "ROLE_NAME", role_id)
        print(fetch_user)
        if fetch_user == []:
            cursor.execute(
                "INSERT INTO ROLE_ASSIGNMENT VALUES(?, ?, ?, ?, ?)",
                (username, teachers_name, role_assigned, assigned_class, role_id),
            )
            conn.commit()
        else:
            cursor.execute(
                "UPDATE ROLE_ASSIGNMENT SET NAME=?, USERNAME=? WHERE ROLE_NAME=?",
                (teachers_name, username, fetch_user[0][-1]),
            )
            conn.commit()

    def fetch_report_card(self, class_name: str = "JSS 2", username: str = "*") -> List:
        cursor = conn.cursor()
        jss_2_table = [
            table
            for table in db_tables()
            if class_name in table
            if "SETTINGS" and "DETAILS" not in table
        ]
        jss_2_table.sort()
        empt = []
        for table in jss_2_table:
            table = table.replace(" ", "_")
            if "username" in table_columns(table_name=table):
                empt2 = []
                if username == "*":
                    cursor.execute(
                        f"SELECT first_name, surname, middle_name, reg_number, FIRST_CA, SECOND_CA, EXAM FROM {table}",
                    )
                else:
                    cursor.execute(
                        f"SELECT first_name, surname, middle_name, reg_number, FIRST_CA, SECOND_CA, EXAM FROM {table} WHERE username=?",
                        (username,),
                    )

                fetch = list(cursor.fetchall())
                print(table.replace("JSS_2_SCORE", ""))
                empt2.append(
                    table.replace("JSS_2_SCORES", "").replace("_", " ").strip()
                )
                empt2.append(fetch)
                empt.append(empt2)
            else:
                pass
        return empt


my_ADMIN = Admin()


# print(my_ADMIN.fetch_report_card(class_name="JSS 2", username="JS23030"), "95858")
# print(len(fetch_table_details("USERS")))
def arrange_report(class_name: str, username: str = "*") -> List:
    report_list = []
    # my_ADMIN = Admin()

    # cursor.execute(f"SELECT {username}")
    fetch_details = my_ADMIN.fetch_report_card()

    return fetch_details


def bio_details(username: str) -> dict:
    Student = User(username)
    class_details = fetch_table_details(Student.user_class + "_DETAILS")
    total_students = len(class_details)
    gender = Student.gender
    reg_number = Student.reg_number
    student_class = Student.user_class

    bio_detail: dict = {
        "total_students": total_students,
        "gender": gender,
        "reg_number": reg_number,
        "student_class": student_class,
        "session": "2024/2025",
        "term": "first term",
        "term_ended": "16/12/2024",
        "new_term_begin": "06/01/2025",
    }

    return bio_detail


def score_list(username: str):
    lst = []
    for subject_det in fetch_result(username)["subject_performance"]:
        # print(subject_det['subject'])
        lst.append(subject_det["subject_score"]["total"])

    return lst


def format_position(postn: int) -> str:
    if str(postn)[-1] == "1" and postn != 11:
        return str(postn) + "st"
    elif str(postn)[-1] == "2" and postn != 12:
        return str(postn) + "nd"
    elif str(postn)[-1] == "3" and postn != 13:
        return str(postn) + "rd"
    else:
        return str(postn) + "th"


def position(username: str) -> dict:
    Student = User(username=username)
    full_name = f"{Student.first_name} {Student.surname} {Student.middle_name}"
    student_class = Student.user_class
    all_students = fetch_table_details(student_class + "_DETAILS")
    std_score: list = []

    for std in all_students:
        user_total = {
            "username": std[-2],
            "overall_score": reduce(lambda x, y: x + y, score_list(std[-2])),
        }

        std_score.append(user_total)

    sort_list = sorted(std_score, key=lambda x: x["overall_score"], reverse=True)

    postn = 1
    for student in sort_list:
        if postn != 1:
            if sort_list[postn - 2]["overall_score"] == student["overall_score"]:
                # print(sort_list[postn-2])
                student["position"] = format_position(postn - 1)
            else:
                student["position"] = format_position(postn)
        else:
            student["position"] = format_position(postn)
        postn += 1

    for user in sort_list:
        if user["username"] == username:
            user["full_name"] = full_name
            print(full_name)
            return user


def fetch_result(username: str) -> dict:
    cursor = conn.cursor()
    jss_2_table = [table for table in db_tables() if "SETTINGS" not in table]
    jss_2_table.sort()

    new_tables = [table.replace(" ", "_") for table in jss_2_table if "SCORES" in table]
    # print(new_tables)
    user_scores = []
    student_data = {}

    for subject in new_tables:
        subject_dict: dict = {}
        total_score: int = 0
        # print(subject)
        user_score = cursor.execute(
            f"select FIRST_CA, SECOND_CA, EXAM from {subject} where username=?",
            (username,),
        ).fetchone()

        if user_score is not None and "ARABIC_LANGUAGE" not in subject:
            for _score in user_score:
                if type(_score) is int:
                    total_score += _score

            user_score = list(user_score)
            # user_score.append(total_score)
            # user_score.append(subject)
            subject_dict["subject"] = subject
            subject_dict["subject_score"] = {}
            subject_score = subject_dict["subject_score"]
            subject_score["first_ca"] = user_score[0]
            subject_score["second_ca"] = user_score[1]
            subject_score["exam"] = user_score[2]
            subject_score["total"] = total_score
            subject_score["grade"] = decide_grade(total_score=total_score)
            user_scores.append(subject_dict)

    student_data["subject_performance"] = user_scores
    student_data["bio_details"] = bio_details(username=username)
    return student_data


def get_result(username: str) -> dict:
    try:

        big_dict: dict = fetch_result(username)
        small_dict: dict = position(username)

        combine_dict: dict = {"subj_details": big_dict, "main_details": small_dict}

        return combine_dict
    except TypeError:
        return None


# print(fetch_result('JS24002'))

# print(arrange_report("jss2"))

# def update_class(table_name: str, column: str, new_value: str) -> None:
#     new_value = new_value[:-1] + "_" + new_value[-1]
#     print(new_value)
#     cursor.execute(f"UPDATE {table_name} SET {column}=?", (new_value,))

# def process():
#     # if request.method == "POST":
#     students_data = fetch_table_details("USERS")
#     for data in students_data:
#         print(data[1])
#         first_name = data[1]
#         surname = data[2]
#         middle_name = data[3]
#         collected_user_class = data[8]
#         collected_user_class = collected_user_class[:-1] + "_" + collected_user_class[-1]
#         user_class = collected_user_class
#         gender = data[4]
#         dob = data[5]
#         reg_number = data[9]
#         create_password = data[11]
#         confirm_password = data[11]
#         user_type = data[7]
#         # print(collected_user_class[:-1] + "_" + collected_user_class[-1])
#         # # register_user(first_name, surname, middle_name, collected_user_class, gender, dob, reg_number, create_password, confirm_password, user_type)
#         reg_number = str(reg_number)
#         if len(reg_number) == 2:
#             reg_number = "0" + reg_number
#         elif len(reg_number) == 1:
#             reg_number = "00" + reg_number


#         initial_year = 2024 - int(collected_user_class[-1]) + 1
#         username = data[10]

#         # print(user_class)
#         image_upload = ''

#         user_score = ""
#         "Yes sirrrr"
#         gen_connect = sqlite3.connect("USERS.db")
#         gen_cursor = gen_connect.cursor()

#         # gen_cursor.execute(f"""CREATE TABLE IF NOT EXISTS USERS(
#         #     id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, gender TEXT, dob TEXT, img_upload BLOB, user_type TEXT, user_class TEXT, reg_number TEXT, username TEXT, user_Password TEXT)""")
#         # gen_cursor.executescript()
#         fetch_reg_numbers = gen_cursor.execute("SELECT * FROM USERS WHERE username=?", (username,))

#         fetch_reg_numbers = fetch_reg_numbers.fetchall()
#         if create_password == confirm_password:
#             print(reg_number+" I am reg number")
#             if user_type == "STUDENT" and reg_number != '':

#                 gen_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {user_class}_DETAILS(
#                                     id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, gender TEXT, dob TEXT, img_upload BLOB, user_type TEXT, user_class TEXT, reg_number TEXT, username TEXT, user_Password TEXT)""")
#                 print(user_class)
#                 gen_cursor.execute(f"CREATE TABLE IF NOT EXISTS {user_class}_ATTENDANCE(id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, reg_number TEXT, total_attendance NUMBER, number_of_times_present NUMBER, number_of_times_absent NUMBER, form_teacher_comment TEXTT)")
#                 test_lists = ["FIRST_CA", "SECOND_CA", "EXAM", "PPT"]

#                 junior_subjects = ["English_Language", "Mathematics", "Civic_Education", "Agric_Science", "Social_Studies",
#                         "Business_Studies", "Basic_Studies", "Computer", "IRK", "Arabic_Language", "Hausa_Language"]

#                 primary_subjects = ["Mathematics", "English_Language", "Basic_Science", "Social_Studies", "Hausa_Language",
#                                     "IRK", "Jolly_Phonics_Writing", "Computer"]


#                 offered_subjects =""
#                 if collected_user_class[0].upper() == "J":
#                     offered_subjects = junior_subjects
#                 else:
#                     offered_subjects = primary_subjects

#                 for subject in offered_subjects:
#                     table_name = subject.upper() + "_" + collected_user_class.upper() + "_SCORES"

#                     gen_cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name}(id INTEGER PRIMARY KEY, first_name TEXT, surname TEXT, middle_name TEXT, reg_number TEXT, username TEXT, FIRST_CA NUMBER, SECOND_CA NUMBER, EXAM NUMBER, PPT NUMBER, TOTAL NUMBER)")

#                     gen_cursor.execute(f"INSERT INTO {table_name} (first_name, surname, middle_name, reg_number, username, FIRST_CA, SECOND_CA, EXAM, PPT, TOTAL) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
#                     (first_name.upper(), surname.upper(), middle_name.upper(), reg_number, username, user_score, user_score, user_score, user_score, user_score))

#                 # gen_cursor.execute(f"INSERT INTO USERS (first_name, surname, middle_name, gender, dob, img_upload, user_type, user_class, reg_number, username, user_Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
#                 # (first_name.upper(), surname.upper(), middle_name.upper(), gender.upper(), dob, image_upload,user_type, user_class.upper(), reg_number, username, create_password))
#                 gen_cursor.execute(f"INSERT INTO {user_class.upper()}_DETAILS (first_name, surname, middle_name, gender, dob, img_upload, user_type, user_class, reg_number, username, user_Password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
#                 (first_name.upper(), surname.upper(), middle_name.upper(), gender.upper(), dob, image_upload,user_type, user_class.upper(), reg_number, username, create_password))

#                 gen_cursor.execute(f"INSERT INTO {user_class.upper()}_ATTENDANCE (first_name, surname, middle_name, reg_number) VALUES(?, ?, ?, ?)", (first_name.upper(), surname.upper(), middle_name.upper(), reg_number))

#                 gen_connect.commit()
#                 gen_connect.close()
#                 # Student = User(username)
#                 # register_student(first_name, surname, middle_name, collected_user_class, gender, dob, reg_number, create_password, confirm_password, user_type)
#                 # return jsonify({"success": f"Dear {first_name} {surname} {middle_name}, you have registered successfully. Your username is {username}"})
#                 print(f"Dear {first_name} {surname} {middle_name}, you have registered successfully. Your username is {username}")

# process()
