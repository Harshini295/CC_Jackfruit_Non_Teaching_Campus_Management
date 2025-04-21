from flask import request, render_template, redirect, session, url_for, flash, jsonify
import MySQLdb

def register_routes(app, mysql):
    @app.route('/')
    @app.route('/home')
    def home():
        if 'email' in session:
            return render_template('home.html')
        return redirect('/login')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()

            if user:
                session['loggedin'] = True
                session['id'] = user['id']
                session['email'] = user['email']
                session['user_type'] = user['user_type']
                return redirect('/dashboard')
            else:
                flash('Incorrect email or password', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully.', 'info')
        return redirect(url_for('login'))

    @app.route('/test-db')
    def test_db():
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE();")
        result = cur.fetchone()
        return {'connected_to': result['DATABASE()']}

    @app.route('/dashboard')
    def dashboard():
        if 'email' not in session:
            return redirect(url_for('login'))
        if session['user_type'] == 'admin':
            return render_template('home.html', name=session['email'])
        else:
            return render_template('home.html', name=session['email'])

    @app.route('/submit-grievance', methods=['POST'])
    def submit_grievance():
        data = request.get_json()
        name = data.get('student_name')
        email = data.get('email')
        category = data.get('category')
        message = data.get('message')

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO grievances (student_name, email, category, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, category, message))
        mysql.connection.commit()
        cur.close()
        return render_template('thank_you.html', name=name)

    @app.route('/grievance-form', methods=['GET'])
    def show_grievance_form():
        return render_template('grievance_form.html')

    @app.route('/submit-grievance-form', methods=['GET', 'POST'])
    def handle_grievance_form():
        if request.method == 'POST':
            name = request.form['student_name']
            email = request.form['email']
            category = request.form['category']
            message = request.form['message']

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO grievances (student_name, email, category, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, category, message))
            mysql.connection.commit()
            cur.close()
            return render_template('thank_you.html', name=name)
        return render_template('grievance_form.html')

    @app.route('/view-grievances')
    def view_grievances():
        if 'user_type' not in session or session['user_type'] != 'admin':
            return "Unauthorized Access", 403
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM grievances ORDER BY submitted_at DESC")
        grievances = cur.fetchall()
        cur.close()
        return render_template('view_grievances.html', grievances=grievances)

    @app.route('/student-grievance-redressal')
    def student_grievance_redressal():
        if 'email' not in session:
            return redirect(url_for('login'))
        user_email = session['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT category, message, submitted_at 
            FROM grievances 
            WHERE email = %s 
            ORDER BY submitted_at DESC
        """, (user_email,))
        user_grievances = cur.fetchall()
        cur.close()
        return render_template('student_grievance_redressal.html', user_grievances=user_grievances)

    @app.route('/counseling-services', methods=['GET', 'POST'])
    def counseling_services():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            appointment_date = request.form['appointment_date']
            time_slot = request.form['time_slot']
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO appointments (name, email, appointment_date, time_slot)
                VALUES (%s, %s, %s, %s)
            """, (name, email, appointment_date, time_slot))
            mysql.connection.commit()
            cur.close()
            return render_template('thank_you.html', name=name)
        return render_template('counseling_services.html')

    @app.route('/wellbeing-programs')
    def wellbeing_programs():
        return render_template('wellbeing_programs.html')

    @app.route('/emergency-support')
    def emergency_support():
        return render_template('emergency_support.html')

    @app.route('/hello')
    def hello():
        return "Hello, Flask is working!"

    @app.route('/session-data')
    def session_data():
        return jsonify(dict(session))

    @app.route('/admin/view-appointments')
    def view_appointments():
        if 'user_type' not in session or session['user_type'] != 'admin':
            return "Unauthorized Access", 403
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM appointments ORDER BY submitted_at DESC")
        appointments = cur.fetchall()
        cur.close()
        return render_template('admin/view_appointments.html', appointments=appointments)

    @app.route('/admin/wellbeing-resources')
    def manage_wellbeing_programs():
        if 'user_type' not in session or session['user_type'] != 'admin':
            return "Unauthorized", 403
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM wellbeing_resources ORDER BY submitted_at DESC")
        resources = cur.fetchall()
        cur.close()
        return render_template('admin/manage_resources.html', resources=resources)

    @app.route('/admin/wellbeing-resources/add', methods=['POST'])
    def add_resource():
        if 'user_type' not in session or session['user_type'] != 'admin':
            return "Unauthorized", 403
        title = request.form['title']
        description = request.form['description']
        link = request.form['link']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO wellbeing_resources (title, description, link) VALUES (%s, %s, %s)",
                    (title, description, link))
        mysql.connection.commit()
        cur.close()
        return redirect('/admin/wellbeing-resources')

    @app.route('/admin/wellbeing-resources/delete/<int:id>')
    def delete_resource(id):
        if 'user_type' not in session or session['user_type'] != 'admin':
            return "Unauthorized", 403
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM wellbeing_resources WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect('/admin/wellbeing-resources')
    
    @app.route('/api/counseling/book', methods=['POST'])
    def api_book_counseling():
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        appointment_date = data.get('appointment_date')
        time_slot = data.get('time_slot')

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO appointments (name, email, appointment_date, time_slot) VALUES (%s, %s, %s, %s)
        """, (name, email, appointment_date, time_slot))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Appointment booked successfully!"}), 201


    @app.route('/api/grievances/view', methods=['GET'])
    def api_view_grievances():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM grievances ORDER BY submitted_at DESC")
        grievances = cur.fetchall()
        cur.close()
        return jsonify(grievances)

