import streamlit as st
import pypdf
import os
import json
import datetime
import api_controller

# --- CONFIGURATION ---
st.set_page_config(page_title="DecodEd", page_icon="⚡", layout="wide")

# --- DATA MANAGEMENT ---
NOTES_FILE = "my_notes.json"

def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_note(title, content):
    notes = load_notes()
    existing = next((item for item in notes if item["title"] == title), None)
    if existing:
        existing["content"] = content
        existing["date"] = str(datetime.date.today())
    else:
        notes.append({
            "title": title if title else "Untitled Note",
            "content": content,
            "date": str(datetime.date.today())
        })
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

def delete_note(title):
    notes = load_notes()
    notes = [n for n in notes if n["title"] != title]
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

# --- STYLING (CSS) ---
def apply_theme():
    st.markdown("""
    <style>
        /* 1. RESET & POSITIONING */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;} 
        
        /* Forces content to top of page */
        .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 5rem !important;
            max-width: 95% !important;
        }

        /* 2. COLOR SCHEME */
        .stApp {
            background-color: #05020a; /* Ultra Dark background */
            color: #e9d5ff;
            font-family: 'Inter', sans-serif;
        }

        /* 3. NAVBAR BUTTONS (High Contrast) */
        div.stButton > button[kind="secondary"] {
            background-color: #1a1625; /* Dark box */
            color: #ffffff !important; /* PURE WHITE TEXT */
            border: 2px solid #7c3aed; /* Bright Purple Border */
            border-radius: 10px; /* Rectangular Curved Edges */
            font-size: 16px;
            font-weight: 700; /* Bold text */
            padding: 0.5rem 1rem;
            width: 100%;
            height: 3.5rem; /* Bigger size */
            transition: 0.3s;
        }
        
        div.stButton > button[kind="secondary"]:hover {
            background-color: #7c3aed; /* Fill with purple on hover */
            color: white !important;
            border-color: #a78bfa;
            box-shadow: 0 0 15px rgba(124, 58, 237, 0.6); /* Glow */
        }

        /* 4. PRIMARY BUTTONS (Action Buttons) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #9333ea, #c026d3);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 700;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
        }

        /* 5. CARDS & INPUTS */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #110e1b;
            border: 1px solid #2e1065;
            border-radius: 12px;
        }
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #0f0518;
            color: white;
            border: 1px solid #5b21b6;
            border-radius: 8px;
        }

        /* TEXT HEADERS */
        h1, h2, h3 { color: #ffffff !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        
    </style>
    """, unsafe_allow_html=True)

# --- INIT SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'current_note_content' not in st.session_state: st.session_state.current_note_content = ""
if 'current_note_title' not in st.session_state: st.session_state.current_note_title = ""

apply_theme()

# --- HORIZONTAL NAVBAR ---
navbar_container = st.container()
with navbar_container:
    # Cols: Logo (Wide) | Spacer (Narrow) | Links...
    c_logo, c_space, c_h, c_d, c_n, c_a, c_s = st.columns([2.5, 0.5, 1.2, 1.2, 1.2, 1.2, 1.2], gap="small")
    
    with c_logo:
        # =========================================================================
        # 🟢 LOGO SECTION
        # =========================================================================
        if os.path.exists("logo.png"):
             # Wide width for rectangular logo
             st.image("logo.png", width=220) 
        else:
             st.markdown("### DecodEd")
        # =========================================================================

    with c_h:
        if st.button("HOME", key="nav_home"): st.session_state.page = "Home"; st.rerun()
    with c_d:
        if st.button("DASHBOARD", key="nav_dash"): st.session_state.page = "Dashboard"; st.rerun()
    with c_n:
        if st.button("MY NOTES", key="nav_notes"): st.session_state.page = "My Notes"; st.rerun()
    with c_a:
        if st.button("ABOUT US", key="nav_about"): st.session_state.page = "About Us"; st.rerun()
    with c_s:
        if st.button("SETTINGS", key="nav_sett"): st.session_state.page = "Settings"; st.rerun()

# --- NAVBAR BOTTOM LINE ---
st.markdown("<div style='height: 2px; background: linear-gradient(90deg, #05020a, #7c3aed, #05020a); margin-top: 10px; margin-bottom: 30px;'></div>", unsafe_allow_html=True)


