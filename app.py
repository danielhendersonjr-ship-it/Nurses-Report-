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

