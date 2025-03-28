import google.generativeai as gemini

from datetime import datetime

# 獲取當前時間
current_time = datetime.now()

api_key = "AIzaSyDPmuDwgNK9sp3DiYyW9f6cvSoZwu5SfDE"
gemini.configure(api_key=api_key)
model = gemini.GenerativeModel('gemini-1.5-flash')

def ask_ai(content):
	chat = model.start_chat(history=[])

	# **2️⃣ 發送訊息並獲取回應**
	response = chat.send_message(
		content,
		generation_config=gemini.types.GenerationConfig(
			candidate_count=1,
			max_output_tokens=2000,
			temperature=0.2
		)
    )

	return response.text

print(ask_ai(f"現在時間是：{current_time}，你可以用人性化的用語告訴我現在幾點嗎？"))