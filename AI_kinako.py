import os
import json
from datetime import datetime
import google.generativeai as gemini

api_key = "AIzaSyDPmuDwgNK9sp3DiYyW9f6cvSoZwu5SfDE"
gemini.configure(api_key=api_key)
model = gemini.GenerativeModel('gemini-1.5-flash')

character = "kinako"  # 預設角色

def ask_ai(content, user_id):
	global character
	"""處理不同使用者的對話，確保歷史記錄正確切換"""
	
	history_path = f"./AI_functions/histories/history_{user_id}.json"
	
	# **1️⃣ 讀取對應使用者的歷史記錄**
	if os.path.exists(history_path):
		with open(history_path, "r", encoding="utf8") as file:
			data = json.load(file)

	else:
		# 使用者的歷史紀錄不存在 -> 讀取角色資料
		data = restore_data()

	# 重新建立 chat 物件，確保是該使用者的對話
	chat = model.start_chat(history=data)

	if content in ['clear', '清除']:
		os.remove(history_path)
		return "資料已清除"

	if content in ['restore', '恢復']:
		# 恢復使用者的歷史紀錄
		data = restore_data()

		with open(history_path, "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)
		
		return "資料已恢復"

	if content.startswith('switch'):
		contents = content.split(" ", 1)
		character = contents[1]
		# 切換角色
		switch_character(character, user_id)
		return "角色已切換"

	# **2️⃣ 發送訊息並獲取回應**
	if "現在幾點" in content or "現在時間" in content:
		content = f"當前時間 {datetime.now()}，告訴我現在幾點，只要說到幾點幾分就好(無條件捨去)"

	response = get_response(content, chat)

	# **3️⃣ 儲存對話紀錄**
	data.append({"parts": [{"text": content}], "role": "user"})
	data.append({"parts": [{"text": response.text}], "role": "model"})

	# **4️⃣ 確保紀錄儲存到該使用者的 JSON**
	if user_id:
		with open(history_path, "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)

	return response.text

def get_response(content, chat):
	# **2️⃣ 發送訊息並獲取回應**
	response = chat.send_message(
		content,
		generation_config=gemini.types.GenerationConfig(
			candidate_count=1,
			max_output_tokens=2000,
			temperature=0.2
		)
	)

	return response

def reset_history(user_id):
	"""清空指定使用者的歷史記錄"""
	history_path = f"./AI_functions/histories/history_{user_id}.json"
	with open(history_path, "w", encoding="utf8") as file:
		json.dump([], file, indent=4, ensure_ascii=False)

def load_character(character):
	"""載入角色資料"""
	default_file = "./AI_functions/characters/kinako.md"
	character_file = f"./AI_functions/characters/{character}.md" if character else default_file

	# 如果角色檔案不存在，就改用預設檔案
	history_file = character_file if os.path.exists(character_file) else default_file

	# 檢查是否確實有可用的角色檔案，避免讀取錯誤
	if not os.path.exists(history_file):
		raise FileNotFoundError(f"角色檔案不存在: {history_file}")

	# 讀取檔案內容
	with open(history_file, "r", encoding="utf8") as file:
		character_data = file.read()

	return character_data  # 保持原始格式，不替換 `\n`

def get_character_response(character_data):
	"""根據角色資料產生開場白回應"""
	chat = model.start_chat(history=[])

	response = chat.send_message(
		character_data, 
		generation_config=gemini.types.GenerationConfig(
			candidate_count=1,
			max_output_tokens=2000,
			temperature=0.7
		)
	)
	
	return response.text

def switch_character(character, user_id):
	"""切換角色並清空使用者歷史紀錄"""
	history_path = f"./AI_functions/histories/history_{user_id}.json"
	
	# 讀取新角色資料
	new_character_data = load_character(character)  # 假設此時是想換成 'kinako'，可根據需求變動角色
	new_character_rule = set_rules()
	
	# 清空歷史紀錄並將新角色資料寫入
	reset_history(user_id)
	
	# 寫入新的角色資料到歷史紀錄
	new_rule_response = get_character_response(new_character_rule)
	new_data_response = get_character_response(new_character_data)
	data = [
		{"parts": [{"text": new_character_rule}], "role": "user"},
		{"parts": [{"text": new_rule_response}], "role": "model"},
		{"parts": [{"text": new_character_data}], "role": "user"},
		{"parts": [{"text": new_data_response}], "role": "model"}
	]

	with open(history_path, "w", encoding="utf8") as file:
		json.dump(data, file, indent=4, ensure_ascii=False)

def restore_data():
	global character
	# 使用者的歷史紀錄不存在 -> 讀取角色資料
	data = []  # 初始化空的歷史紀錄

	character_rule = set_rules()
	rule_response = get_character_response(character_rule)
	
	character_data = load_character(character)  # 讀取角色資料
	data_response = get_character_response(character_data)

	# 把角色資料加入歷史紀錄，這樣會當作第一條訊息
	data = [
		{"parts": [{"text": character_rule}], "role": "user"},
		{"parts": [{"text": rule_response}], "role": "model"},
		{"parts": [{"text": character_data}], "role": "user"},
		{"parts": [{"text": data_response}], "role": "model"}
	]

	return data

def set_rules():
	rule_path = f"./Ai_functions/characters/rules.md"

	with open(rule_path, "r", encoding="utf8") as file:
		data = file.read()

	return data
