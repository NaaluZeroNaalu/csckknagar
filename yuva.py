import streamlit as st
import re
import smtplib
from email.mime.text import MIMEText



st.set_page_config(
    page_title="Student Enquiry Form",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Student Enquiry Form")
st.write("Welcome! Please fill in the enquiry form below.")


def send_email(name, email, phone, course, message):

    sender_email = "studentenquiryform@gmail.com"


    app_password = "wgzz lyae lpwb xdfo"

    
    receiver_email = "shreeyuva4444@gmail.com"

    body = f"""
New Student Enquiry Received

Name: {name}
Email: {email}
Phone: {phone}
Course: {course}

Message:
{message}
"""

    msg = MIMEText(body)

    msg["Subject"] = "New Student Enquiry"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(sender_email, app_password)

    server.sendmail(
        sender_email,
        receiver_email,
        msg.as_string()
    )

    server.quit()



with st.form("student_form"):

    name = st.text_input("Full Name")

    email = st.text_input("Email Address")

    phone = st.text_input("Phone Number")

    course = st.selectbox(
        "Course Interested In",
        [
            "Select Course",
            "B.E Electronics and Communication Engineering",
            "B.E Computer Science Engineering",
            "B.E Mechanical Engineering",
            "B.E Civil Engineering",
            "MBA"
        ]
    )

    message = st.text_area("Enquiry Message")

    submit = st.form_submit_button("Submit Enquiry")


if submit:

    if name.strip() == "":
        st.error("Please enter your full name.")

    elif not re.match(r"^[A-Za-z ]+$", name):
        st.error("Name should contain only letters and spaces.")

    elif email.strip() == "":
        st.error("Please enter your email address.")

    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        st.error("Please enter a valid email address.")

    elif not re.match(r"^\d{10}$", phone):
        st.error("Phone number must contain exactly 10 digits.")

    elif course == "Select Course":
        st.error("Please select a course.")

    elif message.strip() == "":
        st.error("Please enter your enquiry message.")

    else:

        try:

            send_email(
                name,
                email,
                phone,
                course,
                message
            )

            st.success("✅ Enquiry submitted successfully!")

            st.info("Your enquiry has been sent to your email.")

        except Exception as e:

            st.error(f"Email could not be sent: {e}")