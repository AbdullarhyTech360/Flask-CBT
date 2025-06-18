from flask import Flask, request, render_template, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users5.sqlite3'

# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     first_name = db.Column(db.String(30))
#     surname = db.Column(db.String(30))
#     last_name = db.Column(db.String(30))
#     user_type = db.Column(db.String(30))
#     user_class = db.Column(db.String(30))
#     date_registered = db.Column(db.String(20), default=datetime.now().strftime('%d/%m/%Y, %H:%M:%S'))

#     def __init__(self, first_name, surname, last_name, user_type, user_class):
#         self.first_name = first_name
#         self.surname = surname
#         self.last_name = last_name
#         self.user_type = user_type
#         self.user_class = user_class

#     def __repr__(self):
#         return f"{self.first_name} {self.surname} {self.last_name}"

# class Student(db.Model):
#     student_id = db.Column(db.Integer, primary_key = True)
#     user_id = db.Column(db.String(30), db.ForeignKey('users.id'))
#     name = db.Column(db.String(30))

#     def __init__(self, name):
#         self.name = name

# class Teacher(db.Model):
#     teacher_id = db.Column(db.Integer, primary_key = True)
#     user_id = db.Column(db.String(30), db.ForeignKey('users.id'))
#     name = db.Column(db.String(30))

#     def __init__(self, name):
#         self.name = name

# class Class(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(30))
    
#     def __init__(self, name):
#         self.name = name

# class Subject(db.Model):
#     subject_id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(30))
#     class_id = db.Column(db.String(30), db.ForeignKey('class.id'))
    
#     def __init__(self, name):
#         self.name = name
# from flask import jsonify, request
# import json

# app = Flask(__name__)

# my_dict = {
#     "name": "abdullahi",
#     "surname" : "musa",
#     "middle_name": "kidandan",
#     "age": 25,
#     "location": {"country": "nigeria", "state": "kaduna", "local_government": "giwa", "ward": "shika"},
#     "best_color": "green"
# }

lamd2 = r"\\[\\left[\\begin{matrix}\\frac{1}{3}&\\frac{1}{x}\\\\\frac{1}{5^x}&0\\\\\end{matrix}\\right]\\]"

quest = r"\[2^\frac{8}{3} 2/3 \pi \text{ is equivalent to }\]"

# quest = quest.replace("2/3", r"\frac{2}{3}")

# print()
options = r"\[\frac{{2}}{{7}} \]"
name = r"\[ 2^3 \text{ is equal to} \]"

from mathematics import bank  # noqa: E402

quest_lists = bank["banks"]

@app.route("/")
def welcome():
    return render_template("quick2.html", quest_list = quest_lists, lamb = lamd2)

@app.route('/post', methods=["GET", "POST"])
def post():
    if request.method == 'POST':
        print(request.args.get('name'))
        return jsonify({'message': 'I am very happy. Data recieved from front end'})

# with app.app_context():
#     db.create_all()
# if __name__ == "__main__":
#     app.run(debug=True)


# @app.route("/get_data", methods=["post", "get"])
# def get_data():
#     return jsonify(my_dict)

# @app.route("/post_data", methods=["POST", "GET"])
# def post_data():
#     if request.method == "POST":
#         data = request.get_json()
#         print(data)
#         return jsonify({"message": my_dict})

# import sqlite3
# connection = sqlite3.connect("USERS.db")

# cursor = connection.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# print(tables)

# import MySQLdb

# import json
# import sqlite3

# dict_ = {
#     "alpha": r"\alpha",
#     "beta": r"\beta",
#     "gamma": "\gamma",
#     "lambda": "\lambda"
# }

# empt = ""

# sentence = "with alpha beta and gamma"

# for subs, val in dict_.items():
    
#     # empt = sentence.replace(subs, val)
#     print(empt)
    

# from quiz_logic import cursor
# from simpleFlask import connection
# connection = sqlite3.connect("USERS.db")

# def table_columns(table_name):
#     cursor = connection.cursor()
#     cursor.execute(f"PRAGMA table_info({table_name});")
#     columns = cursor.fetchall()
#     # print(columns)
#     columns_list = []
#     for x in columns:
#         columns_list.append(x[1])
#     return columns_list

# print(table_columns("USERS"))

# connection = sqlite3.connect("USERS.db")
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM USERS")
# all_users = cursor.fetchall()
# print(all_users)


# junior_subjects = ["English", "Mathematics", "Civic_Education", "Agric_Science", "Social_Studies",
#                      "Business_Studies", "Basic_Studies", "Computer", "IRK", "Arabic_Language", "Hausa_Language"]

# primary_subjects = ["Mathematics", "English_Language", "Basic_Science", "Social_Studies", "Hausa_Language",
#                     "IRK", "Jolly_Phonics/Writing", "Computer"]

# tests = ["First_CA", "Second_CA", "Exam", "PPT", "Total"]

# user_class = "JSS2"
# for subject in junior_subjects:
#     score_table = subject.upper() + user_class.upper() + "_SCORES"
#     cursor.execute(f"CREATE TABLE IF NOT EXISTS {score_table}(FIRST_CA NUMBER, SECOND_CA NUMBER, EXAM NUMBER, PPT NUMBER, TOTAL NUMBER)")
#     # cursor.executemany(f"INSERT ")

# connection.commit()
# connection.close()
# C = "aBD"
# C.replace("f", "j")
# print(C)