# --- PAGE: HOME ---
if st.session_state.page == 'Home':
    
    # Hero Section
    c_hero_text, c_hero_img = st.columns([1.5, 1], gap="large")
    
    with c_hero_text:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 5rem; line-height: 1; font-weight: 800; letter-spacing: -2px;'>Decoding <br><span style='color: #a855f7;'>Academics.</span></h1>", unsafe_allow_html=True)
        
        st.markdown("""
        <p style='font-size: 1.4rem; margin-top: 25px; margin-bottom: 35px; color: #cbd5e1; line-height: 1.6;'>
        Transforming raw study material into interactive, beneficial learning tools.
        <br>
        <span style='font-size: 1rem; color: #94a3b8;'>
        An AI-powered inquiry into efficient revision • IB Personal Project 2025-26
        </span>
        </p>
        """, unsafe_allow_html=True)
        
        if st.button("START DECODING 🚀", type="primary"):
            st.session_state.page = "Dashboard"
            st.rerun()

    with c_hero_img:
        # =========================================================================
        # 🟢 HERO IMAGE SECTION
        # Save your image as 'home.png' in the same folder.
        # =========================================================================
        if os.path.exists("home.png"):
            st.image("home.png", use_container_width=True)
        elif os.path.exists("home.jpg"):
            st.image("home.jpg", use_container_width=True)
        else:
            # Fallback placeholder if no local image is found
            st.image(
                "https://img.freepik.com/free-vector/gradient-ui-ux-elements-background_23-2149056159.jpg", 
                use_container_width=True
            )
        # =========================================================================

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Features Grid
    st.markdown("### Core Capabilities")
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True):
            st.markdown("#### 📄 Simplify")
            st.write("Convert complex syllabus PDFs into structured, easy-to-read summaries.")
    with f2:
        with st.container(border=True):
            st.markdown("#### 🧠 Test")
            st.write("Automated quiz generation for active recall and exam preparation.")
    with f3:
        with st.container(border=True):
            st.markdown("#### 💾 Organize")
            st.write("A centralized digital notebook to manage your revision materials.")


