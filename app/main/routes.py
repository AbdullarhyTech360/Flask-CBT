from flask import render_template

# Import the blueprint defined in __init__.py
from . import main_bp

@main_bp.route('/')
def index():
    return render_template('main/index.html')
