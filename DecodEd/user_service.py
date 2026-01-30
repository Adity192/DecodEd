import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="DecodEd | AI Study Tool", page_icon="📚")
st.title("📚 DecodEd: AI Academic Decoder")
st.markdown("### *Structuring the Unstructured*")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    mode = st.selectbox("Choose Output Style:", ["Summary", "Quiz", "Flashcards"])

def get_ai_response(user_text, style):
    system_instruction = (
        "You are an expert Grade 10 Academic Tutor. "
        "Your goal is to simplify complex syllabus text into clear, "
        "easy-to-understand bullet points. Do not hallucinate."
    )
    
    full_prompt = f"{system_instruction}\n\nTask: Transform this into a {style}: {user_text}"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content(full_prompt)
    return response.text

user_input = st.text_area("Paste your syllabus material here:", height=250)

if st.button("Decode Material"):
    if not api_key:
        st.error("Please enter an API Key in the sidebar to proceed.")
    elif not user_input:
        st.warning("The input area is empty. Please paste some text.")
    else:
        with st.spinner("Decoding your material..."):
            try:
                result = get_ai_response(user_input, mode)
                st.success("Successfully Decoded!")
                st.markdown("---")
                st.write(result)
            except Exception as e:
                st.error(f"Technical Error: {e}")