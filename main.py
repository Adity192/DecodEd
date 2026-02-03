import streamlit as st
import pypdf
import os
import json
import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="DecodEd", page_icon="⚡", layout="wide")

# --- DATA MANAGEMENT ---
NOTES_FILE = "my_notes.json"
MAX_PDF_PAGES = 40 # Performance: limit pages for very large PDFs

# Performance: Simple cache to avoid re-initializing or re-listing models frequently
if "model_cache" not in st.session_state:
    st.session_state.model_cache = {}

def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_note(title, content):
    notes = load_notes()
    # Normalize title
    safe_title = title.strip() if title and title.strip() else "Untitled Note"

    existing = next((item for item in notes if item["title"] == safe_title), None)
    if existing:
        existing["content"] = content
        existing["date"] = str(datetime.date.today())
    else:
        notes.append(
            {
                "title": safe_title,
                "content": content,
                "date": str(datetime.date.today()),
            }
        )
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def delete_note(title):
    notes = load_notes()
    notes = [n for n in notes if n["title"] != title]
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

# --- AI LOGIC (Integrated API Model & Controller) ---
def get_system_prompt(mode):
    """
    Returns specific instructions based on the selected mode.
    Enforces strict JSON for interactive modes.
    """
    base_instruction = (
        "You are an expert Grade 10 Academic Tutor named 'DecodEd'. "
        "Strictly adhere to the facts in the provided text. "
        "Do not hallucinate information not present in the source."
    )

    if mode == "Summary":
        return (
            f"{base_instruction} "
            "Create a structured summary using Markdown. Use H2 headers for main topics and bullet points for details. "
            "Bold key terms and definitions."
        )

    elif mode == "Quiz":
        return (
            f"{base_instruction} "
            "Generate exactly 10 Multiple Choice Questions based on the text. "
            "RETURN ONLY RAW JSON. No markdown formatting, no ```json tags. "
            "Format: [{'question': 'Question text', 'options': ['A', 'B', 'C', 'D'], 'answer': 'The full text of the correct option'}]"
        )

    elif mode == "Flashcards":
        return (
            f"{base_instruction} "
            "Create 10 revision flashcards. "
            "RETURN ONLY RAW JSON. No markdown formatting, no ```json tags. "
            "Format: [{'front': 'Concept/Term', 'back': 'Definition/Explanation'}]"
        )

    else:
        return base_instruction

def get_ai_response(api_key, user_text, mode):
    """
    Executes the AI request using Google Gemini.
    Includes caching and error handling.
    """
    if not api_key:
        return "Error: API Key is missing. Please check Settings."

    if not user_text.strip():
        return "Error: Input text is empty."

    try:
        # 1. Configure API
        genai.configure(api_key=api_key)

        # 2. Smart Model Selector (Cached)
        if "target_model" not in st.session_state.model_cache:
            try:
                available_models = []
                for m in genai.list_models():
                    if "generateContent" in m.supported_generation_methods:
                        available_models.append(m.name)
                
                if "models/gemini-1.5-flash" in available_models:
                    st.session_state.model_cache["target_model"] = "gemini-1.5-flash"
                elif "models/gemini-pro" in available_models:
                    st.session_state.model_cache["target_model"] = "gemini-pro"
                elif available_models:
                    st.session_state.model_cache["target_model"] = available_models[0]
                else:
                    return "Error: No compatible Gemini models found."
            except Exception as e:
                return f"Error: Invalid API Key or Connection Failed. ({str(e)})"

        target_model = st.session_state.model_cache["target_model"]

        # 3. Generate
        model = genai.GenerativeModel(target_model)
        system_instruction = get_system_prompt(mode)

        full_prompt = f"{system_instruction}\n\n[SOURCE MATERIAL]:\n{user_text}"

        response = model.generate_content(full_prompt)
        text_response = response.text

        # 4. Parsing Logic for JSON modes
        if mode in ["Quiz", "Flashcards"]:
            # Clean up potential markdown code blocks
            clean_text = text_response.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError:
                return [{"error": "AI failed to generate valid JSON. Please try again or reduce text size."}]

        return text_response

    except Exception as e:
        return f"Error: {str(e)}"

