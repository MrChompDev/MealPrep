import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "YOUR_EMAIL@gmail.com"
SMTP_PASS = "YOUR_APP_PASSWORD"

def send_order_email(to_email, order_id, eta, driver):
    subject = f"Your MealPrep Order #{order_id}"
    body = f"""
Thank you for your order!

Order ID: {order_id}
ETA: {eta}
Driver: {driver}

Track your order here:
http://localhost:8000/tracking
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email error:", e)
        return False
