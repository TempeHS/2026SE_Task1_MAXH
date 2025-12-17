import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3 as sql
from datetime import datetime, timedelta


def generate_otp():
    return str(secrets.randbelow(1000000)).zfill(6)


def store_otp(email, otp):
    try:
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()
        expiry = datetime.now() + timedelta(minutes=5)
        cur.execute(
            "insert or replace into twoFa (email, otp, expiry) values (?, ?, ?)",
            (email, otp, expiry.isoformat()),
        )
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(f"OTP storage error: {e}")
        return False


def verify_otp(email, otp):
    try:
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()
        cur.execute(" select otp, expiry from twoFa where email = ?", (email,))
        row = cur.fetchone()
        con.close()

        if not row:
            return False

        stored_otp, expiry = row
        expiry_time = datetime.fromisoformat(expiry)
        if datetime.now() > expiry_time:
            return False

        return stored_otp == otp

    except Exception as e:
        print(f"OTP verification error: {e}")
        return False


def send_otp(email, otp):
    try:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SENDER_EMAIL = "example.email"
        SENDER_PASSWORD = "example.passkey"

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = "your weaksecurity.com 2FA code"

        body = (
            f"Your verification code is: {otp}\n\nThis code will expire in 5 minutes."
        )
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False
