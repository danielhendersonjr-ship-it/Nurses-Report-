import streamlit as st
from openai import OpenAI

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Nurse Notes AI",
    page_icon="🩺",
    layout="centered"
)

# -----------------------------
# Load API key
# -----------------------------
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("Missing OPENAI_API_KEY. Add it to Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# -----------------------------
# App title
# -----------------------------
st.title("🩺 Nurse Notes AI")
st.write("Create clean, professional nursing notes from patient details.")

st.divider()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Settings")

note_type = st.sidebar.selectbox(
    "Choose note type",
    [
        "SOAP Note",
        "Narrative Nursing Note",
        "Progress Note",
        "SBAR Report",
        "Discharge Note"
    ]
)

tone = st.sidebar.selectbox(
    "Documentation style",
    [
        "Professional and concise",
        "Detailed clinical",
        "Simple and clear"
    ]
)

# -----------------------------
# Patient information
# -----------------------------
st.header("Patient Information")

patient_name = st.text_input("Patient Name")
age = st.text_input("Age")
gender = st.selectbox(
    "Gender",
    ["Select", "Female", "Male", "Other", "Prefer not to say"]
)

# -----------------------------
# Clinical details
# -----------------------------
st.header("Clinical Details")

chief_complaint = st.text_area(
    "Chief Complaint",
    placeholder="Example: Patient reports shortness of breath and chest discomfort."
)

assessment = st.text_area(
    "Assessment Findings",
    placeholder="Example: Alert and oriented x4, skin warm and dry, lungs clear bilaterally."
)

vitals = st.text_area(
    "Vital Signs",
    placeholder="Example: BP 128/82, HR 88, RR 18, Temp 98.6°F, SpO2 97% RA."
)

interventions = st.text_area(
    "Nursing Interventions",
    placeholder="Example: Patient placed in semi-Fowler's position, oxygen administered per order."
)

patient_response = st.text_area(
    "Patient Response",
    placeholder="Example: Patient reports improvement after intervention."
)

additional_notes = st.text_area(
    "Additional Notes",
    placeholder="Add anything else relevant here."
)

# -----------------------------
# Prompt function
# -----------------------------
def build_prompt():
    return f"""
You are a professional nursing documentation assistant.

Create a {note_type} using a {tone.lower()} documentation style.

Important rules:
- Use only the information provided.
- Do not invent diagnoses, medications, orders, lab values, or treatments.
- Keep the note clinically appropriate.
- Make the documentation clear, organized, and professional.
- If information is missing, do not make it up.

Patient Information:
Patient Name: {patient_name}
Age: {age}
Gender: {gender}

Chief Complaint:
{chief_complaint}

Assessment Findings:
{assessment}

Vital Signs:
{vitals}

Nursing Interventions:
{interventions}

Patient Response:
{patient_response}

Additional Notes:
{additional_notes}
"""

# -----------------------------
# Generate button
# -----------------------------
st.divider()

if st.button("Generate Nursing Note", type="primary"):
    if not chief_complaint and not assessment and not interventions:
        st.warning("Please enter at least a chief complaint, assessment, or nursing intervention.")
        st.stop()

    with st.spinner("Generating note... because paperwork was apparently not painful enough already."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You help nurses create accurate, professional, "
                            "clinically appropriate documentation."
                        )
                    },
                    {
                        "role": "user",
                        "content": build_prompt()
                    }
                ],
                temperature=0.2
            )

            generated_note = response.choices[0].message.content

            st.success("Nursing note generated.")
            st.subheader("Generated Nursing Note")
            st.write(generated_note)

            st.download_button(
                label="Download Note as TXT",
                data=generated_note,
                file_name="nursing_note.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error("Something went wrong while generating the note.")
            st.code(str(e))

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption("Documentation support only. Review all notes before clinical use.")
