#!/usr/bin/env python3
"""
Create sample doctors and hospitals for testing
"""
from app import app, db, User, Doctor, Hospital

with app.app_context():
    # Check if sample doctors already exist
    existing_doctors = Doctor.query.count()
    
    if existing_doctors > 0:
        print(f"✅ Sample data already exists ({existing_doctors} doctors found)")
    else:
        # Create sample hospitals first
        hospitals = [
            Hospital(
                user_id=1,  # Will be updated after user creation
                name="City General Hospital",
                address="123 Medical Center Drive, City, State 12345",
                phone="+1 (555) 123-4567",
                website="https://citygeneral.com",
                description="A leading multi-specialty hospital with state-of-the-art facilities.",
                emergency_number="+1 (555) 911-HELP"
            ),
            Hospital(
                user_id=1,
                name="Wellness Medical Center",
                address="456 Health Avenue, City, State 12345",
                phone="+1 (555) 234-5678",
                website="https://wellnessmedical.com",
                description="Comprehensive healthcare services with expert specialists.",
                emergency_number="+1 (555) 911-HELP"
            ),
            Hospital(
                user_id=1,
                name="Children's Medical Institute",
                address="789 Pediatric Way, City, State 12345",
                phone="+1 (555) 345-6789",
                website="https://childrensmedical.org",
                description="Specialized care for children and adolescents.",
                emergency_number="+1 (555) 911-HELP"
            )
        ]
        
        # Create sample users for hospitals
        hospital_users = []
        for i, hospital_data in enumerate([
            {"email": "cityhospital@test.com", "name": "City General Hospital"},
            {"email": "wellness@test.com", "name": "Wellness Medical Center"},
            {"email": "children@test.com", "name": "Children's Medical Institute"}
        ]):
            user = User(
                email=hospital_data["email"],
                user_type="hospital",
                is_verified=True
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            hospital_users.append(user)
        
        # Update hospital user_ids
        for i, hospital in enumerate(hospitals):
            hospital.user_id = hospital_users[i].id
        
        db.session.add_all(hospitals)
        db.session.flush()
        
        print("✅ Sample hospitals created!")
        
        # Create sample doctors
        doctors_data = [
            {
                "first_name": "Sarah",
                "last_name": "Johnson",
                "specialization": "Cardiology",
                "qualification": "MD, FACC",
                "experience": 15,
                "phone": "+1 (555) 111-2222",
                "hospital_id": 1,
                "bio": "Board-certified cardiologist with expertise in interventional cardiology and heart failure management.",
                "consultation_fee": 150.00,
                "is_available": True
            },
            {
                "first_name": "Michael",
                "last_name": "Chen",
                "specialization": "Neurology",
                "qualification": "MD, PhD",
                "experience": 12,
                "phone": "+1 (555) 222-3333",
                "hospital_id": 1,
                "bio": "Neurologist specializing in stroke, epilepsy, and movement disorders.",
                "consultation_fee": 175.00,
                "is_available": True
            },
            {
                "first_name": "Emily",
                "last_name": "Williams",
                "specialization": "Pediatrics",
                "qualification": "MD, FAAP",
                "experience": 10,
                "phone": "+1 (555) 333-4444",
                "hospital_id": 3,
                "bio": "Pediatrician with special interest in childhood development and nutrition.",
                "consultation_fee": 100.00,
                "is_available": True
            },
            {
                "first_name": "James",
                "last_name": "Martinez",
                "specialization": "Orthopedics",
                "qualification": "MD, FAAOS",
                "experience": 18,
                "phone": "+1 (555) 444-5555",
                "hospital_id": 2,
                "bio": "Orthopedic surgeon specializing in sports medicine and joint replacement.",
                "consultation_fee": 200.00,
                "is_available": True
            },
            {
                "first_name": "Lisa",
                "last_name": "Anderson",
                "specialization": "Dermatology",
                "qualification": "MD, FAAD",
                "experience": 8,
                "phone": "+1 (555) 555-6666",
                "hospital_id": 2,
                "bio": "Dermatologist specializing in skin cancer detection and cosmetic dermatology.",
                "consultation_fee": 125.00,
                "is_available": True
            },
            {
                "first_name": "Robert",
                "last_name": "Taylor",
                "specialization": "Internal Medicine",
                "qualification": "MD, FACP",
                "experience": 20,
                "phone": "+1 (555) 666-7777",
                "hospital_id": 1,
                "bio": "Internist with expertise in preventive medicine and chronic disease management.",
                "consultation_fee": 120.00,
                "is_available": True
            },
            {
                "first_name": "Jennifer",
                "last_name": "Brown",
                "specialization": "Gynecology",
                "qualification": "MD, FACOG",
                "experience": 14,
                "phone": "+1 (555) 777-8888",
                "hospital_id": 3,
                "bio": "Obstetrician-gynecologist providing comprehensive women's health services.",
                "consultation_fee": 130.00,
                "is_available": True
            },
            {
                "first_name": "David",
                "last_name": "Lee",
                "specialization": "Ophthalmology",
                "qualification": "MD, FACS",
                "experience": 11,
                "phone": "+1 (555) 888-9999",
                "hospital_id": 2,
                "bio": "Ophthalmologist specializing in cataract surgery and LASIK.",
                "consultation_fee": 175.00,
                "is_available": True
            },
            {
                "first_name": "Amanda",
                "last_name": "Garcia",
                "specialization": "Psychiatry",
                "qualification": "MD, MHA",
                "experience": 9,
                "phone": "+1 (555) 999-0000",
                "hospital_id": 1,
                "bio": "Psychiatrist specializing in anxiety, depression, and mood disorders.",
                "consultation_fee": 160.00,
                "is_available": True
            },
            {
                "first_name": "Christopher",
                "last_name": "Wilson",
                "specialization": "General Surgery",
                "qualification": "MD, FACS",
                "experience": 16,
                "phone": "+1 (555) 000-1111",
                "hospital_id": 2,
                "bio": "General surgeon with expertise in minimally invasive laparoscopic surgery.",
                "consultation_fee": 185.00,
                "is_available": True
            }
        ]
        
        # Create users and doctors
        for doc_data in doctors_data:
            # Create user for doctor
            user = User(
                email=f"doctor.{doc_data['first_name'].lower()}.{doc_data['last_name'].lower()}@test.com",
                user_type="doctor",
                is_verified=True
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            
            # Create doctor profile
            doctor = Doctor(
                user_id=user.id,
                first_name=doc_data["first_name"],
                last_name=doc_data["last_name"],
                specialization=doc_data["specialization"],
                qualification=doc_data["qualification"],
                experience=doc_data["experience"],
                phone=doc_data["phone"],
                hospital_id=doc_data["hospital_id"],
                bio=doc_data["bio"],
                consultation_fee=doc_data["consultation_fee"],
                is_available=doc_data["is_available"]
            )
            db.session.add(doctor)
        
        db.session.commit()
        
        print(f"✅ Sample data created successfully!")
        print(f"   - {len(hospitals)} hospitals")
        print(f"   - {len(doctors_data)} doctors")
        print(f"\n📋 Login credentials:")
        print(f"   Email: doctor.sarah.johnson@test.com")
        print(f"   Password: password123")
