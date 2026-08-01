import os
from google import genai


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_ai(prompt, model="gemini-2.0-flash"):

    try:

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        return response.text.strip()


    except Exception as e:

        return f"AI Error: {str(e)}"