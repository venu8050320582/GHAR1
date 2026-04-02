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
        password="venu1234",   # 🔴 change this
        database="ghar_db"
    )

# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        role = request.form['role']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (name, mobile, password, role) VALUES (%s,%s,%s,%s)",
                (name, mobile, password, role)
            )
            conn.commit()
            flash("Registration Successful", "success")
            return redirect(url_for('login'))
        except:
            flash("Mobile already registered", "danger")
        finally:
            conn.close()

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE mobile=%s", (mobile,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):

            if user['status'] == 'blocked':
                flash("Account Blocked", "danger")
                return redirect('/login')

            session['user_id'] = user['id']
            session['role'] = user['role']

            if user['role'] == 'Owner':
                return redirect('/owner/dashboard')
            elif user['role'] == 'Customer':
                return redirect('/search')

        flash("Invalid Login", "danger")

    return render_template('login.html')

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

    conn.close()
    return render_template('owner_dashboard.html', houses=houses)

# ---------------- ADD HOUSE ----------------
@app.route('/add_house', methods=['GET','POST'])
def add_house():
    if session.get('role') != 'Owner':
        return redirect('/login')

    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO houses (owner_id, area, city, rent, deposit, tenant_type)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            request.form['area'],
            request.form['city'],
            request.form['rent'],
            request.form['deposit'],
            request.form['tenant_type']
        ))

        conn.commit()
        conn.close()

        return redirect('/owner/dashboard')

    return render_template('add_house.html')

# ---------------- SEARCH ----------------
@app.route('/search', methods=['GET','POST'])
def search_house():
    houses = []

    if request.method == 'POST':
        city = request.form['city']

        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM houses WHERE city LIKE %s AND status='Available'",
            (f"%{city}%",)
        )

        houses = cur.fetchall()
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

    conn.close()

    return render_template('house_details.html', house=house, owner=owner)

# ---------------- COMPLAINT ----------------
@app.route('/complaint/<int:against_id>', methods=['GET','POST'])
def complaint(against_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO complaints (complainer_id,against_user_id,reason) VALUES (%s,%s,%s)",
            (session['user_id'], against_id, request.form['reason'])
        )

        conn.commit()
        conn.close()

        flash("Complaint submitted", "success")
        return redirect('/')

    return render_template('complaint.html')

# ---------------- TOGGLE USER STATUS ----------------
@app.route('/toggle_status/<int:id>')
def toggle_status(id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT status FROM users WHERE id=%s", (id,))
    user = cur.fetchone()

    if user:
        new_status = 'blocked' if user['status'] == 'active' else 'active'

        cur.execute(
            "UPDATE users SET status=%s WHERE id=%s",
            (new_status, id)
        )
        conn.commit()

    conn.close()
    return redirect('/')

# ---------------- START ----------------
if __name__ == '__main__':
    app.run()