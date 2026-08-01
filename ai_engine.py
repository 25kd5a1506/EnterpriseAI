import os
from groq import Groq


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_ai(prompt, model="llama-3.3-70b-versatile"):

    try:

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5
        )

        return response.choices[0].message.content.strip()


    except Exception as e:

        return f"AI Error: {str(e)}"