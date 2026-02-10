"""
MedVault: Appointment Booking & Medical Records Management System
Senior Project Implementation with Professional Design
"""

from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import random
import string
import os

# Configuration
app = Flask(__name__)
app.secret_key = 'medvault_secret_key_2024'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medvault.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Configure with your email
app.config['MAIL_PASSWORD'] = 'your_app_password'      # Configure with app password
app.config['MAIL_DEFAULT_SENDER'] = 'MedVault <noreply@medvault.com>'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
mail = Mail(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """Base User Model for Patients, Doctors, and Hospitals"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # patient, doctor, hospital
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    patient = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    hospital = db.relationship('Hospital', backref='user', uselist=False, cascade='all, delete-orphan')
    otps = db.relationship('OTP', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class OTP(db.Model):
    """OTP Verification Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # registration, login, reset
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

class Patient(db.Model):
    """Patient Profile Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='patient', lazy='dynamic')

class Doctor(db.Model):
    """Doctor Profile Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    experience = db.Column(db.Integer, default=0)  # Years of experience
    phone = db.Column(db.String(20), nullable=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    consultation_fee = db.Column(db.Float, default=0.0)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    hospital = db.relationship('Hospital', backref='doctors')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    availability = db.relationship('DoctorAvailability', backref='doctor', cascade='all, delete-orphan')

class Hospital(db.Model):
    """Hospital/Clinic Profile Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logo = db.Column(db.String(200), nullable=True)
    emergency_number = db.Column(db.String(20), nullable=True)
    
    # Relationships
    departments = db.relationship('Department', backref='hospital', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='hospital', lazy='dynamic')

class Department(db.Model):
    """Hospital Departments"""
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

class DoctorAvailability(db.Model):
    """Doctor Availability Schedule"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

class Appointment(db.Model):
    """Appointment Booking Model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=True)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MedicalRecord(db.Model):
    """Medical Records Storage"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)  # prescription, lab_result, scan, report
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(300), nullable=True)
    record_date = db.Column(db.Date, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_shared = db.Column(db.Boolean, default=False)
    shared_with = db.Column(db.String(500), nullable=True)  # Comma-separated doctor IDs

class Prescription(db.Model):
    """Prescription Model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)
    medications = db.Column(db.Text, nullable=False)  # JSON string of medications
    diagnosis = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    prescribed_date = db.Column(db.Date, default=datetime.utcnow)
    valid_until = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    """Notification Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # appointment, reminder, alert
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== HELPER FUNCTIONS ====================

def generate_otp(length=6):
    """Generate random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email, otp, purpose):
    """Send OTP via email"""
    subject = f"MedVault - OTP for {purpose.title()}"
    body = f"""
    Your OTP for {purpose.title()} on MedVault is: {otp}
    
    This OTP is valid for 10 minutes. Please do not share this OTP with anyone.
    
    If you did not request this, please ignore this email.
    
    Best regards,
    MedVault Team
    """
    try:
        msg = Message(subject, recipients=[email], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def create_notification(user_id, title, message, notif_type='info'):
    """Create a notification for user"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notif_type
    )
    db.session.add(notification)
    db.session.commit()

# ==================== MIDDLEWARE ====================

@app.before_request
def check_user_verified():
    """Check if logged-in user is verified, redirect to login if not"""
    if 'user_id' in session:
        user = User.query.get(session.get('user_id'))
        if user and not user.is_verified:
            session.clear()
            flash('Your email has not been verified. Please log in to continue.', 'warning')
            return redirect(url_for('login'))

# ==================== ROUTES ====================

@app.route('/')
def welcome():
    """Welcome/Landing Page"""
    return render_template('welcome.html')

@app.route('/about')
def about():
    """About Page"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact Page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        flash(f'Thank you, {name}! Your message has been sent. We will contact you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login with Email OTP"""
    if 'user_id' in session:
        user = User.query.get(session.get('user_id'))
        if user and user.is_verified:
            user_type = session.get('user_type')
            if user_type == 'patient':
                return redirect(url_for('patient_dashboard'))
            elif user_type == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user_type == 'hospital':
                return redirect(url_for('hospital_dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email', '')
        
        if action == 'send_otp':
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash('No account found with this email. Please register first.', 'error')
                return redirect(url_for('register'))
            
            # Generate and send OTP
            otp_code = generate_otp()
            otp = OTP(
                user_id=user.id,
                otp_code=otp_code,
                purpose='login',
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            db.session.add(otp)
            db.session.commit()
            
            # Send OTP email (store demo OTP for development/testing)
            sent = send_otp_email(email, otp_code, 'login')
            session['demo_otp'] = otp_code
            if sent:
                flash('OTP sent to your email. Please enter it below.', 'info')
            else:
                # Demo mode - show OTP
                flash(f'OTP sent (Demo: Your OTP is {otp_code})', 'info')

            session['login_email'] = email
            session['login_user_id'] = user.id
            session['otp_purpose'] = 'login'

            return redirect(url_for('verify_otp'))
        
        elif action == 'verify_otp':
            otp_code = request.form.get('otp', '').strip()
            email = session.get('login_email')
            login_user_id = session.get('login_user_id')
            
            if not login_user_id:
                flash('Session expired. Please log in again.', 'error')
                return redirect(url_for('login'))
            
            user = User.query.get(login_user_id)
            otp_record = OTP.query.filter_by(
                user_id=login_user_id,
                otp_code=otp_code,
                purpose='login',
                is_used=False
            ).order_by(OTP.created_at.desc()).first()
            
            if otp_record and otp_record.is_valid():
                otp_record.is_used = True
                user.is_verified = True
                user.last_login = datetime.utcnow()
                db.session.commit()
                # Clear demo OTP after successful login verification
                session.pop('demo_otp', None)

                session.clear()
                session['user_id'] = user.id
                session['user_type'] = user.user_type
                session['email'] = user.email
                
                flash('Login successful! Welcome to MedVault.', 'success')
                
                # Redirect based on user type
                if user.user_type == 'patient':
                    return redirect(url_for('patient_dashboard'))
                elif user.user_type == 'doctor':
                    return redirect(url_for('doctor_dashboard'))
                elif user.user_type == 'hospital':
                    return redirect(url_for('hospital_dashboard'))
            else:
                flash('Invalid or expired OTP. Please try again.', 'error')
                return redirect(url_for('verify_otp'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration Page"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'send_otp':
            email = request.form.get('email')
            user_type = request.form.get('user_type')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validation
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('register'))
            
            if len(password) < 8:
                flash('Password must be at least 8 characters.', 'error')
                return redirect(url_for('register'))
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered. Please login.', 'error')
                return redirect(url_for('login'))
            
            # Create temporary user
            temp_user = User(
                email=email,
                user_type=user_type,
                is_verified=False
            )
            temp_user.set_password(password)
            db.session.add(temp_user)
            db.session.commit()
            
            # Generate OTP
            otp_code = generate_otp()
            otp = OTP(
                user_id=temp_user.id,
                otp_code=otp_code,
                purpose='registration',
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            db.session.add(otp)
            db.session.commit()
            
            # Send OTP email (in dev we also keep OTP in session for demo)
            sent = send_otp_email(email, otp_code, 'registration')
            session['demo_otp'] = otp_code
            if sent:
                flash('OTP sent to your email. Please verify to complete registration.', 'info')
            else:
                flash(f'OTP sent (Demo: Your OTP is {otp_code})', 'info')

            session['register_user_id'] = temp_user.id
            session['register_email'] = email
            session['otp_purpose'] = 'registration'

            return redirect(url_for('verify_otp'))
    
    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    """Email/OTP Verification Page"""
    otp_purpose = session.get('otp_purpose')
    
    if request.method == 'POST':
        otp_code = request.form.get('otp', '').strip()
        
        if otp_purpose == 'registration':
            user_id = session.get('register_user_id')
            email = session.get('register_email')
            
            if not user_id:
                flash('Session expired. Please try registration again.', 'error')
                return redirect(url_for('register'))
            
            otp_record = OTP.query.filter_by(
                user_id=user_id,
                otp_code=otp_code,
                purpose='registration',
                is_used=False
            ).order_by(OTP.created_at.desc()).first()
            
            if otp_record and otp_record.is_valid():
                otp_record.is_used = True
                user = User.query.get(user_id)
                user.is_verified = True
                db.session.commit()

                # Clear demo OTP after successful verification
                session.pop('demo_otp', None)

                flash('Email verified successfully! Please complete your profile.', 'success')
                session['user_id'] = user.id
                session['user_type'] = user.user_type
                session['email'] = user.email
                session.pop('register_user_id', None)
                session.pop('register_email', None)
                session.pop('otp_purpose', None)

                # Redirect to profile completion based on user type
                if user.user_type == 'patient':
                    return redirect(url_for('complete_patient_profile'))
                elif user.user_type == 'doctor':
                    return redirect(url_for('complete_doctor_profile'))
                elif user.user_type == 'hospital':
                    return redirect(url_for('complete_hospital_profile'))
            else:
                flash('Invalid or expired OTP. Please try again.', 'error')
                return redirect(url_for('verify_otp'))
        
        elif otp_purpose == 'login':
            login_user_id = session.get('login_user_id')
            
            if not login_user_id:
                flash('Session expired. Please log in again.', 'error')
                return redirect(url_for('login'))
            
            user = User.query.get(login_user_id)
            otp_record = OTP.query.filter_by(
                user_id=login_user_id,
                otp_code=otp_code,
                purpose='login',
                is_used=False
            ).order_by(OTP.created_at.desc()).first()
            
            if otp_record and otp_record.is_valid():
                otp_record.is_used = True
                user.is_verified = True
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                session.clear()
                session['user_id'] = user.id
                session['user_type'] = user.user_type
                session['email'] = user.email
                
                flash('Login successful! Welcome to MedVault.', 'success')
                
                # Redirect based on user type
                if user.user_type == 'patient':
                    return redirect(url_for('patient_dashboard'))
                elif user.user_type == 'doctor':
                    return redirect(url_for('doctor_dashboard'))
                elif user.user_type == 'hospital':
                    return redirect(url_for('hospital_dashboard'))
            else:
                flash('Invalid or expired OTP. Please try again.', 'error')
                return redirect(url_for('verify_otp'))
    
    email = session.get('register_email') or session.get('login_email', '')
    demo_otp = session.get('demo_otp')
    return render_template('verify_otp.html', email=email, purpose=otp_purpose, demo_otp=demo_otp)

@app.route('/complete_patient_profile', methods=['GET', 'POST'])
def complete_patient_profile():
    """Complete Patient Profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    patient = Patient.query.filter_by(user_id=user.id).first()
    
    if request.method == 'POST':
        # Create patient record if it doesn't exist
        if not patient:
            patient = Patient(user_id=user.id)
            db.session.add(patient)
        
        # Use 'or' to handle both None and empty string cases
        patient.first_name = request.form.get('first_name') or 'User'
        patient.last_name = request.form.get('last_name') or ''
        patient.phone = request.form.get('phone') or ''
        patient.address = request.form.get('address') or ''
        patient.blood_group = request.form.get('blood_group') or ''
        patient.gender = request.form.get('gender') or ''
        
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            patient.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        patient.allergies = request.form.get('allergies') or ''
        patient.emergency_contact = request.form.get('emergency_contact') or ''
        
        db.session.commit()
        flash('Profile completed successfully!', 'success')
        return redirect(url_for('patient_dashboard'))
    
    return render_template('complete_profile.html', user_type='patient', patient=patient)

@app.route('/complete_doctor_profile', methods=['GET', 'POST'])
def complete_doctor_profile():
    """Complete Doctor Profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    
    if not doctor:
        doctor = Doctor(user_id=user.id)
        db.session.add(doctor)
        db.session.commit()
    
    hospitals = Hospital.query.all()
    
    if request.method == 'POST':
        doctor.first_name = request.form.get('first_name')
        doctor.last_name = request.form.get('last_name')
        doctor.specialization = request.form.get('specialization')
        doctor.qualification = request.form.get('qualification')
        doctor.experience = int(request.form.get('experience', 0))
        doctor.phone = request.form.get('phone')
        doctor.hospital_id = request.form.get('hospital_id')
        doctor.bio = request.form.get('bio')
        doctor.consultation_fee = float(request.form.get('consultation_fee', 0))
        
        db.session.commit()
        flash('Profile completed successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('complete_profile.html', user_type='doctor', doctor=doctor, hospitals=hospitals)

@app.route('/complete_hospital_profile', methods=['GET', 'POST'])
def complete_hospital_profile():
    """Complete Hospital Profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hospital = Hospital.query.filter_by(user_id=user.id).first()
    
    if not hospital:
        hospital = Hospital(user_id=user.id)
        db.session.add(hospital)
        db.session.commit()
    
    if request.method == 'POST':
        hospital.name = request.form.get('name')
        hospital.address = request.form.get('address')
        hospital.phone = request.form.get('phone')
        hospital.website = request.form.get('website')
        hospital.description = request.form.get('description')
        hospital.emergency_number = request.form.get('emergency_number')
        
        db.session.commit()
        flash('Profile completed successfully!', 'success')
        return redirect(url_for('hospital_dashboard'))
    
    return render_template('complete_profile.html', user_type='hospital', hospital=hospital)

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('welcome'))

@app.route('/patient/dashboard')
def patient_dashboard():
    """Patient Dashboard"""
    if session.get('user_type') != 'patient':
        return redirect(url_for('login'))
    
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    # If patient profile doesn't exist, redirect to complete it
    if not patient:
        flash('Please complete your patient profile first.', 'warning')
        return redirect(url_for('complete_patient_profile'))
    
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
        Appointment.appointment_date.desc()
    ).limit(5).all()
    records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(
        MedicalRecord.created_at.desc()
    ).limit(5).all()
    notifications = Notification.query.filter_by(
        user_id=session['user_id'], is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('patient_dashboard.html', 
                         patient=patient, 
                         appointments=appointments, 
                         records=records,
                         notifications=notifications)

@app.route('/doctor/dashboard')
def doctor_dashboard():
    """Doctor Dashboard"""
    if session.get('user_type') != 'doctor':
        return redirect(url_for('login'))
    
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    # If doctor profile doesn't exist, redirect to complete it
    if not doctor:
        flash('Please complete your doctor profile first.', 'warning')
        return redirect(url_for('complete_doctor_profile'))
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(
        Appointment.appointment_date.desc()
    ).limit(10).all()
    notifications = Notification.query.filter_by(
        user_id=session['user_id'], is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    today = datetime.now().date()
    today_appointments = [a for a in appointments if a.appointment_date == today]
    
    return render_template('doctor_dashboard.html',
                         doctor=doctor,
                         appointments=appointments,
                         today_appointments=today_appointments,
                         notifications=notifications)

@app.route('/hospital/dashboard')
def hospital_dashboard():
    """Hospital Dashboard"""
    if session.get('user_type') != 'hospital':
        return redirect(url_for('login'))
    
    hospital = Hospital.query.filter_by(user_id=session['user_id']).first()
    
    # If hospital profile doesn't exist, redirect to complete it
    if not hospital:
        flash('Please complete your hospital profile first.', 'warning')
        return redirect(url_for('complete_hospital_profile'))
    
    doctors = Doctor.query.filter_by(hospital_id=hospital.id).all()
    appointments = Appointment.query.filter_by(hospital_id=hospital.id).order_by(
        Appointment.appointment_date.desc()
    ).limit(10).all()
    notifications = Notification.query.filter_by(
        user_id=session['user_id'], is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('hospital_dashboard.html',
                         hospital=hospital,
                         doctors=doctors,
                         appointments=appointments,
                         notifications=notifications)

@app.route('/appointments')
def appointments():
    """Appointments Page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_type = session.get('user_type')
    
    if user_type == 'patient':
        patient = Patient.query.filter_by(user_id=session['user_id']).first()
        if not patient:
            flash('Please complete your profile first.', 'warning')
            return redirect(url_for('complete_patient_profile'))
        appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
            Appointment.appointment_date.desc()
        ).all()
        doctors = Doctor.query.filter_by(is_available=True).all()
        return render_template('appointments.html', appointments=appointments, doctors=doctors, mode='patient')
    
    elif user_type == 'doctor':
        doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
        if not doctor:
            flash('Please complete your profile first.', 'warning')
            return redirect(url_for('complete_doctor_profile'))
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(
            Appointment.appointment_date.desc()
        ).all()
        return render_template('appointments.html', appointments=appointments, mode='doctor')
    
    elif user_type == 'hospital':
        hospital = Hospital.query.filter_by(user_id=session['user_id']).first()
        if not hospital:
            flash('Please complete your profile first.', 'warning')
            return redirect(url_for('complete_hospital_profile'))
        appointments = Appointment.query.filter_by(hospital_id=hospital.id).order_by(
            Appointment.appointment_date.desc()
        ).all()
        return render_template('appointments.html', appointments=appointments, mode='hospital')
    
    return redirect(url_for('welcome'))

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    """Book New Appointment"""
    if session.get('user_type') != 'patient':
        return redirect(url_for('login'))
    
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    if not patient:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('complete_patient_profile'))
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        reason = request.form.get('reason')
        
        doctor = Doctor.query.get(doctor_id)
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            hospital_id=doctor.hospital_id,
            appointment_date=datetime.strptime(appointment_date, '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(appointment_time, '%H:%M').time(),
            reason=reason,
            status='pending'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Create notification for doctor
        create_notification(
            doctor.user_id,
            'New Appointment',
            f'New appointment request from {patient.first_name} {patient.last_name} on {appointment_date}',
            'appointment'
        )
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments'))
    
    doctors = Doctor.query.filter_by(is_available=True).all()
    return render_template('book_appointment.html', doctors=doctors)

@app.route('/appointment/action/<int:appointment_id>/<action>')
def appointment_action(appointment_id, action):
    """Accept or Reject Appointment"""
    if session.get('user_type') != 'doctor':
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get(appointment_id)
    
    if action == 'accept':
        appointment.status = 'confirmed'
        message = 'Appointment accepted!'
    elif action == 'reject':
        appointment.status = 'cancelled'
        message = 'Appointment rejected!'
    else:
        appointment.status = 'completed'
        message = 'Appointment marked as completed!'
    
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('appointments'))

@app.route('/records')
def medical_records():
    """Medical Records Page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_type = session.get('user_type')
    
    if user_type == 'patient':
        patient = Patient.query.filter_by(user_id=session['user_id']).first()
        records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(
            MedicalRecord.created_at.desc()
        ).all()
        return render_template('medical_records.html', records=records, mode='patient')
    
    elif user_type in ['doctor', 'hospital']:
        # For doctors/hospitals, show shared records or search
        records = []
        if user_type == 'doctor':
            doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
            records = MedicalRecord.query.filter(
                MedicalRecord.shared_with.contains(str(doctor.id))
            ).all()
        return render_template('medical_records.html', records=records, mode=user_type)
    
    return redirect(url_for('welcome'))

@app.route('/upload_record', methods=['GET', 'POST'])
def upload_record():
    """Upload Medical Record"""
    if session.get('user_type') != 'patient':
        return redirect(url_for('login'))
    
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    if not patient:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('complete_patient_profile'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        record_type = request.form.get('record_type')
        description = request.form.get('description')
        file = request.files.get('file')
        
        file_path = None
        if file and file.filename:
            filename = secure_filename(f"{patient.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = filename
        
        record = MedicalRecord(
            patient_id=patient.id,
            record_type=record_type,
            title=title,
            description=description,
            file_path=file_path,
            uploaded_by=session['user_id']
        )
        
        db.session.add(record)
        db.session.commit()
        
        flash('Medical record uploaded successfully!', 'success')
        return redirect(url_for('medical_records'))
    
    return render_template('upload_record.html')

@app.route('/download_record/<int:record_id>')
def download_record(record_id):
    """Download Medical Record"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    record = MedicalRecord.query.get(record_id)
    
    if record.file_path:
        return send_from_directory(app.config['UPLOAD_FOLDER'], record.file_path, as_attachment=True)
    
    flash('File not found.', 'error')
    return redirect(url_for('medical_records'))

@app.route('/search_doctors')
def search_doctors():
    """Search for Doctors"""
    specialization = request.args.get('specialization')
    location = request.args.get('location')

    query = Doctor.query.filter_by(is_available=True)

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))

    doctors = query.all()
    return render_template('search_doctors.html', doctors=doctors)

@app.route('/doctor/patients')
def doctor_patients():
    """Doctor's Patients List"""
    if session.get('user_type') != 'doctor':
        return redirect(url_for('login'))

    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    if not doctor:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('complete_doctor_profile'))

    # Get unique patients who have appointments with this doctor
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    patient_ids = list(set([appt.patient_id for appt in appointments]))
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []

    # Calculate ages
    for patient in patients:
        if patient.date_of_birth:
            patient.age = datetime.now().year - patient.date_of_birth.year
        else:
            patient.age = None

    return render_template('doctor_patients.html', doctor=doctor, patients=patients)

@app.route('/hospital/patients')
def hospital_patients():
    """Hospital's Patients List"""
    if session.get('user_type') != 'hospital':
        return redirect(url_for('login'))

    hospital = Hospital.query.filter_by(user_id=session['user_id']).first()
    if not hospital:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('complete_hospital_profile'))

    # Get unique patients who have appointments at this hospital
    appointments = Appointment.query.filter_by(hospital_id=hospital.id).all()
    patient_ids = list(set([appt.patient_id for appt in appointments]))
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []

    # Calculate ages
    for patient in patients:
        if patient.date_of_birth:
            patient.age = datetime.now().year - patient.date_of_birth.year
        else:
            patient.age = None

    return render_template('hospital_patients.html', hospital=hospital, patients=patients)

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error='Internal server error'), 500

# Initialize Database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

