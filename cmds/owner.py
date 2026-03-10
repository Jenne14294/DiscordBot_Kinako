import discord
import os
import sys
import random
import re
import json
import asyncio
import yt_dlp
import importlib
import requests
import dbFunction
import AI_kinako

from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
from discord.ui import LayoutView, Container, Section, TextDisplay, Separator, ActionRow, Button
from discord.utils import get
from datetime import datetime
from cmds.economy import reload_db


class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(description='重新載入')
	@app_commands.describe(類別="重載的類別")
	@app_commands.choices(類別=[
			app_commands.Choice(name="管理(admin)", value="admin"),
			app_commands.Choice(name="音樂(audio)", value="audio"),
			app_commands.Choice(name="經濟(economy)", value="economy"),
			app_commands.Choice(name="事件(event)", value="event"),
			app_commands.Choice(name="功能(function)", value="function"),
			app_commands.Choice(name="遊戲(game)", value="game"),
			app_commands.Choice(name="擁有者(owner)", value="owner"),
			app_commands.Choice(name="計時器(timer)", value="timer"),
			app_commands.Choice(name="聖魂傳奇(hl)", value="hl"),
			app_commands.Choice(name="全部*(all)", value="all")
	])
	async def reload(self, interaction: discord.Interaction, 類別: app_commands.Choice[str]):
		if interaction.user.id not in [493411441832099861, 660099488228311050]:
			await interaction.response.send_message("你沒有權限使用此指令")
			return
		
		if 類別.value != "all":
			await self.bot.reload_extension(f"cmds.{類別.value}")
			await interaction.response.send_message(content=f"**{類別.name}**類別重新載入完成!",ephemeral=True)
			return
			
		for filename in os.listdir("./cmds"):
			if filename.endswith(".py"):
				await self.bot.reload_extension(f"cmds.{filename[:-3]}")

		await interaction.response.send_message(content=f"**所有類別**重新載入完成!",ephemeral=True)
			

	@app_commands.command(description='重新啟動')
	async def restart(self, interaction):
		if interaction.user.id not in [493411441832099861, 660099488228311050]:
			await interaction.response.send_message("你沒有權限使用此指令")
			return
		
		await interaction.response.send_message("重新啟動!")
		os.execv(sys.executable, ["python"] + sys.argv)
		

	@app_commands.command(description='獲取用戶資料')
	async def getdata(self, interaction: discord.Interaction, 用戶: discord.User):
		if interaction.user.id in [493411441832099861, 660099488228311050]:
			await interaction.response.send_message(f"> 用戶名稱：{用戶.name}\n> 用戶ID：{用戶.id}\n> 用戶頭像：{用戶.avatar.url}")
			

	@app_commands.command(name="test", description='測試用 LayoutView 排版')
	async def test(self, interaction: discord.Interaction):
		view = LayoutView()
		container = Container() 

		# 1. 先建立按鈕 (等等要作為附屬品)
		btn = Button(label="點擊測試", style=discord.ButtonStyle.primary)
		
		async def button_callback(btn_interaction: discord.Interaction):
			await btn_interaction.response.send_message("成功！按鈕作為附屬品運作正常！", ephemeral=True)
		btn.callback = button_callback

		# 2. 建立 Section，並直接將按鈕設為 accessory！
		# 這樣按鈕就會漂亮地排在文字的右邊
		text_section = Section(accessory=btn)
		
		text_section.add_item(TextDisplay(
			"## 🚀 LayoutView 測試成功！\n"
			"這是一個使用 Discord 最新 Components V2 排版的測試訊息。\n"
			"你看！右邊那顆按鈕就是這個區塊的 `accessory` (附屬品)。"
		))
		
		container.add_item(text_section) 
		view.add_item(container)

		await interaction.response.send_message(view=view)
		
	
	@app_commands.command(name="big_test", description='測試大型 LayoutView 綜合排版')
	async def big_test(self, interaction: discord.Interaction):
		# 1. 初始化主畫布與主容器
		view = LayoutView()
		container = Container()

		# ==========================================
		# 區塊 A：頂部歡迎橫幅 (純文字，沒有附屬品)
		# 👉 修正：不需要 Section，直接把 TextDisplay 加入 Container！
		# ==========================================
		container.add_item(TextDisplay(
			"## 🏰 歡迎來到伺服器中心\n"
			"這是一個使用 `LayoutView` 打造的大型互動面板。\n"
			"在這裡你可以查看最新資訊，並透過下方的按鈕進行互動。"
		))
		
		# 放入分隔線
		container.add_item(Separator())

		# ==========================================
		# 區塊 B：系統資訊 (有右側附屬品：重新整理按鈕)
		# 👉 正確寫法：因為有按鈕在右邊，所以必須用 Section 包起來
		# ==========================================
		refresh_btn = Button(label="重新整理", style=discord.ButtonStyle.secondary, emoji="🔄")
		
		async def refresh_callback(btn_interaction: discord.Interaction):
			await btn_interaction.response.send_message("資料已重新整理！(測試)", ephemeral=True)
		refresh_btn.callback = refresh_callback

		# 建立 Section，並指定附屬品
		info_section = Section(accessory=refresh_btn)
		info_section.add_item(TextDisplay(
			"### 📊 目前系統狀態\n"
			"* **機器人延遲**：`24ms`\n"
			"* **伺服器人數**：`1,024 人`\n"
			"* **語音伺服器**：`連線正常`"
		))
		container.add_item(info_section)

		# 再次放入分隔線
		container.add_item(Separator())

		# ==========================================
		# 區塊 C：底部動作列 (多顆按鈕並排)
		# ==========================================
		action_row = ActionRow()

		btn_agree = Button(label="我同意規則", style=discord.ButtonStyle.success, emoji="✅")
		async def agree_callback(btn_interaction: discord.Interaction):
			await btn_interaction.response.send_message("感謝你的同意！", ephemeral=True)
		btn_agree.callback = agree_callback

		btn_deny = Button(label="拒絕並退出", style=discord.ButtonStyle.danger, emoji="❌")
		async def deny_callback(btn_interaction: discord.Interaction):
			await btn_interaction.response.send_message("你已拒絕規則。", ephemeral=True)
		btn_deny.callback = deny_callback

		btn_link = Button(label="官方網站", style=discord.ButtonStyle.link, url="https://discord.com")

		action_row.add_item(btn_agree)
		action_row.add_item(btn_deny)
		action_row.add_item(btn_link)

		container.add_item(action_row)

		# ==========================================
		# 最終組裝與發送
		# ==========================================
		view.add_item(container)
		await interaction.response.send_message(view=view)


async def setup(bot):
	await bot.add_cog(Owner(bot))


