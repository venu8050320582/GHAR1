from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ghar_secret_key_123"

# ---------------- MYSQL CONNECTION ----------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="venu1234",   # change if needed
        database="ghar_db"
    )

# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        role = request.form.get('role')
        password = generate_password_hash(request.form.get('password'))

        conn = get_db()
        cur = conn.cursor()

        try:
            # check if email already exists
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            existing_user = cur.fetchone()

            if existing_user:
                flash("Email already registered", "danger")
                return redirect('/register')

            cur.execute(
                "INSERT INTO users (name, mobile, email, password, role, status) VALUES (%s,%s,%s,%s,%s,%s)",
                (name, mobile, email, password, role, 'active')
            )
            conn.commit()

            flash("Registration Successful! Please login.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            print("ERROR:", e)
            flash("Registration failed", "danger")

        finally:
            cur.close()
            conn.close()

    return render_template('register.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        try:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

            if user:
                if user['status'] == 'blocked':
                    flash("Account is blocked", "danger")
                    return redirect('/login')

                if check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['role'] = user['role']

                    if user['role'] == 'Owner':
                        return redirect('/owner/dashboard')
                    else:
                        return redirect('/search')

            flash("Invalid email or password", "danger")

        except Exception as e:
            print("ERROR:", e)
            flash("Login error", "danger")

        finally:
            cur.close()
            conn.close()

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- OWNER DASHBOARD ----------------
@app.route('/owner/dashboard')
def owner_dashboard():
    if session.get('role') != 'Owner':
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM houses WHERE owner_id=%s", (session['user_id'],))
    houses = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('owner_dashboard.html', houses=houses)


# ---------------- ADD HOUSE ----------------
@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    if session.get('role') != 'Owner':
        return redirect('/login')

    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO houses (owner_id, area, city, rent, deposit, tenant_type, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            request.form.get('area'),
            request.form.get('city'),
            request.form.get('rent'),
            request.form.get('deposit'),
            request.form.get('tenant_type'),
            'Available'
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash("House added successfully", "success")
        return redirect('/owner/dashboard')

    return render_template('add_house.html')


# ---------------- SEARCH ----------------
@app.route('/search', methods=['GET', 'POST'])
def search_house():
    houses = []

    if request.method == 'POST':
        city = request.form.get('city')

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM houses WHERE city LIKE %s AND status='Available'",
            (f"%{city}%",)
        )

        houses = cur.fetchall()

        cur.close()
        conn.close()

    return render_template('search_house.html', houses=houses)


# ---------------- HOUSE DETAILS ----------------
@app.route('/house/<int:id>')
def house_details(id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM houses WHERE id=%s", (id,))
    house = cur.fetchone()

    cur.execute("SELECT id,name,mobile FROM users WHERE id=%s", (house['owner_id'],))
    owner = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('house_details.html', house=house, owner=owner)


# ---------------- COMPLAINT ----------------
@app.route('/complaint/<int:against_id>', methods=['GET', 'POST'])
def complaint(against_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO complaints (complainer_id, against_user_id, reason) VALUES (%s,%s,%s)",
            (session['user_id'], against_id, request.form.get('reason'))
        )

        conn.commit()
        cur.close()
        conn.close()

        flash("Complaint submitted", "success")
        return redirect('/')

    return render_template('complaint.html')


# ---------------- START ----------------
if __name__ == '__main__':
    app.run(debug=True)
