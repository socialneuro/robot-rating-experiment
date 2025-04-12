import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Robot Rating Experiment", layout="centered")

# Load condition file
@st.cache_data
def load_conditions():
    df = pd.read_csv("robot_conditions.csv")
    return df

df_conditions = load_conditions()

# === Session Initialization ===
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "responses" not in st.session_state:
    st.session_state.responses = []
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "selected_images" not in st.session_state:
    st.session_state.selected_images = df_conditions.sample(n=21).reset_index(drop=True)

# === Page 1: Welcome with Info Sheet ===
if st.session_state.page == "welcome":
    st.title("Participant Information Sheet")

    st.markdown("""
**Research Title**: Perceptions of AI-Generated Robots  
**Researcher**: Professor Eric J. Vanman (e.vanman@psy.uq.edu.au), School of Psychology, University of Queensland

---

Thank you for your interest in this research study. Please read the following information carefully before deciding whether you would like to participate.

Your participation is completely voluntary. You may withdraw at any time without penalty and without affecting your relationship with The University of Queensland or the School of Psychology.

### What is this research about?
This study explores how people perceive AI-generated images of robots. The impressions you provide may help improve human-robot interaction and social robotics.

### What will I need to do?
- Provide basic demographic information  
- View a series of AI-generated images of robots  
- Make three ratings of each robot

The study takes ~5 minutes. You will be paid via Prolific after completion.

### Possible benefits:
Your input helps advance understanding of artificial agents and robot design.

### Risks:
No known risks. You can discontinue at any time.

### What happens with your data?
Your responses are anonymous and stored securely. Data may be published de-identified in academic journals or conferences.

### Withdrawal:
You may withdraw before submitting final responses. After submission, data cannot be removed as it is de-identified.

### Results:
You may email e.vanman@psy.uq.edu.au to request a summary of results after the project concludes.

### Ethics Contacts:
UQ Ethics Coordinator  
Phone: +61 7 3365 3924 / +61 7 3443 1656  
Email: humanethics@research.uq.edu.au
""")

    if st.button("I Agree, Continue to Study"):
        st.session_state.page = "demographics"
        st.rerun()

# === Page 2: Demographics ===
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

# === Page 3: Experiment ===
elif st.session_state.page == "experiment":
    if st.session_state.image_index < len(st.session_state.selected_images):
        row = st.session_state.selected_images.iloc[st.session_state.image_index]
        image = row['filename']
        st.header(f"Image {st.session_state.image_index + 1} of {len(st.session_state.selected_images)}")
        st.image(f"images/{image}", use_container_width=True)

        labels = [
            "1 - Not at all",
            "2 - A little",
            "3 - Moderately",
            "4 - A lot",
            "5 - Extremely"
        ]

        with st.form(f"form_{st.session_state.image_index}"):
            realistic = st.radio("How realistic does this robot look?", options=labels, index=2)
            friendly = st.radio("How friendly does this robot look?", options=labels, index=2)
            scary = st.radio("How scary does this robot look?", options=labels, index=2)
            submitted = st.form_submit_button("Submit Rating")

            if submitted:
                def extract_rating(choice): return int(choice.split(" ")[0])
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
        st.success("Thank you for participating!")
        df = pd.DataFrame(st.session_state.responses)
        os.makedirs("data", exist_ok=True)
        filename = f"data/{st.session_state.participant_id}_ratings.csv"
        df.to_csv(filename, index=False)
        st.write(f"Your data has been saved to `{filename}`.")
        st.balloons()
