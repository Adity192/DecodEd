import google.generativeai as genai
import json
from api_model import get_system_prompt

def get_ai_response(api_key, user_text, mode):
    if not api_key:
        return None  # Return None so main.py handles the error

    try:
        # 1. Configure API
        genai.configure(api_key=api_key)

        # 2. Smart Model Selector
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except:
            return "Error: Invalid API Key"

        if 'models/gemini-1.5-flash' in available_models:
            target_model = 'gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            target_model = 'gemini-pro'
        elif available_models:
            target_model = available_models[0]
        else:
            return "Error: No models found"

        # 3. Generate
        model = genai.GenerativeModel(target_model)
        system_instruction = get_system_prompt(mode)
        
        # We explicitly ask for JSON in the user prompt to reinforce the system prompt
        full_prompt = f"{system_instruction}\n\n[SOURCE MATERIAL]:\n{user_text}"
        
        response = model.generate_content(full_prompt)
        text_response = response.text

        # 4. PARSING LOGIC (New)
        if mode in ["Quiz", "Flashcards"]:
            # Clean up potential markdown code blocks like ```json ... ```
            clean_text = text_response.replace("```json", "").replace("```", "").strip()
            try:
                # Convert string to Python List/Dictionary
                return json.loads(clean_text)
            except json.JSONDecodeError:
                # If AI fails to give JSON, return error structure
                return [{"error": "AI failed to generate valid JSON. Try again."}]
        
        return text_response

    except Exception as e:
        return f"Error: {str(e)}"
