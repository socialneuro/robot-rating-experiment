import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Robot Rating Experiment", layout="centered")

@st.cache_data
def load_conditions():
    return pd.read_csv("robot_conditions.csv")

df_conditions = load_conditions()

if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "responses" not in st.session_state:
    st.session_state.responses = []
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "selected_images" not in st.session_state:
    st.session_state.selected_images = df_conditions.sample(frac=1).reset_index(drop=True)

# === Page 1: Participant Information Sheet ===
if st.session_state.page == "welcome":
    st.title("Participant Information Sheet")
    st.markdown("""
**Research Title**: Perceptions of AI-Generated Robots  
**Researcher**: Professor Eric J. Vanman (e.vanman@psy.uq.edu.au), School of Psychology, University of Queensland

Thank you for your interest in this research study. Please read the following information carefully before deciding whether you would like to participate.

Your participation is completely voluntary. You may withdraw at any time without penalty.

### What is this research about?
This study explores how people perceive AI-generated images of robots. The impressions you provide may help improve human-robot interaction and social robotics.

### What will I need to do?
- Provide basic demographic information  
- View a series of AI-generated images of robots  
- Make three ratings of each robot

The study takes ~5 minutes. You will be paid via Prolific after completion.

### Benefits and Risks
Your input helps improve robot design. No known risks. You can discontinue at any time.

### Data Privacy
Your responses are anonymous and stored securely. Data may be published in academic outlets in de-identified form.

### Contact
Questions or concerns? Email: e.vanman@psy.uq.edu.au  
Ethics: humanethics@research.uq.edu.au
""")

    if st.button("Continue"):
        st.session_state.page = "study_intro"
        st.rerun()

elif st.session_state.page == "study_intro":
    st.title("Welcome to our study")
    st.write("We are going to show you 42 images that were generated by AI of robots.")
    st.write("We would like you to consider how realistic you think each robot looks—does it look like something that could really exist in the real world?")
    st.write("In addition, we will ask you to rate how friendly and how scary the robot looks.")
    st.write("Your ratings will help us as we try to understand aspects of robot design.")

    if st.button("Continue to Demographics"):
        st.session_state.page = "demographics"
        st.rerun()

elif st.session_state.page == "demographics":
    st.title("Basic Information")
    age = st.number_input("What is your age?", min_value=10, max_value=120, step=1)
    gender = st.radio("What is your gender?", ["Female", "Male", "Non-binary", "Prefer not to say"])

    if st.button("Start the Study"):
        st.session_state.participant_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        st.session_state.age = age
        st.session_state.gender = gender
        st.session_state.page = "experiment"
        st.rerun()

elif st.session_state.page == "experiment":
    if st.session_state.image_index < len(st.session_state.selected_images):
        row = st.session_state.selected_images.iloc[st.session_state.image_index]
        image_path = f"images/{row['filename']}"
        st.header(f"Image {st.session_state.image_index + 1} of {len(st.session_state.selected_images)}")

        try:
            image = Image.open(image_path)
            new_height = 400
            aspect_ratio = image.width / image.height
            new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height))
            st.image(image, use_container_width=False)
        except Exception as e:
            st.error(f"Error loading image: {e}")

        labels = ["1 - Not at all", "2 - A little", "3 - Moderately", "4 - A lot", "5 - Extremely"]

        with st.form(f"form_{st.session_state.image_index}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                realistic = st.radio("Realistic", options=labels, index=None)
            with col2:
                friendly = st.radio("Friendly", options=labels, index=None)
            with col3:
                scary = st.radio("Scary", options=labels, index=None)
            submitted = st.form_submit_button("Submit Ratings")

            if submitted:
                def extract_rating(choice): return int(choice.split(" ")[0]) if choice else None
                st.session_state.responses.append({
                    "participant": st.session_state.participant_id,
                    "age": st.session_state.age,
                    "gender": st.session_state.gender,
                    "image": row['filename'],
                    "friendliness": row['friendliness'],
                    "type": row['type'],
                    "instance": row['instance'],
                    "realistic": extract_rating(realistic),
                    "friendly": extract_rating(friendly),
                    "scary": extract_rating(scary),
                    "timestamp": datetime.now().isoformat()
                })
                st.session_state.image_index += 1
                st.rerun()
    else:
        st.session_state.page = "thankyou"
        st.rerun()

elif st.session_state.page == "thankyou":
    st.title("Thank you!")
    st.write("You have completed the study.")
    st.markdown("Please use the following **Prolific completion code** to confirm your participation:")
    st.code("PROLIFIC-ROBOTS-0424", language="text")
    st.balloons()

    df = pd.DataFrame(st.session_state.responses)
    os.makedirs("data", exist_ok=True)
    filename = f"data/{st.session_state.participant_id}_ratings.csv"
    df.to_csv(filename, index=False)

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("robot-ratings-study-0dd9cb5a7dd7.json", scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Robot Ratings").worksheet("Sheet 1")
        sheet.append_rows(df.values.tolist())
        st.success("Data successfully saved to Google Sheets.")
    except Exception as e:
        st.error(f"Failed to upload to Google Sheets: {e}")
