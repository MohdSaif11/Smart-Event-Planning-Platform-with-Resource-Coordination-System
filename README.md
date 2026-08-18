# Smart Event Planning Platform with Resource Coordination System

## 📌 Project Description

The **Smart Event Planning Platform with Resource Coordination System** is a web-based event management application developed using **Python and Django**. It provides a centralized platform for creating, managing, registering, and monitoring events.

The system provides separate functionalities for **administrators and users**. Administrators can manage events, categories, organizers, venues, registrations, participants, and attendance. Users can browse available events, view event details, register for events, add events to their wishlist, view their registrations, manage their profiles, and receive notifications.

The platform also includes **QR code-based event registration and attendance**, dashboard analytics, organizer management, and an **Event Assistant chatbot** that helps users with event-related queries. The main objective of the project is to reduce manual work and provide an organized digital solution for complete event planning and registration.

---

## 🛠️ Technologies Used

- Python
- Django 6.0.7
- Django REST Framework
- HTML5
- CSS3
- JavaScript
- Bootstrap
- SQLite
- QRCode
- Pillow
- Google GenAI
- Git
- GitHub

---

## ✨ Main Features

- Admin and User Authentication
- Admin Dashboard
- Event Creation and Management
- Category Management
- Organizer Management
- Venue Management
- User Event Registration
- QR Code Generation
- QR-Based Attendance Tracking
- Event Wishlist
- Event Notifications
- User Profile Management
- Event Status Tracking
- Registration Analytics
- Upcoming and Completed Events
- Event Assistant Chatbot

---

## 📂 Project Structure

```text
Smart-Event-Planning-Platform-with-Resource-Coordination-System/
│
├── Eventregistration/
│   │
│   ├── event/
│   │   ├── migrations/
│   │   ├── templates/
│   │   ├── static/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   └── tests.py
│   │
│   ├── Eventregistration/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── .gitignore
│
└── README.md

🚀 How to Run the Project

Follow these commands in this exact order when setting up the project on a new system.

1. Clone the Repository
Downloads the project from GitHub to your computer.
git clone https://github.com/MohdSaif11/Smart-Event-Planning-Platform-with-Resource-Coordination-System.git

2. Open the Project Folder
Moves the terminal into the project directory.
cd Smart-Event-Planning-Platform-with-Resource-Coordination-System

3. Create a Virtual Environment
Creates an isolated Python environment for the project's dependencies.
python -m venv env

4. Activate the Virtual Environment
Activates the environment so the project's Python packages are installed separately from your system Python.
Windows:
env\Scripts\activate

5. Upgrade pip
Updates Python's package manager before installing the project dependencies.
python -m pip install --upgrade pip

6. Install Project Dependencies
Installs all the Python/Django packages required by the project from requirements.txt.
pip install -r requirements.txt

7. Check the Django Project
Checks whether the Django configuration and project setup have any errors.
python manage.py check

8. Create Database Migrations
Creates migration files based on the models defined in models.py.
python manage.py makemigrations

9. Apply Database Migrations
Creates and updates the required database tables.
python manage.py migrate

10. Create an Admin Account
Creates a Django superuser who can access the Django administration panel.
python manage.py createsuperuser

11. Start the Development Server
Starts the Django application locally.
python manage.py runserver

Open the application at:
http://127.0.0.1:8000/

Django Admin:
http://127.0.0.1:8000/admin/

🔄 Useful Commands

After making changes to models.py, run:

python manage.py makemigrations
python manage.py migrate

To stop the development server:
CTRL + C

To start it again:
python manage.py runserver

To check migration status:
python manage.py showmigrations

To open the Django shell:
python manage.py shell

---

## 👨‍💻 Developed By

**Mohammed Saif R**  
**Infosys Springboard Virtual Internship 7.0**
