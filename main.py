from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = MongoClient("mongodb+srv://musab05ahs:pyKC3HZqfrHTjD16@cluster0.l8wgb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['ticket_reservation_system']
users_collection = db['users']
tickets_collection = db['tickets']
bookings_collection = db['bookings']
requests_collection = db['requests']

if users_collection.count_documents({'username': 'admin'}) == 0:
    users_collection.insert_one({'username': 'admin', 'is_admin': True})

if tickets_collection.count_documents({}) == 0:
    total_seats = 10 
    seats = [{'block': f'S{i}', 'is_booked': False, 'booked_by': None} for i in range(1, total_seats + 1)]
    tickets_collection.insert_one({'total_seats': total_seats, 'seats': seats})

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    user = users_collection.find_one({'username': username})
    if not user:
        users_collection.insert_one({'username': username, 'is_admin': False})
        user = users_collection.find_one({'username': username})
    session['username'] = username
    session['is_admin'] = user.get('is_admin', False)
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    if session.get('is_admin'):
        bookings = list(bookings_collection.find())
        return render_template('admin_dashboard.html', bookings=bookings)
    tickets = list(tickets_collection.find())
    bookings = list(bookings_collection.find({'username': session['username']}))
    return render_template('user_dashboard.html', tickets=tickets, bookings=bookings)

@app.route('/book', methods=['POST'])
def book():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    selected_seats = request.form.getlist('seats[]')
    if not selected_seats:
        return 'No seats selected'
    
    ticket_doc = tickets_collection.find_one({})
    if not ticket_doc:
        return 'No tickets available'
        
    for seat in ticket_doc['seats']:
        if seat['block'] in selected_seats and seat['is_booked']:
            return 'Some selected seats are already booked'
    
    result = tickets_collection.update_one(
        {'_id': ticket_doc['_id']},
        {
            '$set': {
                'seats.$[elem].is_booked': True,
                'seats.$[elem].booked_by': session['username']
            }
        },
        array_filters=[{'elem.block': {'$in': selected_seats}}]
    )
    
    if result.modified_count > 0:
        bookings_collection.insert_one({
            'username': session['username'],
            'seats': selected_seats
        })
        return redirect(url_for('dashboard'))
    return 'Selected seats are not available'

@app.route('/payment/<booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    if 'username' not in session:
        return redirect(url_for('home'))
    booking = bookings_collection.find_one({'_id': ObjectId(booking_id)})
    if request.method == 'POST':
        tickets_collection.update_one(
            {'_id': ObjectId(booking['ticket_id'])},
            {'$inc': {'available': -booking['num_tickets']}}
        )
        return redirect(url_for('dashboard'))
    return render_template('payment.html', booking=booking)

@app.route('/cancel', methods=['POST'])
def cancel():
    if 'username' not in session:
        return redirect(url_for('home'))
    booking_id = request.form['booking_id']
    booking = bookings_collection.find_one({'_id': ObjectId(booking_id)})
    if booking and booking['username'] == session['username']:
        seats_to_cancel = request.form.getlist('cancel_seats')
        if all(seat in booking['seats'] for seat in seats_to_cancel):
            
            for seat in seats_to_cancel:
                tickets_collection.update_one(
                    {'seats.block': seat},
                    {
                        '$set': {
                            'seats.$[elem].is_booked': False,
                            'seats.$[elem].booked_by': None
                        }
                    },
                    array_filters=[{'elem.block': seat}]
                )
            
            bookings_collection.update_one(
                {'_id': ObjectId(booking_id)},
                {'$pull': {'seats': {'$in': seats_to_cancel}}}
            )
            
            return redirect(url_for('dashboard'))
    return 'Invalid booking ID or number of tickets'

@app.route('/admin/reset_tickets', methods=['POST'])
def reset_tickets():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    tickets_collection.update_one(
        {},
        {
            '$set': {
                'seats.$[].is_booked': False,
                'seats.$[].booked_by': None
            }
        }
    )
    bookings_collection.delete_many({})
    return redirect(url_for('dashboard'))

@app.route('/admin/set_tickets', methods=['POST'])
def set_tickets():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))
    total_seats = int(request.form['total_tickets'])
    seats = [{'block': f'S{i}', 'is_booked': False, 'booked_by': None} for i in range(1, total_seats + 1)]
    tickets_collection.delete_many({})
    tickets_collection.insert_one({'total_seats': total_seats, 'seats': seats})
    return redirect(url_for('dashboard'))

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        is_admin = 'is_admin' in request.form
        if users_collection.find_one({'username': username}):
            return 'User already exists'
        users_collection.insert_one({'username': username, 'is_admin': is_admin})
        return 'User added successfully'
    return render_template('add_user.html')

@app.route('/request', methods=['POST'])
def request_access():
    if 'username' not in session:
        return redirect(url_for('home'))
    timestamp = request.form['timestamp']
    requests_collection.insert_one({
        'username': session['username'], 
        'timestamp': timestamp,
        'status': 'pending'
    })
    return 'Request sent'

@app.route('/reply', methods=['POST'])
def reply_access():
    if 'username' not in session:
        return redirect(url_for('home'))
    requester = request.form['requester']
    requests_collection.update_one(
        {'username': requester, 'status': 'pending'},
        {'$set': {'status': 'granted'}}
    )
    return 'Reply sent'

if __name__ == '__main__':
    app.run(debug=True, port=5000)