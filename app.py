import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("Gemini Models")

try:
    for m in genai.list_models():
        st.write(m.name)
except Exception as e:
    st.exception(e)
