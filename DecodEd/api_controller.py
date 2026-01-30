import google.generativeai as genai
from api_model import get_system_prompt

def get_ai_response(api_key, user_text, mode):
    if not api_key:
        return "⚠️ Error: API Key is missing. Please go to Settings."
    
    try:
        # 1. Configure API
        genai.configure(api_key=api_key)

        # 2. SMART MODEL SELECTOR (This fixes the 404 Error)
        # We ask the API what models are actually available to your key
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except Exception as e:
            return f"❌ Authorization Error: Your API Key is invalid or has no permissions. Details: {e}"

        # 3. Pick the best model available
        # We prefer Flash (Fastest), then Pro (Standard)
        if 'models/gemini-1.5-flash' in available_models:
            target_model = 'gemini-1.5-flash'
        elif 'models/gemini-1.5-flash-latest' in available_models:
            target_model = 'gemini-1.5-flash-latest'
        elif 'models/gemini-pro' in available_models:
            target_model = 'gemini-pro'
        elif available_models:
            target_model = available_models[0] # Pick the first one found
        else:
            return "❌ Error: No AI models found for this API Key."

        # 4. Generate Content
        model = genai.GenerativeModel(target_model)
        system_instruction = get_system_prompt(mode)
        full_prompt = f"{system_instruction}\n\n[USER TEXT TO PROCESS]:\n{user_text}"
        
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        return f"❌ Connection Error: {str(e)}"