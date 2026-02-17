"""
MedVault Email Configuration
Configure your email settings here or use environment variables

📧 GMAIL SETUP INSTRUCTIONS:
1. Go to https://myaccount.google.com/
2. Enable 2-Factor Authentication (required)
3. Go to https://myaccount.google.com/apppasswords
4. Create a new app password for "MedVault"
5. Use that 16-character password in environment variables below
"""

import os

# Email Configuration
# Use environment variables for security (RECOMMENDED)
# Or configure manually below

# Environment variables (recommended):
# export MEDVAULT_EMAIL="your_email@gmail.com"
# export MEDVAULT_EMAIL_PASSWORD="xxxxxxxxxxxxxxxx"
# export MEDVAULT_EMAIL_SENDER="MedVault <noreply@medvault.com>"

# Get credentials from environment variables or use defaults
EMAIL_CONFIG = {
    'MAIL_SERVER': os.environ.get('MEDVAULT_MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(os.environ.get('MEDVAULT_MAIL_PORT', 587)),
    'MAIL_USE_TLS': os.environ.get('MEDVAULT_MAIL_USE_TLS', 'True').lower() == 'true',
    'MAIL_USE_SSL': os.environ.get('MEDVAULT_MAIL_USE_SSL', 'False').lower() == 'true',
    'MAIL_USERNAME': os.environ.get('MEDVAULT_EMAIL', ''),
    'MAIL_PASSWORD': os.environ.get('MEDVAULT_EMAIL_PASSWORD', ''),
    'MAIL_DEFAULT_SENDER': os.environ.get('MEDVAULT_EMAIL_SENDER', 'MedVault <noreply@medvault.com>'),
}

# Alternative SMTP Settings

# Outlook/Hotmail
# EMAIL_CONFIG = {
#     'MAIL_SERVER': 'smtp-mail.outlook.com',
#     'MAIL_PORT': 587,
#     'MAIL_USE_TLS': True,
#     'MAIL_USERNAME': 'your_email@outlook.com',
#     'MAIL_PASSWORD': 'your_password',
#     'MAIL_DEFAULT_SENDER': 'MedVault <your_email@outlook.com>',
# }

# Yahoo Mail
# EMAIL_CONFIG = {
#     'MAIL_SERVER': 'smtp.mail.yahoo.com',
#     'MAIL_PORT': 587,
#     'MAIL_USE_TLS': True,
#     'MAIL_USERNAME': 'your_email@yahoo.com',
#     'MAIL_PASSWORD': 'your_app_password',
#     'MAIL_DEFAULT_SENDER': 'MedVault <your_email@yahoo.com>',
# }

# Custom SMTP (e.g., your own mail server)
# EMAIL_CONFIG = {
#     'MAIL_SERVER': 'mail.yourdomain.com',
#     'MAIL_PORT': 587,  # or 465 for SSL
#     'MAIL_USE_TLS': True,
#     'MAIL_USERNAME': 'noreply@yourdomain.com',
#     'MAIL_PASSWORD': 'your_email_password',
#     'MAIL_DEFAULT_SENDER': 'MedVault <noreply@yourdomain.com>',
# }

# OTP Settings
OTP_CONFIG = {
    'OTP_LENGTH': 6,
    'OTP_EXPIRY_MINUTES': 10,
}

# Email templates
EMAIL_SUBJECTS = {
    'registration': 'Verify Your MedVault Account',
    'login': 'Your MedVault Login OTP',
    'password_reset': 'MedVault Password Reset OTP',
    'appointment_reminder': 'Appointment Reminder - MedVault',
}

def get_email_body(purpose, otp, user_email):
    """Generate email body based on purpose"""
    
    base_message = f"""
Dear MedVault User,

Your OTP (One-Time Password) for {purpose} is:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        OTP: {otp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This OTP is valid for 10 minutes. Please do not share this OTP with anyone.

If you did not request this OTP, please ignore this email.

Best regards,
MedVault Team
---
Healthcare Management System
    """
    
    return base_message

