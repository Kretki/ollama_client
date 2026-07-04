import ollama

model_name = "gemma4:12b"

response = ollama.chat(
    model=model_name,
    messages=[{"role": "user", "content": "Provide some unusual code for hello world in c"}]
)

print(response["message"]["content"])