import os
import json

from datetime import datetime
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from google import genai

api_key = "AIzaSyDPmuDwgNK9sp3DiYyW9f6cvSoZwu5SfDE"
client = genai.Client(api_key=api_key)  # 使用 Client 來配置 API 金鑰

character = "kinako"  # 預設角色
time_keyword = ["現在幾點", "現在時間"]
weather_keyword = ["天氣", "氣候", "氣溫"]

def ask_ai(content, image, user_id):
	global character
	"""處理不同使用者的對話，確保歷史記錄正確切換"""
	
	history_path = f"./AI_functions/histories/history_{user_id}.json"
	
	# **1️⃣ 讀取對應使用者的歷史記錄**
	if os.path.exists(history_path):
		with open(history_path, "r", encoding="utf8") as file:
			data = json.load(file)

	else:
		# 使用者的歷史紀錄不存在 -> 讀取角色資料
		data = switch_character(character, user_id)

	# 重新建立 chat 物件，確保是該使用者的對話
	chat = client.chats.create(model="gemini-2.0-flash", history=data)

	if content in ['clear', '清除']:
		os.remove(history_path)
		return "資料已清除"

	if any(content.startswith(word) for word in ['restore', '恢復']):
		parts = content.split(" ", 1)
		
		if len(parts) == 1:
			return "必須指定要恢復的檔案"
		
		file_name = parts[1]  # 取得指定的檔案名稱

		if not os.path.exists(f"./AI_functions/output_data/{file_name}.json"):  # 確保 restore_data 成功
			return f"無法恢復檔案 {file_name}，請確認檔案是否存在"

		# 恢復使用者的歷史紀錄
		data = restore_data(file_name)
		
		history_path = f"./AI_functions/histories/history_{user_id}.json"
		
		with open(history_path, "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)
		
		return f"資料已成功從 {file_name} 恢復"

	
	if any(content.startswith(word) for word in ['export', '導出']):
		timestamp = get_timestamp()
		name = content.split(" ", 1)

		if len(name) == 1:
			return "導出檔案必須有名字"
		
		else:
			name = name[1]
			
		file_path = f"./AI_functions/output_data/{user_id}_{name}_{timestamp}.json"
		with open(file_path, "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)

		return f"資料已導出至 {file_path}，可使用 `list` 來顯示所有導出的紀錄"

	if content.startswith('switch'):
		contents = content.split(" ", 1)
		character = contents[1]
		# 切換角色
		switch_character(character, user_id)
		return "角色已切換"

	# **2️⃣ 發送訊息並獲取回應**
	if any(keyword in content for keyword in time_keyword):
		content = get_search(content)

	elif any(keyword in content for keyword in weather_keyword):
		content = get_search(content)

	# if image:
	# 	content = get_picture_response(image)
	
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
	response = chat.send_message(content)
	return response

# def get_picture_response(image):
# 	response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents=[image, "幫我解釋這張照片"]
# 	)

# 	return response.text

def get_search(question):
	# 設定 Google 搜索工具
	google_search_tool = Tool(
	google_search = GoogleSearch()
	)

	response = client.models.generate_content(
		model="gemini-2.0-flash",
		contents=question,
		config=GenerateContentConfig(
			tools=[google_search_tool],
			response_modalities=["TEXT"],
		)
	)
	
	# 返回回應文本
	return response.text  # 假設回應結果是純文本


"""使用者設定"""
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
	chat = client.chats.create(model="gemini-2.0-flash", history=[])
	response = chat.send_message(character_data)
	
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

	return data


def restore_data(data):
	file_path = f"./AI_functions/output_data/{data}.json"
	with open(file_path, "r", encoding="utf8") as file:
		data = json.load(file)

	return data

def set_rules():
	rule_path = f"./Ai_functions/characters/rules.md"

	with open(rule_path, "r", encoding="utf8") as file:
		data = file.read()

	return data

def get_timestamp():
    """獲取當前時間並格式化為 YYYY-MM-DD HH:MM:SS"""
    return datetime.now().strftime("%Y%m%d%H%M%S")