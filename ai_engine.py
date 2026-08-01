import requests


OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ai(prompt, model="qwen2.5:7b"):

    try:

        response = requests.post(

            OLLAMA_URL,

            json={

                "model": model,

                "prompt": prompt,

                "stream": False,

                "options": {

                    "temperature": 0,

                    "top_p": 0.5,

                    "top_k": 20,

                    "num_predict": 100

                },

                "keep_alive": "10m"

            },

            timeout=120

        )


        response.raise_for_status()


        result = response.json()


        return result.get(
            "response",
            "No response"
        ).strip()


    except Exception as e:

        return f"AI Error: {str(e)}"