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
from discord.ui import Button, View, Select
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
			

	@app_commands.command(description='測試用')
	async def test(self, interaction: discord.Interaction):
		pass
		


async def setup(bot):
	await bot.add_cog(Owner(bot))


