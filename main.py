#導入插件
import discord
import os
import re
import json
import asyncio

#從插件導入模組
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 檔

api_key = os.getenv("bot_token")


#機器人元件
intent = discord.Intents.all()
bot = commands.Bot(command_prefix="k!", intents=intent)
bot.remove_command("help")

with open("./jsonfile/data.json", "r", encoding="utf8") as file:
	data = json.load(file)

def get_game_roles(guild):
	role_map = {}

	pattern = re.compile(r'^\[(.+?)\]\s*(.+)$')

	for role in guild.roles:
		m = pattern.match(role.name)
		if not m:
			continue

		emoji = normalize_emoji(m.group(1))
		role_map[emoji] = role

	return role_map

def normalize_emoji(s: str) -> str:
	if "\u200d" in s:
		return s
	return s.replace('\uFE0F', '')

#機器人啟動
@bot.event
async def on_ready():
	for filename in os.listdir("./cmds"):
		if filename.endswith(".py"):
			await bot.load_extension(f"cmds.{filename[:-3]}")
		else:
			pass

	if __name__ == "__main__":
		pass

	print("黃名子上線囉!")
	await bot.tree.sync()
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="使用**/help**來查詢指令 | 管理著毀滅世代"),status=discord.Status.do_not_disturb)

	GUILD_ID = 808332107758698528
	CHANNEL_ID = 815216213750841365
	MESSAGE_ID = 815219247382003734

	guild = bot.get_guild(GUILD_ID)
	
	if guild:
		channel = guild.get_channel(CHANNEL_ID)
		if channel:
			try:
				message = await channel.fetch_message(MESSAGE_ID)
				
				# 呼叫你的函式取得對照表
				role_map = get_game_roles(guild)
				
				print(f"掃描到 {len(role_map)} 個符合格式的身分組，開始新增反應...")

				for emoji_key in role_map.keys():
					try:
						# 機器人對訊息按表情
						await message.add_reaction(emoji_key)
						
						# 稍微暫停一下，避免觸發 Discord Rate Limit (速率限制)
						await asyncio.sleep(0.5) 
						
					except discord.HTTPException:
						print(f"無法新增表情 '{emoji_key}' (可能是無效的 Emoji 或是機器人不在該伺服器)")
					except Exception as e:
						print(f"新增表情 '{emoji_key}' 失敗: {e}")

				print("所有表情檢查/新增完畢！")

			except discord.NotFound:
				print("找不到目標訊息 (Message ID 錯誤或已被刪除)")
		else:
			print("找不到目標頻道 (Channel ID 錯誤)")
	else:
		print("找不到目標伺服器 (Guild ID 錯誤)")

bot.run(api_key) # pyright: ignore[reportArgumentType]