# --- STYLING (CSS) ---
def apply_theme():
    st.markdown(
        """
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

        /* 2. COLOR SCHEME - Dark Void Theme */
        .stApp {
            background-color: #05020a; 
            color: #e9d5ff;
            font-family: 'Inter', sans-serif;
        }

        /* 3. NAVBAR BUTTONS (Big & Centered) */
        /* We target secondary buttons used in the navbar */
        div.stButton > button[kind="secondary"] {
            background-color: #110e1b;
            color: #ffffff !important;
            border: 2px solid #7c3aed; /* Thicker Purple border */
            border-radius: 30px; /* Big pill shape */
            font-size: 20px; /* Bigger Text */
            font-weight: 700;
            padding: 0px 20px;
            width: 100%;
            height: 4.5rem; /* Taller button */
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            white-space: nowrap;
        }
        
        div.stButton > button[kind="secondary"]:hover {
            background-color: #7c3aed;
            color: white !important;
            border-color: #a78bfa;
            box-shadow: 0 0 20px rgba(124, 58, 237, 0.8);
            transform: translateY(-3px);
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
            box-shadow: 0 4px 10px rgba(147, 51, 234, 0.3);
        }
        
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 0 20px rgba(192, 38, 211, 0.6);
        }

        /* 5. CARDS & INPUTS */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #0a0614;
            border: 1px solid #2e1065;
            border-radius: 12px;
            padding: 20px;
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
        
        /* 7. TYPOGRAPHY */
        h1, h2, h3 { 
            color: #ffffff !important; 
            text-shadow: 0 2px 4px rgba(0,0,0,0.5); 
        }
        p, li {
            color: #d1d5db;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- INIT SESSION STATE ---
if "page" not in st.session_state: st.session_state.page = "Home"
# DEFAULT API KEY SET HERE
if "api_key" not in st.session_state: st.session_state.api_key = "AIzaSyBf-kROykmRTMQRYhLLt8Q20Tr6SyyRB5Y"
if "current_note_content" not in st.session_state: st.session_state.current_note_content = ""
if "current_note_title" not in st.session_state: st.session_state.current_note_title = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = None
if "flashcard_data" not in st.session_state: st.session_state.flashcard_data = None
if "fc_index" not in st.session_state: st.session_state.fc_index = 0
if "fc_flipped" not in st.session_state: st.session_state.fc_flipped = False

apply_theme()

# --- HORIZONTAL NAVBAR ---
# Using columns with vertical_alignment="center" to align logo and buttons perfectly
navbar_container = st.container()
with navbar_container:
    # Increased widths for button columns to support larger buttons
    c_logo, c_space, c_h, c_d, c_n, c_a, c_s = st.columns(
        [3, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5], gap="small", vertical_alignment="center"
    )

    with c_logo:
        # Robust path detection for the Logo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "Logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=220)
        else:
            st.markdown("## DecodEd")
            
    with c_h:
        if st.button("HOME", key="nav_home", type="secondary"):
            st.session_state.page = "Home"
            st.rerun()
    with c_d:
        if st.button("DASHBOARD", key="nav_dash", type="secondary"):
            st.session_state.page = "Dashboard"
            st.rerun()
    with c_n:
        if st.button("MY NOTES", key="nav_notes", type="secondary"):
            st.session_state.page = "My Notes"
            st.rerun()
    with c_a:
        if st.button("ABOUT US", key="nav_about", type="secondary"):
            st.session_state.page = "About Us"
            st.rerun()
    with c_s:
        if st.button("SETTINGS", key="nav_sett", type="secondary"):
            st.session_state.page = "Settings"
            st.rerun()
    st.markdown(
        "<div style='height: 2px; background: linear-gradient(90deg, #05020a, #7c3aed, #05020a); margin-top: 10px; margin-bottom: 30px;'></div>",
        unsafe_allow_html=True,
    )

# --- PAGE: HOME ---
if st.session_state.page == "Home":
    c_hero_text, c_hero_img = st.columns([1.5, 1], gap="large")
    with c_hero_text:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h1 style='font-size: 5rem; line-height: 1; font-weight: 800; letter-spacing: -2px;'>Decoding <br><span style='color: #a855f7;'>Academics.</span></h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """<p style='font-size: 1.4rem; margin-top: 25px; margin-bottom: 35px; color: #cbd5e1; line-height: 1.6;'>
            Transforming raw study material into interactive, beneficial learning tools.
            An AI-powered inquiry into efficient revision.
            </p>""",
            unsafe_allow_html=True,
        )
        if st.button("START DECODING 🚀", type="primary"):
            st.session_state.page = "Dashboard"
            st.rerun()

    with c_hero_img:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        home_path = os.path.join(base_dir, "home.png")
        if os.path.exists(home_path):
            st.image(home_path, use_container_width=True)
        else:
            # Fallback placeholder if image missing
            st.markdown("<!-- home.png placeholder -->")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("### Core Capabilities")
    st.markdown("---")
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
elif st.session_state.page == "Dashboard":
    c_title, c_search = st.columns([3, 1.5])
    with c_title:
        st.title("Dashboard")
    with c_search:
        st.markdown("<br>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Search", placeholder="🔍 Search notes...", label_visibility="collapsed"
        )

    # API Key Warning
    if not st.session_state.api_key:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            col_warn_icon, col_warn_text, col_warn_input = st.columns([0.5, 3, 2])
            with col_warn_icon:
                st.markdown("## ⚠️")
            with col_warn_text:
                st.markdown("**API Key Missing**")
                st.caption("Paste your Google Gemini API Key here to enable AI features.")
            with col_warn_input:
                dash_key_input = st.text_input(
                    "Enter Key",
                    type="password",
                    label_visibility="collapsed",
                    placeholder="Paste Key & Press Enter",
                )
                if dash_key_input:
                    st.session_state.api_key = dash_key_input
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("📝 Blank Document")
            st.caption("Input raw text manually from your lectures or textbooks.")
            if st.button(
                "Create Note →",
                key="btn_blank",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.current_note_content = ""
                st.session_state.current_note_title = ""
                st.session_state.page = "Editor"
                st.rerun()
    with c2:
        with st.container(border=True):
            st.subheader("📥 Upload PDF")
            st.caption("Extract text from syllabus documents automatically.")
            uploaded_file = st.file_uploader(
                "", type=["pdf"], label_visibility="collapsed"
            )
            if uploaded_file and st.button(
                "Process PDF →",
                key="btn_pdf",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Processing PDF..."):
                    try:
                        reader = pypdf.PdfReader(uploaded_file)
                        text = ""
                        # Performance Limit
                        max_pages = min(len(reader.pages), MAX_PDF_PAGES)
                        for i in range(max_pages):
                            page_text = reader.pages[i].extract_text()
                            if page_text:
                                text += page_text + "\n"
                        
                        if not text.strip():
                            st.error("Could not extract text. PDF might be an image.")
                        else:
                            st.session_state.current_note_content = text
                            st.session_state.current_note_title = uploaded_file.name
                            st.session_state.page = "Editor"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error reading PDF: {e}")

    st.markdown("<br><h3>Recent Activity</h3><hr>", unsafe_allow_html=True)
    notes = load_notes()
    if "search_query" in locals() and search_query:
        notes = [n for n in notes if search_query.lower() in n["title"].lower()]
        
    if not notes:
        st.info("No activity found. Start a new project above.")
    else:
        # Show last 3 notes
        for note in reversed(notes[-3:]):
            with st.container(border=True):
                col_a, col_b = st.columns([5, 1])
                col_a.markdown(f"#### 📄 {note['title']}")
                col_a.markdown(
                    f"<small style='color:#a78bfa'>Last Edited: {note['date']}</small>",
                    unsafe_allow_html=True,
                )
                if col_b.button("Open", key=f"dash_{note['title']}"):
                    st.session_state.current_note_title = note["title"]
                    st.session_state.current_note_content = note["content"]
                    st.session_state.page = "Editor"
                    st.rerun()

# --- PAGE: MY NOTES ---
elif st.session_state.page == "My Notes":
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
                    st.session_state.current_note_title = note["title"]
                    st.session_state.current_note_content = note["content"]
                    st.session_state.page = "Editor"
                    st.rerun()
                if c3.button("Delete", key=f"del_{i}"):
                    delete_note(note["title"])
                    st.rerun()

# --- PAGE: ABOUT US ---
elif st.session_state.page == "About Us":
    st.title("About DecodEd")

    with st.container(border=True):
        st.markdown("""
        ### 🎯 The Motive
        DecodEd was born from a simple observation: students spend too much time organizing and not enough time learning. 
        I wanted to find a way to apply innovative tools like Large Language Models to make a real change in academics.
        
        **My Learning Goal:** To learn foundational Python programming and how to use a generative AI API, I created this 
        digital web application that transforms raw study material into interactive and beneficial learning tools.
        
        ### 👤 Personal Interest
        My learning goal originates from my interest and love in the field of computer science and digital technologies. 
        While pondering about different personal project ideas, the one that appealed the most to me was the application 
        of LLM models to aid in educational development. This project helps students pursue their academic goals by 
        sharpening their skills efficiently.
        
        ### 🔬 How It Works
        DecodEd is a "Prompt Engineering" wrapper around the Google Gemini API.
        
        1.  **Input:** Raw text or PDFs are uploaded by the user.
        2.  **Logic:** The Python backend applies a "Grade 10 Tutor" persona via specific system instructions.
        3.  **Output:** The API returns structured summaries, quizzes, and flashcards formatted for easy revision.
        
        ### 💡 Justification
        Innovation has always been inspired by building upon the work of those who came before us. Rather than starting 
        from scratch (building my own model), I chose to make use of powerful tools (APIs) already developed through years 
        of research. This allows me to solve real-life problems effectively.
        """)

# --- PAGE: SETTINGS ---
elif st.session_state.page == "Settings":
    st.title("Settings")
    with st.container(border=True):
        st.header("🔑 API Key")
        st.markdown("To use the AI features, you need a Google Gemini API Key.")
        key_input = st.text_input(
            "API Key", value=st.session_state.api_key, type="password"
        )
        if key_input:
            st.session_state.api_key = key_input
            st.success("API Key saved! You can now use the AI features.")

# --- PAGE: EDITOR ---
elif st.session_state.page == "Editor":
    c_back, c_tit, c_sav = st.columns([1, 4, 1])
    with c_back:
        if st.button("← Back"):
            st.session_state.page = "Dashboard"
            st.rerun()
    with c_tit:
        new_title = st.text_input(
            "Title",
            value=st.session_state.current_note_title,
            label_visibility="collapsed",
            placeholder="Note Title...",
        )
    with c_sav:
        if st.button("💾 Save", type="primary"):
            save_note(new_title, st.session_state.current_note_content)
            st.toast("Saved successfully!")

    c_in, c_out = st.columns([1, 1], gap="medium")
    with c_in:
        st.caption("Input Content")
        user_text = st.text_area(
            "Input",
            value=st.session_state.current_note_content,
            height=600,
            label_visibility="collapsed",
            placeholder="Paste your notes or syllabus here..."
        )
        st.session_state.current_note_content = user_text

    with c_out:
        st.caption("AI Generation Tools")
        tool_col, run_col = st.columns([3, 1])
        with tool_col:
            mode = st.selectbox(
                "Mode", ["Summary", "Quiz", "Flashcards"], label_visibility="collapsed"
            )
        with run_col:
            run_btn = st.button("Run ➤", type="primary", use_container_width=True)

        output_container = st.container(border=True)
        with output_container:
            if run_btn:
                if not st.session_state.api_key:
                    st.error("Missing API Key. Please go to Settings.")
                elif not user_text:
                    st.warning("Please enter some text or upload a PDF first.")
                else:
                    with st.spinner(f"Generating {mode}..."):
                        response_data = get_ai_response(
                            st.session_state.api_key, user_text, mode
                        )
                        
                        if isinstance(response_data, str) and response_data.startswith("Error"):
                            st.error(response_data)
                        
                        elif mode == "Quiz":
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
                            # Summary Mode
                            st.markdown(response_data)
                            # Append result to content for saving
                            st.session_state.current_note_content += (
                                f"\n\n--- AI {mode} ---\n{response_data}"
                            )

# --- PAGE: ACTIVE QUIZ ---
elif st.session_state.page == "Active Quiz":
    st.button(
        "← Back to Editor",
        on_click=lambda: st.session_state.update(page="Editor"),
    )
    st.title("🧠 Active Recall Quiz")

    if st.session_state.quiz_data:
        score = 0
        total = len(st.session_state.quiz_data)
        
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**{i+1}. {q.get('question', 'Error')}**")
                choice = st.radio(
                    "Select an option:",
                    q.get("options", []),
                    key=f"q_{i}",
                    label_visibility="collapsed",
                )
                if choice == q.get("answer"):
                    score += 1
                st.markdown("---")
                
            submitted = st.form_submit_button("Submit Quiz", type="primary")
            
        if submitted:
            st.markdown(f"## 🏆 Your Score: {score} / {total}")
            if score == total:
                st.balloons()
                st.success("Perfect Score! You have mastered this topic.")
            elif score > total / 2:
                st.info("Great job! Review the incorrect answers to improve.")
            else:
                st.warning("Keep studying! Try generating a Summary first.")
    else:
        st.error("No quiz data found.")

# --- PAGE: ACTIVE FLASHCARDS ---
elif st.session_state.page == "Active Flashcards":
    st.button(
        "← Back to Editor",
        on_click=lambda: st.session_state.update(page="Editor"),
    )
    st.title("⚡ Flashcards")

    if st.session_state.flashcard_data:
        idx = st.session_state.fc_index
        card = st.session_state.flashcard_data[idx]
        total = len(st.session_state.flashcard_data)
        
        # Progress Bar
        st.progress((idx + 1) / total)
        st.caption(f"Card {idx + 1} of {total}")
        
        # Display Card
        content = card["back"] if st.session_state.fc_flipped else card["front"]
        st.markdown(
            f"""<div class="flashcard">{content}</div>""", unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_prev, col_flip, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.button("Previous"):
                if idx > 0:
                    st.session_state.fc_index -= 1
                    st.session_state.fc_flipped = False
                    st.rerun()
        
        with col_flip:
            btn_text = (
                "Show Answer 🔄"
                if not st.session_state.fc_flipped
                else "Show Question 🔄"
            )
            if st.button(btn_text, type="primary", use_container_width=True):
                st.session_state.fc_flipped = not st.session_state.fc_flipped
                st.rerun()
                
        with col_next:
            if st.button("Next"):
                if idx < total - 1:
                    st.session_state.fc_index += 1
                    st.session_state.fc_flipped = False
                    st.rerun()
    else:
        st.error("No flashcard data found.")
