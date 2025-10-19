from flask import render_template, redirect, url_for, request, flash

# Import the blueprint defined in __init__.py
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '1234':
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid credentials', 'danger')
    return render_template('auth/login.html')
