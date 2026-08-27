import streamlit as st
import smtplib
from email.message import EmailMessage

st.title("📧 Email File Sender")

# Gmail details
sender_email = "shaliniby143@gmail.com"
app_password = "kawn xrut bluf ypfq"

# Receiver Email
receiver_email = st.text_input("Enter Your Email")

# Multiple files
uploaded_files = st.file_uploader(
    "Upload PDF / Images / Documents",
    type=["pdf", "jpg", "jpeg", "png", "docx", "xlsx"],
    accept_multiple_files=True
)

# Message
message = st.text_area("Type your message")

# Send button
if st.button("Send Email"):

    if not receiver_email:
        st.warning("Please enter receiver email.")

    elif not uploaded_files and not message:
        st.warning("Please upload a file or type a message.")

    else:
        try:
            # Create email
            email = EmailMessage()

            email["From"] = sender_email
            email["To"] = receiver_email
            email["Subject"] = "Files and Message"

            # Message
            if message:
                email.set_content(message)
            else:
                email.set_content("Files are attached.")

            # Attach files
            if uploaded_files:
                for file in uploaded_files:

                    file_data = file.getvalue()
                    file_type = file.type

                    if "/" in file_type:
                        maintype, subtype = file_type.split("/", 1)
                    else:
                        maintype = "application"
                        subtype = "octet-stream"

                    email.add_attachment(
                        file_data,
                        maintype=maintype,
                        subtype=subtype,
                        filename=file.name
                    )

            # Send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

                smtp.login(
                    sender_email,
                    app_password
                )

                smtp.send_message(email)

            st.success("✅ Email sent successfully!")

        except Exception as e:
            st.error(f"❌ Error: {e}")