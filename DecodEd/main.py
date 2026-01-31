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
        
        .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 5rem !important;
            max-width: 95% !important;
        }

        /* 2. COLOR SCHEME */
        .stApp {
            background-color: #05020a; 
            color: #e9d5ff;
            font-family: 'Inter', sans-serif;
        }

        /* 3. NAVBAR BUTTONS */
        div.stButton > button[kind="secondary"] {
            background-color: #1a1625;
            color: #ffffff !important;
            border: 2px solid #7c3aed;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 700;
            padding: 0.5rem 1rem;
            width: 100%;
            height: 3.5rem;
            transition: 0.3s;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #7c3aed;
            color: white !important;
            border-color: #a78bfa;
            box-shadow: 0 0 15px rgba(124, 58, 237, 0.6);
        }

        /* 4. PRIMARY BUTTONS */
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
        
        /* 6. FLASHCARD STYLE */
        .flashcard {
            background-color: #1e1b2e;
            border: 2px solid #a78bfa;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(167, 139, 250, 0.2);
        }

        h1, h2, h3 { color: #ffffff !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        
    </style>
    """, unsafe_allow_html=True)

# --- INIT SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'current_note_content' not in st.session_state: st.session_state.current_note_content = ""
if 'current_note_title' not in st.session_state: st.session_state.current_note_title = ""

# --- QUIZ & FLASHCARD STATE ---
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = None
if 'flashcard_data' not in st.session_state: st.session_state.flashcard_data = None
if 'fc_index' not in st.session_state: st.session_state.fc_index = 0
if 'fc_flipped' not in st.session_state: st.session_state.fc_flipped = False

apply_theme()

# --- HORIZONTAL NAVBAR ---
navbar_container = st.container()
with navbar_container:
    c_logo, c_space, c_h, c_d, c_n, c_a, c_s = st.columns([2.5, 0.5, 1.2, 1.2, 1.2, 1.2, 1.2], gap="small")
    with c_logo:
        # UPDATED: Corrected to look for Logo.png specifically
        if os.path.exists("Logo.png"): 
            st.image("Logo.png", width=220) 
        elif os.path.exists("logo.png"): 
            st.image("logo.png", width=220) 
        else: 
            st.markdown("### DecodEd")
            
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

st.markdown("<div style='height: 2px; background: linear-gradient(90deg, #05020a, #7c3aed, #05020a); margin-top: 10px; margin-bottom: 30px;'></div>", unsafe_allow_html=True)


# --- PAGE: HOME ---
if st.session_state.page == 'Home':
    c_hero_text, c_hero_img = st.columns([1.5, 1], gap="large")
    with c_hero_text:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 5rem; line-height: 1; font-weight: 800; letter-spacing: -2px;'>Decoding <br><span style='color: #a855f7;'>Academics.</span></h1>", unsafe_allow_html=True)
        st.markdown("""<p style='font-size: 1.4rem; margin-top: 25px; margin-bottom: 35px; color: #cbd5e1; line-height: 1.6;'>Transforming raw study material into interactive, beneficial learning tools.</p>""", unsafe_allow_html=True)
        if st.button("START DECODING 🚀", type="primary"):
            st.session_state.page = "Dashboard"; st.rerun()
    with c_hero_img:
        # UPDATED: Corrected to look for home.png specifically
        if os.path.exists("home.png"): 
            st.image("home.png", use_container_width=True)
        elif os.path.exists("Home.png"): 
            st.image("Home.png", use_container_width=True)
        elif os.path.exists("home.jpg"): 
            st.image("home.jpg", use_container_width=True)
        else: 
            st.image("https://img.freepik.com/free-vector/gradient-ui-ux-elements-background_23-2149056159.jpg", use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("#### 📄 Simplify"); st.write("Convert complex syllabus PDFs into structured summaries.")
    with f2:
        st.markdown("#### 🧠 Test"); st.write("Automated quiz generation for active recall.")
    with f3:
        st.markdown("#### 💾 Organize"); st.write("A centralized digital notebook.")

# --- PAGE: DASHBOARD ---
elif st.session_state.page == 'Dashboard':
    c_title, c_search = st.columns([3, 1.5])
    with c_title: st.title("Dashboard")
    with c_search: st.markdown("<br>", unsafe_allow_html=True); search_query = st.text_input("Search", placeholder="🔍 Search notes...", label_visibility="collapsed")

    if not st.session_state.api_key:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            col_warn_icon, col_warn_text, col_warn_input = st.columns([0.5, 3, 2])
            with col_warn_icon: st.markdown("## ⚠️")
            with col_warn_text: st.markdown("**API Key Missing**"); st.caption("Paste your Google Gemini API Key here.")
            with col_warn_input:
                dash_key_input = st.text_input("Enter Key", type="password", label_visibility="collapsed", placeholder="Paste Key & Press Enter")
                if dash_key_input: st.session_state.api_key = dash_key_input; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("📝 Blank Document")
            if st.button("Create Note →", key="btn_blank", type="primary", use_container_width=True):
                st.session_state.current_note_content = ""; st.session_state.current_note_title = ""; st.session_state.page = "Editor"; st.rerun()
    with c2:
        with st.container(border=True):
            st.subheader("📥 Upload PDF")
            uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
            if uploaded_file and st.button("Process PDF →", key="btn_pdf", type="primary", use_container_width=True):
                reader = pypdf.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages: text += page.extract_text() + "\n"
                st.session_state.current_note_content = text; st.session_state.current_note_title = uploaded_file.name; st.session_state.page = "Editor"; st.rerun()
    
    st.markdown("<br><h3>Recent Activity</h3><hr>", unsafe_allow_html=True)
    notes = load_notes()
    if search_query: notes = [n for n in notes if search_query.lower() in n['title'].lower()]
    if not notes: st.info("No activity found.")
    else:
        for note in reversed(notes[-3:]):
            with st.container(border=True):
                col_a, col_b = st.columns([5,1])
                col_a.markdown(f"#### 📄 {note['title']}")
                col_a.markdown(f"<small style='color:#a78bfa'>Last Edited: {note['date']}</small>", unsafe_allow_html=True)
                if col_b.button("Open", key=f"dash_{note['title']}"):
                    st.session_state.current_note_title = note['title']; st.session_state.current_note_content = note['content']; st.session_state.page = "Editor"; st.rerun()

# --- PAGE: MY NOTES ---
elif st.session_state.page == 'My Notes':
    st.title("My Notebook")
    notes = load_notes()
    if not notes: st.write("Library is empty.")
    else:
        for i, note in enumerate(notes):
            with st.container(border=True):
                c1, c2, c3 = st.columns([6, 1, 1])
                c1.markdown(f"### {note['title']}")
                c1.caption(f"{note['date']}")
                if c2.button("Edit", key=f"edit_{i}"): st.session_state.current_note_title = note['title']; st.session_state.current_note_content = note['content']; st.session_state.page = "Editor"; st.rerun()
                if c3.button("Delete", key=f"del_{i}"): delete_note(note['title']); st.rerun()

# --- PAGE: ABOUT US ---
elif st.session_state.page == 'About Us':
    st.title("About DecodEd")
    with st.container(border=True):
        st.markdown("""### 🎯 The Motive\n**DecodEd** was born from a simple observation: students spend too much time *organizing* and not enough time *learning*.\n\n### 🔬 How It Works\nDecodEd is a "Prompt Engineering" wrapper around the Google Gemini API.\n1. **Input:** Raw text or PDFs.\n2. **Logic:** Python backend applies a "Grade 10 Tutor" persona.\n3. **Output:** Structured summaries, quizzes, and flashcards.""")

# --- PAGE: SETTINGS ---
elif st.session_state.page == 'Settings':
    st.title("Settings")
    with st.container(border=True):
        st.header("🔑 API Key")
        key_input = st.text_input("API Key", value=st.session_state.api_key, type="password")
        if key_input: st.session_state.api_key = key_input; st.success("Connected!")

# --- PAGE: EDITOR ---
elif st.session_state.page == 'Editor':
    c_back, c_tit, c_sav = st.columns([1, 4, 1])
    with c_back:
        if st.button("← Back"): st.session_state.page = "Dashboard"; st.rerun()
    with c_tit:
        new_title = st.text_input("Title", value=st.session_state.current_note_title, label_visibility="collapsed", placeholder="Note Title...")
    with c_sav:
        if st.button("💾 Save", type="primary"): save_note(new_title, st.session_state.current_note_content); st.toast("Saved!")

    c_in, c_out = st.columns([1, 1], gap="medium")
    with c_in:
        st.caption("Input Content")
        user_text = st.text_area("Input", value=st.session_state.current_note_content, height=500, label_visibility="collapsed")
        st.session_state.current_note_content = user_text 

    with c_out:
        st.caption("AI Tools")
        tool_col, run_col = st.columns([3, 1])
        with tool_col: mode = st.selectbox("Mode", ["Summary", "Quiz", "Flashcards"], label_visibility="collapsed")
        with run_col: run_btn = st.button("Run ➤", type="primary", use_container_width=True)

        output_container = st.container(border=True)
        with output_container:
            if run_btn:
                if not st.session_state.api_key: st.error("Missing API Key.")
                elif not user_text: st.warning("No text to process.")
                else:
                    with st.spinner("Processing..."):
                        response_data = api_controller.get_ai_response(st.session_state.api_key, user_text, mode)
                        
                        # --- LOGIC TO HANDLE QUIZ & FLASHCARDS REDIRECTION ---
                        if mode == "Quiz":
                            if isinstance(response_data, list): 
                                st.session_state.quiz_data = response_data
                                st.session_state.page = "Active Quiz"
                                st.rerun()
                            else:
                                st.error("AI failed to generate quiz structure. Try again.")
                        
                        elif mode == "Flashcards":
                            if isinstance(response_data, list):
                                st.session_state.flashcard_data = response_data
                                st.session_state.fc_index = 0
                                st.session_state.fc_flipped = False
                                st.session_state.page = "Active Flashcards"
                                st.rerun()
                            else:
                                st.error("AI failed to generate flashcards. Try again.")
                                
                        else:
                            st.markdown(response_data)
                            st.session_state.current_note_content += f"\n\n--- AI {mode} ---\n{response_data}"

# --- PAGE: ACTIVE QUIZ ---
elif st.session_state.page == 'Active Quiz':
    st.button("← Back to Editor", on_click=lambda: st.session_state.update(page="Editor"))
    st.title("🧠 Active Recall Quiz")
    
    if st.session_state.quiz_data:
        score = 0
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**{i+1}. {q.get('question', 'Error')}:**")
                choice = st.radio("Select an option:", q.get('options', []), key=f"q_{i}", label_visibility="collapsed")
                st.markdown("---")
                if choice == q.get('answer'):
                    score += 1

            submitted = st.form_submit_button("Submit Quiz", type="primary")
            if submitted:
                st.markdown(f"## 🏆 Your Score: {score} / {len(st.session_state.quiz_data)}")
                if score == len(st.session_state.quiz_data):
                    st.balloons()

# --- PAGE: ACTIVE FLASHCARDS ---
elif st.session_state.page == 'Active Flashcards':
    st.button("← Back to Editor", on_click=lambda: st.session_state.update(page="Editor"))
    st.title("⚡ Flashcards")
    
    if st.session_state.flashcard_data:
        idx = st.session_state.fc_index
        card = st.session_state.flashcard_data[idx]
        total = len(st.session_state.flashcard_data)
        st.progress((idx + 1) / total)
        
        content = card['back'] if st.session_state.fc_flipped else card['front']
        st.markdown(f"""<div class="flashcard">{content}</div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_prev, col_flip, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("Previous") and idx > 0:
                st.session_state.fc_index -= 1; st.session_state.fc_flipped = False; st.rerun()
        with col_flip:
            if st.button("Flip 🔄", type="primary", use_container_width=True):
                st.session_state.fc_flipped = not st.session_state.fc_flipped; st.rerun()
        with col_next:
            if st.button("Next") and idx < total - 1:
                st.session_state.fc_index += 1; st.session_state.fc_flipped = False; st.rerun()
    else:
        st.error("No flashcard data found.")