# --- PAGE: DASHBOARD ---
elif st.session_state.page == 'Dashboard':
    # Top Bar: Title + Search
    c_title, c_search = st.columns([3, 1.5])
    with c_title:
        st.title("Dashboard")
        st.caption("Select an input method to begin.")
    with c_search:
        st.markdown("<br>", unsafe_allow_html=True)
        search_query = st.text_input("Search", placeholder="🔍 Search notes...", label_visibility="collapsed")

    # Action Cards
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        with st.container(border=True):
            st.subheader("📝 Blank Document")
            st.write("Input raw text manually from your lectures or textbooks.")
            if st.button("Create Note →", key="btn_blank", type="primary", use_container_width=True):
                st.session_state.current_note_content = ""
                st.session_state.current_note_title = ""
                st.session_state.page = "Editor"
                st.rerun()

    with c2:
        with st.container(border=True):
            st.subheader("📥 Upload PDF")
            st.write("Extract text from syllabus documents automatically.")
            uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
            if uploaded_file is not None:
                if st.button("Process PDF →", key="btn_pdf", type="primary", use_container_width=True):
                    reader = pypdf.PdfReader(uploaded_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    st.session_state.current_note_content = text
                    st.session_state.current_note_title = uploaded_file.name
                    st.session_state.page = "Editor"
                    st.rerun()
    
    # Recent Notes Section
    st.markdown("<br><h3>Recent Activity</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    notes = load_notes()
    if search_query:
        notes = [n for n in notes if search_query.lower() in n['title'].lower() or search_query.lower() in n['content'].lower()]

    if not notes:
        st.info("No activity found. Start a new project above.")
    else:
        for note in reversed(notes[-3:]): # Show last 3
            with st.container(border=True):
                col_a, col_b = st.columns([5,1])
                col_a.markdown(f"#### 📄 {note['title']}")
                col_a.markdown(f"<small style='color:#a78bfa'>Last Edited: {note['date']}</small>", unsafe_allow_html=True)
                if col_b.button("Open", key=f"dash_{note['title']}"):
                    st.session_state.current_note_title = note['title']
                    st.session_state.current_note_content = note['content']
                    st.session_state.page = "Editor"
                    st.rerun()

# --- PAGE: MY NOTES ---
elif st.session_state.page == 'My Notes':
    st.title("My Notebook")
    
    notes = load_notes()
    if not notes:
        st.write("Library is empty.")
    else:
        for i, note in enumerate(notes):
            with st.container(border=True):
                c1, c2, c3 = st.columns([6, 1, 1])
                c1.markdown(f"### {note['title']}")
                c1.caption(f"{note['date']}")
                
                if c2.button("Edit", key=f"edit_{i}"):
                    st.session_state.current_note_title = note['title']
                    st.session_state.current_note_content = note['content']
                    st.session_state.page = "Editor"
                    st.rerun()
                if c3.button("Delete", key=f"del_{i}"):
                    delete_note(note['title'])
                    st.rerun()

# --- PAGE: ABOUT US ---
elif st.session_state.page == 'About Us':
    st.title("About DecodEd")
    
    with st.container(border=True):
        st.markdown("""
        ### 🎯 The Motive
        **DecodEd** was born from a simple observation: students spend too much time *organizing* and not enough time *learning*. 
        
        This project was developed as an inquiry into personalized AI tutoring tools. The goal was to bridge the gap between human language and machine logic, creating a tool that transforms raw study material into interactive, beneficial learning aids.

        ### 🔬 How It Works
        DecodEd is not just a text editor; it is a "Prompt Engineering" wrapper around the Google Gemini API. 
        1.  **Input:** You provide raw text or PDFs.
        2.  **Logic:** The Python backend applies a specific "Persona" (Grade 10 Tutor) to the AI.
        3.  **Output:** The system forces the AI to strictly adhere to syllabus content, minimizing hallucinations and maximizing academic relevance.

        ### 🛠️ Technology Stack
        *   **Frontend:** Streamlit (Python) for the web interface.
        *   **Backend:** Python logic for file parsing and data handling.
        *   **AI Model:** Google Gemini 1.5 Flash (chosen for speed and efficiency).
        *   **Verification:** CARRDS analysis was used to select reliable documentation and libraries.

        *Created as part of the IB MYP Personal Project (2025-26).*
        """)

# --- PAGE: SETTINGS ---
elif st.session_state.page == 'Settings':
    st.title("Settings")
    with st.container(border=True):
        st.header("🔑 API Key")
        st.write("Enter your Google Gemini API key to enable AI features.")
        key_input = st.text_input("API Key", value=st.session_state.api_key, type="password")
        if key_input:
            st.session_state.api_key = key_input
            st.success("Connected to Gemini!")

# --- PAGE: EDITOR ---
elif st.session_state.page == 'Editor':
    # Top Bar
    c_back, c_tit, c_sav = st.columns([1, 4, 1])
    with c_back:
        if st.button("← Back"):
            st.session_state.page = "Dashboard"
            st.rerun()
    with c_tit:
        new_title = st.text_input("Title", value=st.session_state.current_note_title, label_visibility="collapsed", placeholder="Note Title...")
    with c_sav:
        if st.button("💾 Save", type="primary"):
            save_note(new_title, st.session_state.current_note_content)
            st.toast("Saved!")

    # Workspace
    c_in, c_out = st.columns([1, 1], gap="medium")
    
    with c_in:
        st.caption("Input Content")
        user_text = st.text_area("Input", value=st.session_state.current_note_content, height=500, label_visibility="collapsed")
        st.session_state.current_note_content = user_text # Auto-update state

    with c_out:
        st.caption("AI Tools")
        # Tool selector
        tool_col, run_col = st.columns([3, 1])
        with tool_col:
            mode = st.selectbox("Mode", ["Summary", "Quiz", "Flashcards"], label_visibility="collapsed")
        with run_col:
            run_btn = st.button("Run ➤", type="primary", use_container_width=True)

        # Output Area
        output_container = st.container(border=True)
        with output_container:
            if run_btn:
                if not st.session_state.api_key:
                    st.error("Missing API Key.")
                elif not user_text:
                    st.warning("No text to process.")
                else:
                    with st.spinner("Processing..."):
                        res = api_controller.get_ai_response(st.session_state.api_key, user_text, mode)
                        st.markdown(res)
                        # Option to append
                        st.session_state.current_note_content += f"\n\n--- AI {mode} ---\n{res}"
            else:
                st.write("AI Output will appear here...")