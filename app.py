from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Doctor
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doc_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('dashboard')
    return redirect('login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password'].encode('utf-8')
        role=request.form['role']
        doc_code = request.form.get('doc_code', '')

        if role == 'doctor' and doc_code != 'doc123':
            flash("Invalid teacher code.")
            return redirect('/register')

        if User.query.filter_by(email=email).first():
            flash("User already exists.")
            return redirect('/register')
        
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        if role == 'doctor' and doc_code == 'doc123':
           new_user = Doctor(
        email=email,
        password=hashed,
        role=role,
        all_time=['10', '11', '12', '14', '15', '16', '17', '18', '19', '20', '21', '22'],
        booked_time=[]
)
        else:
            new_user = User(email=email, password=hashed, role=role)



        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password'].encode('utf-8')
        role = request.form['role']

        user = User.query.filter_by(email=email, role=role).first()

        if user and bcrypt.checkpw(password, user.password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Login successful!")

            if user.role == 'doctor':
                return redirect('/doctor_dashboard')
            else:
                return redirect('/dashboard')
        else:
            flash("Invalid credentials or role.")
            return redirect('/login')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session or session.get('role') != 'patient':
        flash("Unauthorized access.")
        return redirect('/login')
    
    docs =Doctor.query.all()
    selected_doctor = None
    if request.method == 'POST':
        if 'doc_id' in request.form:
            doc_id = request.form['doc_id']
            selected_doctor = Doctor.query.get(int(doc_id))
        elif 'time' in request.form:
            time = request.form['time']
            doc_id = request.form['selected_doc_id']
            doctor = Doctor.query.get(int(doc_id))
            
            if time in doctor.booked_time:
                flash("Time slot already booked.")
            else:
                doctor.booked_time.append(time)
                db.session.commit()
                flash("Booking successful!")
                
                return redirect(url_for('dashboard', doc_id=doc_id))
    else:
        doc_id = request.args.get('doc_id')
        if doc_id:
            selected_doctor = Doctor.query.get(int(doc_id))
                

    return render_template('dashboard.html',docs=docs, selected_doctor=selected_doctor)




if __name__ == "__main__":  
    with app.app_context():
        db.create_all()
    app.run(debug=True)


