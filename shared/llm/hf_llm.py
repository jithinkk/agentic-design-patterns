import os
import requests


class HFLLM:
    def __init__(self, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.model = model
        self.api_url = f"https://router.huggingface.co/models/{model}"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
        }

    def invoke(self, messages):
        prompt = self._format_messages(messages)

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                },
                timeout=60
            )
            
            if response.status_code != 200:
                return {"error": f"Status {response.status_code}: {response.text}"}
            
            data = response.json()
            
            # Handle HF response format
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", str(data))
            else:
                return str(data)
        except Exception as e:
            return {"error": f"API Error: {str(e)}"}

    def _format_messages(self, messages):
        return "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        ) + "\nassistant:"