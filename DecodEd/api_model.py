def get_system_prompt(mode):
    """
    Returns specific instructions.
    CRITICAL: For Quiz and Flashcards, we now enforce STRICT JSON output
    so the app can parse it into interactive elements.
    """
    
    base_instruction = (
        "You are an expert Grade 10 Academic Tutor named 'DecodEd'. "
        "Strictly adhere to the facts in the provided text."
    )

    if mode == "Summary":
        return (
            f"{base_instruction} "
            "Create a structured summary using Markdown. Use H2 headers and bullet points. "
            "Bold key terms."
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
