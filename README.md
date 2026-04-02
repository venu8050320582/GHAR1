🏠 GHAR – House Rental Web Application

---

📌 Project Overview
GHAR is a web-based application that allows users to search, list, and manage rental properties.
It connects house owners and tenants in a simple and efficient way.

---

🚀 Features

* User Registration & Login (Owner / Customer)
* Add House Listings (Owner)
* Search Houses by City (Customer)
* View Property Details
* Complaint System
* User Status Control (Active / Blocked)

---

🛠️ Tech Stack

* Backend: Python (Flask)
* Frontend: HTML, CSS
* Database: MySQL
* Deployment: Render
* Version Control: GitHub

---

📁 Project Structure

project/
│
├── app.py
├── requirements.txt
├── Procfile
├── templates/
├── static/

---

⚙️ Installation (Local Setup)

1. Clone the repository:
   git clone https://github.com/your-username/ghar-project.git

2. Navigate to project folder:
   cd ghar-project

3. Install dependencies:
   pip install -r requirements.txt

4. Setup MySQL database:
   CREATE DATABASE ghar_db;

5. Run the application:
   python app.py

6. Open in browser:
   http://127.0.0.1:5000/

---

🌐 Deployment
The application is deployed using:

* Render (for hosting)
* Railway (for MySQL database)

---

🔑 Environment Variables (for production)

Update database connection in app.py:

host = YOUR_HOST
user = YOUR_USER
password = YOUR_PASSWORD
database = YOUR_DB

---

⚠️ Notes

* Ensure MySQL server is running
* Update DB credentials before running
* Data is stored permanently in MySQL

---

📌 Future Enhancements

* Add house images upload
* Payment integration
* Mobile responsive UI
* Notification system
* Ratings & Reviews

---

👨‍💻 Author
Venu

---

📜 License
This project is for educational purposes.
