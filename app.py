import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
from io import StringIO
from datetime import datetime

st.set_page_config(page_title="Robot Rating Experiment", layout="centered")

# Dummy image and rating logic skipped for brevity — assume responses are collected in st.session_state.responses

st.title("✅ Thank you for completing the study!")

if "responses" in st.session_state and st.session_state.responses:
    df = pd.DataFrame(st.session_state.responses)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    try:
        # Build the email
        msg = EmailMessage()
        msg["Subject"] = f"Robot Ratings Submission - {datetime.now().isoformat(timespec='seconds')}"
        msg["From"] = st.secrets["email"]["address"]
        msg["To"] = st.secrets["email"]["to"]
        msg.set_content("Attached is a participant's robot rating submission.")

        # Attach CSV
        msg.add_attachment(csv_data, subtype="csv", filename="robot_ratings.csv")

        # Send email using Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets["email"]["address"], st.secrets["email"]["password"])
            smtp.send_message(msg)

        st.success("✅ Your responses have been sent. You may now close this window.")
    except Exception as e:
        st.error(f"❌ Failed to send email. Error: {e}")
else:
    st.warning("⚠️ No responses were recorded.")

