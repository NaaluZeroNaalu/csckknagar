import smtplib
# import streamlit as st
from email.mime.multipart

# st.file_uploader("Upload")

import MIMEMultipart
from email.mime.text import MIMEText

import MIMEApplication
# from email.mime.appliction

sender_email = ("shalusri1603@gmail.com")
app_password = ("npss agqb ihry zphe")
receiver_email = ("shaluvisu160306@gmail.com")

Subject = ("Test email")
content = "Hello shalini.... This email was sent image and pdf Python."

msg.attach(MIMEText(content,"plain"))

msg = MIMEMultipart()
msg["Subject"] = "Test Email"
msg["From"] = sender_email
msg["To"] = receiver_email

file_path =c:\Users\SRI VIDHYA\Downloads\flower image.jpg

with open(file_path, "rb") as file:
    attachment = MIMEApplication(file.read(),Name = "sample.pdf")

attachment["content-Disposition"] = 'attachment;
filename = "sample.pdf"'
    msg.attach(attachment)

with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
    server.login(sender_email,app_password)
    server.send_message(msg)

print("Email sent sucessfully")

