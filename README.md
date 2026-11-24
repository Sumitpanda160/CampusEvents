# CampusEvents – College Event Management Portal

CampusEvents is a web-based College Event Management and Registration Portal that allows students to explore college events, register for events, and manage their registrations through a simple interface.

## 🚀 Features

- User Signup and Login
- Secure Password Hashing
- Browse Upcoming College Events
- Search Events by Name or Category
- Online Event Registration
- Duplicate Registration Prevention
- Event Capacity Management
- View My Registrations
- Cancel Event Registration
- Re-register for Cancelled Events
- Available Seat Tracking

## 🛠️ Technology Stack

**Frontend**
- HTML5
- CSS3
- JavaScript
- Jinja2

**Backend**
- Python
- Flask

**Database**
- MySQL

**Tools**
- VS Code
- Git
- GitHub

## 📁 Project Structure

```text
CampusEvents/
│
├── app.py
├── database.py
├── .gitignore
│
├── static/
│   └── css/
│       └── style.css
│
└── templates/
    ├── index.html
    ├── login.html
    ├── signup.html
    └── my_registrations.html
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sumitpanda160/CampusEvents.git
cd CampusEvents
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install Flask mysql-connector-python
```

### 4. Configure MySQL Database

- Start your MySQL server.
- Create a database named `college_events`.
- Create the required `users`, `events`, and `registrations` tables.
- Configure database credentials using environment variables if needed.

### 5. Configure Flask Secret Key

```bash
export SECRET_KEY="your-secret-key"
```

### 6. Run the Application

```bash
python3 app.py
```

Open your browser:

```text
http://127.0.0.1:5001
```

## 🔐 Security

- Passwords are stored using secure password hashing.
- Database credentials can be configured through environment variables.
- Flask session secret is configured through an environment variable.

## 🎯 Project Objective

The main objective of CampusEvents is to simplify college event management by providing a centralized platform for event discovery, student registration, and registration management.

## 👨‍💻 Developer

**Sumit Kumar Panda**

B.Tech – Information Technology

GitHub: [Sumitpanda160](https://github.com/Sumitpanda160)

---

⭐ If you find this project interesting, feel free to explore the repository!
