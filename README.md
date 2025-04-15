## 🚆 ** Project :**
Created a **Train Seat Reservation System** using **Flask (Python)** and **MongoDB** as a backend database.

This system:
- Lets **users login**
- Lets users **book or cancel train seats**
- Gives **admins control** to manage seats and users
- Stores all info in a database (so it works like a real app)

---

## 💡 Simple Explanation of Features

### ✅ 1. **Login System**
- Anyone can log in with just a **username**.
- If the username is new, it gets added to the database.
- If the username is "admin", the person gets **admin access**.

### 🧑‍💻 2. **User Dashboard**
Once logged in, users can:
- **See available seats**
- **Book seats** (if not already booked)
- **Cancel** their previously booked seats
- **Send access or help requests** to admin

### 🎫 3. **Seat Booking System**
- Seats are labeled like `S1`, `S2`, ... `S10`
- You keep track of:
  - If the seat is **booked or not**
  - Who **booked** the seat
- Users can select multiple seats and book them at once
- All bookings are stored in a collection called `bookings`

### ❌ 4. **Cancel Booking**
- A user can cancel any seat they've booked
- The seat becomes available again for others

### 👮‍♂️ 5. **Admin Dashboard**
If logged in as an admin:
- You can **view all bookings**
- You can **reset** all tickets (clear all bookings)
- You can **set total number of seats** (like adding more seats)
- You can **add new users** and decide if they are admins

### 📨 6. **User Requests**
- Users can **submit a request** (for anything: help, access, etc.)
- Admins can **respond to requests** and update their status

---

## 🧠 How the App Thinks (Behind the Scenes)

### 💾 Database (MongoDB)
You use collections (like tables):
- `users`: who is using the app (admin or not)
- `tickets`: information about all seats
- `bookings`: stores which user booked which seats
- `requests`: messages/requests sent to admin

### 🧠 Logic
Your app:
- Checks if seats are available before booking
- Prevents double booking
- Shows users **only their own bookings**
- Lets admins manage the entire system

---

## 🖼️ Example Workflow:
1. User visits the site → sees login page
2. Logs in → redirected to dashboard
3. Sees seats → selects and books some
4. Books saved in database
5. Can cancel later or send a request
6. Admin can reset seats, reply to requests, or manage users

---

### 🌟 Summary
You made a **mini train seat booking system** that:
- Has both **admin and user access**
- Can **book/cancel seats**
- Uses a **real database (MongoDB)**
- Has features like **requests, payment placeholder, and seat control**


---

## 🏗️ **1. Basic Setup**
```python
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
```
- You import necessary tools:
  - `Flask` is used to build the web app.
  - `render_template` is for HTML pages.
  - `request` handles form data.
  - `redirect` & `url_for` help with navigation.
  - `session` keeps users logged in.
  - `MongoClient` connects to MongoDB (your database).
  - `ObjectId` is used to work with MongoDB document IDs.

---

## ⚙️ **2. Initializing the App and Database**
```python
app = Flask(__name__)
app.secret_key = 'your_secret_key'
```
- You create the Flask app and give it a secret key to manage user sessions securely.

### Connecting to MongoDB:
```python
client = MongoClient("your_mongo_uri")
db = client['ticket_reservation_system']
```
- You connect to your **MongoDB database** named `ticket_reservation_system`.

### Collections (Tables):
```python
users_collection = db['users']
tickets_collection = db['tickets']
bookings_collection = db['bookings']
requests_collection = db['requests']
```
- These are like different tables in your database:
  - **users** → stores all users.
  - **tickets** → stores seat information.
  - **bookings** → stores user bookings.
  - **requests** → stores access or help requests.

---

## 👮‍♂️ **3. Default Data Setup**
```python
if users_collection.count_documents({'username': 'admin'}) == 0:
    users_collection.insert_one({'username': 'admin', 'is_admin': True})
```
- If there's no admin user, you create one.

```python
if tickets_collection.count_documents({}) == 0:
    total_seats = 10 
    seats = [{'block': f'S{i}', 'is_booked': False, 'booked_by': None} for i in range(1, total_seats + 1)]
    tickets_collection.insert_one({'total_seats': total_seats, 'seats': seats})
```
- If there are no seats, you create 10 default seats (`S1` to `S10`), all unbooked.

---

## 🔐 **4. Routes for the App**

### `/` → Login page
```python
@app.route('/')
def home():
    return render_template('login.html')
```

---

### `/login` → Logs in or registers user
```python
@app.route('/login', methods=['POST'])
def login():
    # Get username from form
    # If new user → add to DB
    # Store username & admin status in session
    return redirect(url_for('dashboard'))
```

---

### `/dashboard` → User or Admin dashboard
```python
@app.route('/dashboard')
def dashboard():
    if session['is_admin']:
        return render_template('admin_dashboard.html', bookings=bookings)
    return render_template('user_dashboard.html', tickets=tickets, bookings=bookings)
```
- If user is admin → show admin view
- Else → show user dashboard with tickets and their own bookings

---

### `/book` → User books seats
```python
@app.route('/book', methods=['POST'])
def book():
    # User selects seats
    # Check if selected seats are already booked
    # If not, update MongoDB to mark those as booked
    # Save booking record
    return redirect(url_for('dashboard'))
```

---

### `/payment/<booking_id>` → Placeholder for future payment
```python
@app.route('/payment/<booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    # Display payment page
    # (You haven't added actual payment logic here)
```

---

### `/cancel` → Cancel selected seats
```python
@app.route('/cancel', methods=['POST'])
def cancel():
    # User selects seats to cancel
    # Update seat status in MongoDB to unbooked
    # Remove those seats from the booking record
    return redirect(url_for('dashboard'))
```

---

## 👨‍💻 **5. Admin Features**

### `/admin/reset_tickets`
```python
@app.route('/admin/reset_tickets', methods=['POST'])
def reset_tickets():
    # Admin clears all bookings
```

### `/admin/set_tickets`
```python
@app.route('/admin/set_tickets', methods=['POST'])
def set_tickets():
    # Admin sets number of available seats
```

### `/admin/add_user`
```python
@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    # Admin can add a new user (admin or regular)
```

---

## 📨 **6. Access Requests**

### `/request` → User sends a request
```python
@app.route('/request', methods=['POST'])
def request_access():
    # User submits a timestamped request
```

### `/reply` → Admin replies to the request
```python
@app.route('/reply', methods=['POST'])
def reply_access():
    # Admin changes request status to "granted"
```

---

## 🚀 **7. Run the App**
```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## ✅ Summary

- **Users** can login, view available seats, book, cancel, and request access.
- **Admins** can view all bookings, reset seats, add users, and manage access requests.
- **MongoDB** is used to store all the data, and Flask handles the user interface and routing.

## OUTPUT

![Output 1](https://github.com/user-attachments/assets/db3ee974-1c77-45e6-a8b9-e8fe6e73cb8e)

![Output 2](https://github.com/user-attachments/assets/97e91923-f731-4467-8d3b-adf5a8119979)

https://github.com/user-attachments/assets/b8a79d20-95a2-4dc0-b8c9-18685033168d
