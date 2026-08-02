import os
from groq import Groq

# Initialize Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_ai(prompt, model="llama-3.3-70b-versatile"):
    try:

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """
You are EnterpriseAI Assistant.

Your behavior:
- Reply in the same language used by the user.
- If the user writes in Telugu, reply in Telugu.
- If the user writes in Telugu-English (Tanglish), reply in simple Telugu-English.
- If the user writes in English, reply in English.
- Keep explanations simple and beginner-friendly.
- Explain step by step whenever possible.
- For programming questions:
  * Give complete working code.
  * Explain every important line in simple language.
  * Mention output if necessary.
- For emails, reports, letters and documents:
  * Generate professional content.
- For translation:
  * Give only the translated text unless the user asks for an explanation.
- Be friendly, polite and professional.
- If you don't know something, honestly say you don't know instead of making up an answer.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=2048
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"🤖 AI Error: {str(e)}"