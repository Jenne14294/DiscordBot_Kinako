import os
import google.generativeai as gemini #gemini api

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

gemini.configure(api_key = api_key)
model = gemini.GenerativeModel('gemini-2.0-flash')

chat = model.start_chat(history=[])

def ask_ai(content): 
	response = chat.send_message(
		content, 
		generation_config = gemini.types.GenerationConfig(
			candidate_count = 1,
			max_output_tokens = 2000,
			temperature=0.2
			)
		)
	
	return response.text