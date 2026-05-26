import ollama

response = ollama.chat(
    model="deepseek-r1:14b",
    messages=[{
        "role":    "user",
        "content": "Say hello and nothing else"
    }],
    stream=True
)

full_response = ""

for chunk in response:
    token = chunk['message']['content']
    print(token, end='', flush=True)
    full_response += token

print()  # newline when done
print( full_response)