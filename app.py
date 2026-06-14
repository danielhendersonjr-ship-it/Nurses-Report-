from datetime import datetime

import streamlit as st
from openai import OpenAI
from PIL import Image
from streamlit_drawable_canvas import st_canvas


st.set_page_config(
    page_title="Nurse Notes AI",
    page_icon="🩺",
    layout="wide"
)


def initialize_state():
    defaults = {
        "raw_event_note": "",
        "ai_note": "",
        "template_name": "ICU Report Sheet",
        "saved_drafts": [],
        "uploaded_report_image": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_openai_client():
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Missing OPENAI_API_KEY. Add it in Streamlit app secrets.")
        st.stop()

    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def create_nursing_note(raw_text, template_name, note_style):
    client = get_openai_client()

    instructions = f"""
You are helping create a professional nursing note draft.

Rules:
- This is for demo or non-PHI use only.
- Do not include or request patient identifiers.
- Do not invent facts.
- Use only the supplied information.
- Use objective nursing documentation language.
- Do not diagnose.
- Do not give medical advice.
- List missing details clearly.
- Remind the nurse to review and approve the note.

Report sheet type:
{template_name}

Preferred note style:
{note_style}

Format:

Date/Time:
Situation/Event:
Assessment:
Interventions:
Patient Response:
Notifications:
Follow-Up:
Missing Details:
Nurse Review Reminder:
"""

    response = client.responses.create(
        model="gpt-5.2",
        instructions=instructions,
        input=raw_text
    )

    return response.output_text


def show_header():
    st.title("🩺 Nurse Notes AI")
    st.write(
        "A Streamlit app for report sheets, Apple Pencil writing, "
        "iPad dictation, and AI nursing-note drafts."
    )
    st.warning("Use demo/non-PHI information only.")


def report_sheet_section():
    st.header("1. Choose or Upload Report Sheet")

    template_name = st.selectbox(
        "Report sheet type",
        [
            "ICU Report Sheet",
            "Med-Surg Report Sheet",
            "ER Report Sheet",
            "Custom Report Sheet 1",
            "Custom Report Sheet 2",
            "Custom Report Sheet 3",
        ]
    )

    st.session_state.template_name = template_name

    uploaded_file = st.file_uploader(
        "Upload report sheet image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.session_state.uploaded_report_image = image
        st.image(image, caption="Uploaded Report Sheet", use_container_width=True)
    else:
        st.subheader(template_name)

        if template_name == "ICU Report Sheet":
            st.markdown("""
| Section | Notes |
|---|---|
| Room / Initials | |
| Diagnosis | |
| Code Status | |
| Allergies | |
| Neuro | |
| Cardiac | |
| Respiratory | |
| GI / GU | |
| Lines / Drains | |
| Labs | |
| Medications | |
| Plan | |
""")

        elif template_name == "Med-Surg Report Sheet":
            st.markdown("""
| Section | Notes |
|---|---|
| Room / Initials | |
| Admitting Diagnosis | |
| Safety / Fall Risk | |
| Diet | |
| Mobility | |
| Pain | |
| Skin / Wounds | |
| IV Access | |
| Medications | |
| Pending Tasks | |
""")

        elif template_name == "ER Report Sheet":
            st.markdown("""
| Section | Notes |
|---|---|
| Chief Complaint | |
| Triage Level | |
| Vitals | |
| Assessment | |
| Labs / Imaging | |
| Medications Given | |
| Provider Updates | |
| Disposition Plan | |
""")

        else:
            st.markdown("""
| Custom Field | Notes |
|---|---|
| Field 1 | |
| Field 2 | |
| Field 3 | |
| Field 4 | |
| Field 5 | |
| Field 6 | |
| Field 7 | |
| Field 8 | |
""")


def handwriting_section():
    st.header("2. Apple Pencil Writing Area")

    st.write(
        "Use your Apple Pencil or finger to write here. "
        "This captures handwriting as drawing, not typed text yet."
    )

    stroke_width = st.slider("Pen width", 1, 10, 3)

    st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#ffffff",
        height=450,
        drawing_mode="freedraw",
        key="canvas",
    )


def event_note_section():
    st.header("3. Type or Dictate Event Note")

    st.info(
        "On iPad: tap inside the box, then tap the microphone on the iPad keyboard "
        "to use voice-to-text."
    )

    st.session_state.raw_event_note = st.text_area(
        "Raw event note",
        value=st.session_state.raw_event_note,
        height=250,
        placeholder=(
            "Example: At 1430, demo patient reported 7/10 chest discomfort. "
            "Vitals obtained. Provider notified. New orders received..."
        )
    )


def ai_note_section():
    st.header("4. Create AI Nursing Note")

    note_style = st.selectbox(
        "Choose note style",
        [
            "Narrative Nursing Note",
            "DAR Note",
            "SOAP Note",
            "SBAR Summary",
        ]
    )

    if st.button("✨ Create AI Nursing Note"):
        if not st.session_state.raw_event_note.strip():
            st.warning("Type or dictate an event note first.")
        else:
            with st.spinner("Creating nursing note draft..."):
                try:
                    st.session_state.ai_note = create_nursing_note(
                        st.session_state.raw_event_note,
                        st.session_state.template_name,
                        note_style
                    )
                except Exception as error:
                    st.error(f"Something went wrong: {error}")

    st.session_state.ai_note = st.text_area(
        "AI-generated nursing note draft",
        value=st.session_state.ai_note,
        height=300
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save Draft in This Session"):
            if st.session_state.ai_note.strip():
                st.session_state.saved_drafts.append({
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "template": st.session_state.template_name,
                    "raw_note": st.session_state.raw_event_note,
                    "ai_note": st.session_state.ai_note,
                })
                st.success("Draft saved for this session.")
            else:
                st.warning("No AI note to save.")

    with col2:
        st.download_button(
            "Download Note as TXT",
            data=st.session_state.ai_note.encode("utf-8"),
            file_name="nursing_note_draft.txt",
            mime="text/plain",
            disabled=not bool(st.session_state.ai_note.strip())
        )


def saved_drafts_section():
    st.header("5. Saved Drafts")

    if not st.session_state.saved_drafts:
        st.info("No saved drafts yet.")
        return

    for index, draft in enumerate(st.session_state.saved_drafts, start=1):
        with st.expander(f"Draft {index} - {draft['created_at']}"):
            st.write("Template:", draft["template"])
            st.subheader("Raw Note")
            st.write(draft["raw_note"])
            st.subheader("AI Draft")
            st.write(draft["ai_note"])


def main():
    initialize_state()
    show_header()

    tab1, tab2, tab3 = st.tabs([
        "Report Sheet + Writing",
        "Event Note + AI",
        "Saved Drafts"
    ])

    with tab1:
        report_sheet_section()
        handwriting_section()

    with tab2:
        event_note_section()
        ai_note_section()

    with tab3:
        saved_drafts_section()

    st.divider()
    st.caption(
        "AI output is a draft only. A licensed nurse must review, edit, and approve it."
    )


if __name__ == "__main__":
    main()
