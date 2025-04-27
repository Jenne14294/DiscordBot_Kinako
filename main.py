#導入插件
import discord
import os
import json

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
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="使用/help來查詢指令|管理著AshanStudio"),status=discord.Status.do_not_disturb)

@bot.command()
async def sync(ctx):
	await bot.tree.sync()
	await ctx.send('指令已同步!')

bot.run(api_key) # pyright: ignore[reportArgumentType]
