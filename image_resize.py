import base64
import sqlite3
from PIL import Image, UnidentifiedImageError
import io
from flask import Flask, render_template
# from current_resize import image_data

app = Flask(__name__)
# from image_resize import image

# Connect to SQLite3 database
conn = sqlite3.connect('USERS.db')
cursor = conn.cursor()

# username = "JS22002"
# Retrieve binary image data from the database
# cursor.execute("SELECT img_upload FROM USERS WHERE username = ?", (username,))
# image_data = cursor.fetchone()[0]



# file = None
# image_data = "JS23024.jpg"
# with open(image_data, 'rb') as image_file:
#     file = image_file.read()
#     print(len(file))

# image = Image.open(io.BytesIO(file))
# image.show()
# import ast
# print(image_data)
# print(type(image_data))
# str
# data = base64.b64encode(image_data)
# data = data.decode("utf-8")
# print(data)
