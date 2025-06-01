import google.generativeai as genai

genai.configure(api_key='your-key')

# List available models
for m in genai.list_models():
    print(m.name)
