import google.generativeai as gemini #gemini api

api_key = "AIzaSyDPmuDwgNK9sp3DiYyW9f6cvSoZwu5SfDE"
gemini.configure(api_key = api_key)
model = gemini.GenerativeModel('gemini-2.0-flash')

chat = model.start_chat(history=[])

def ask_ai(content): 
	response = chat.send_message(
		content, 
		generation_config = gemini.types.GenerationConfig(
			candidate_count = 1,
			max_output_tokens = 2000,
			temperature=0.7
			)
		)
	
	return response.text