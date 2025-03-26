import discord
import json
import os
import asyncio

from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput

class SnipeFunction:
	class ShowInfo:
		def __init__(self, data, n):

			author = data["author"][n - 1]
			content = data["content"][n - 1]
			channel = data["channel"][n - 1]
			attachments = data["attachments"][n - 1]
			time = data["time"][n - 1]
			x = len(data["author"])

			self.embed = discord.Embed(title=f"被刪除的訊息(第 {n} 則 / 共 {x} 則)", description="擷取結果", color=0x3d993a)
			self.embed.add_field(name="訊息作者", value=author, inline=True)
			self.embed.add_field(name="訊息內容", value=content, inline=True)
			self.embed.add_field(name="訊息頻道", value=f"<#{channel}>", inline=True)
			self.embed.add_field(name="訊息附件", value=attachments, inline=True)
			self.embed.add_field(name="訊息時間", value=time, inline=True)

		def to_dict(self):
			return self.embed.to_dict()
		
	class changePage(discord.ui.View):
		def __init__(self, timeout: float | None = 180):
			super().__init__(timeout = timeout)

			prev = discord.ui.Button(label="上一則", style=discord.ButtonStyle.primary, custom_id="prev", emoji="⬅️")
			next = discord.ui.Button(label="下一則", style=discord.ButtonStyle.primary, custom_id="next", emoji="➡️")

			async def change_page(interaction:discord.Interaction):
				await interaction.response.defer()
				function = interaction.data["custom_id"]
				path = f"./deleted_files/{interaction.guild.id}.json"

				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)

				if function == "prev" and data["page"] > 1:
					data["page"] -= 1

				elif function == "next" and data["page"] < len(data["content"]):
					data["page"] += 1

				with open(path, "w", encoding="utf8") as file:
					json.dump(data, file, indent=4, ensure_ascii=False)

				page = data["page"]

				embed = SnipeFunction.ShowInfo(data, page)
				view = SnipeFunction.changePage()

				await interaction.edit_original_response(embed=embed, view=view)

			self.add_item(prev)
			self.add_item(next)

			prev.callback = change_page
			next.callback = change_page

class HistoryFunction:
	class ShowInfo:
		def __init__(self, data, n):

			author = data["author"][n - 1]
			Bcontent = data["Bcontent"][n - 1]
			Acontent = data["Acontent"][n - 1]
			channel = data["channel"][n - 1]
			date = data["date"][n - 1]
			x = len(data["author"])

			self.embed = discord.Embed(title=f"被編輯的訊息(第 {n} 則 / 共 {x} 則)", description="擷取結果", color=0x3d993a)
			self.embed.add_field(name="訊息作者", value=author, inline=True)
			self.embed.add_field(name="訊息頻道", value=f"<#{channel}>", inline=True)
			self.embed.add_field(name="訊息時間", value=date, inline=True)
			self.embed.add_field(name="編輯前內容", value=Bcontent, inline=True)

			for msg in Acontent:
				self.embed.add_field(name="編輯後訊息", value=msg, inline=True)
			

		def to_dict(self):
			return self.embed.to_dict()
		
	class changePage(discord.ui.View):
		def __init__(self, timeout: float | None = 180):
			super().__init__(timeout = timeout)

			prev = discord.ui.Button(label="上一則", style=discord.ButtonStyle.primary, custom_id="prev", emoji="⬅️")
			next = discord.ui.Button(label="下一則", style=discord.ButtonStyle.primary, custom_id="next", emoji="➡️")

			async def change_page(interaction:discord.Interaction):
				await interaction.response.defer()
				function = interaction.data["custom_id"]
				path = f"./edited_files/{interaction.guild.id}.json"

				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)

				if function == "prev" and data["page"] > 1:
					data["page"] -= 1

				elif function == "next" and data["page"] < len(data["BID"]):
					data["page"] += 1

				with open(path, "w", encoding="utf8") as file:
					json.dump(data, file, indent=4, ensure_ascii=False)

				page = data["page"]

				embed = HistoryFunction.ShowInfo(data, page)
				view = HistoryFunction.changePage()

				await interaction.edit_original_response(embed=embed, view=view)

			self.add_item(prev)
			self.add_item(next)

			prev.callback = change_page
			next.callback = change_page

class SettingFunction:
	class join_settings(Modal, title = "加入相關設定"):
		channel = TextInput(label="加入頻道", placeholder="請輸入頻道ID", style=discord.TextStyle.short, custom_id="channel", required=True)
		message = TextInput(label="加入訊息", placeholder="請輸入加入訊息", style=discord.TextStyle.short, custom_id="message", required=True)

		async def on_submit(self, interaction: discord.Interaction):
			channel = int(self.channel.value)
			message = self.message.value

			with open(f"./guild_settings/{interaction.guild_id}.json", "r", encoding="utf8") as file:
				data = json.load(file)

			data["join_channel"] = channel
			data["join_message"] = message

			with open(f"./guild_settings/{interaction.guild_id}.json", "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)
				
			await interaction.response.send_message("加入設定已經儲存！")
	class leave_settings(Modal, title = "離開相關設定"):
		channel = TextInput(label="離開頻道", placeholder="請輸入頻道ID", style=discord.TextStyle.short, custom_id="channel", required=True)
		message = TextInput(label="離開訊息", placeholder="請輸入離開訊息", style=discord.TextStyle.short, custom_id="message", required=True)

		async def on_submit(self, interaction: discord.Interaction):
			channel = int(self.channel.value)
			message = self.message.value

			with open(f"./guild_settings/{interaction.guild_id}.json", "r", encoding="utf8") as file:
				data = json.load(file)

			data["leave_channel"] = channel
			data["leave_message"] = message

			with open(f"./guild_settings/{interaction.guild_id}.json", "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)

			await interaction.response.send_message("離開設定已經儲存！")

	class music_settings(Modal, title = "音樂功能設定"):
		time = TextInput(label="自動斷線時間", placeholder="請輸入時間(秒數)", style=discord.TextStyle.short, custom_id="time", required=True)

		async def on_submit(self, interaction: discord.Interaction):
			time = int(self.time.value)

			with open(f"./guild_settings/{interaction.guild_id}.json", "r", encoding="utf8") as file:
				data = json.load(file)

			data["AD_time"] = time

			with open(f"./guild_settings/{interaction.guild_id}.json", "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)

			await interaction.response.send_message("音樂設定已經儲存！")

	class greet_settings(Modal, title = "早安相關設定"):
		channel = TextInput(label="早安頻道", placeholder="請輸入頻道ID", style=discord.TextStyle.short, custom_id="channel", required=True)
		message = TextInput(label="早安訊息", placeholder="請輸入早安訊息", style=discord.TextStyle.short, custom_id="message")

		async def on_submit(self, interaction: discord.Interaction):
			channel = int(self.channel.value)
			message = self.message.value

			with open(f"./guild_settings/{interaction.guild_id}.json", "r", encoding="utf8") as file:
				data = json.load(file)

			data["greet_channel"] = channel
			data["greet_message"] = message

			with open(f"./guild_settings/{interaction.guild_id}.json", "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)

			await interaction.response.send_message("早安設定已經儲存！")

class Admin(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@app_commands.command(description="設定機器人")
	@app_commands.choices(類別=[
		app_commands.Choice(name="加入設定(join_settings)",value=1),
		app_commands.Choice(name="離開設定(leave_settings)",value=2),
		app_commands.Choice(name="音樂設定(music_settings)",value=3),
		app_commands.Choice(name="早安設定(greet_settings)",value=4),
	])
	@commands.has_permissions(administrator=True)
	async def settings(self, interaction:discord.Interaction, 類別:app_commands.Choice[int]):
		if 類別.value == 1:
			modal = SettingFunction.join_settings()
			await interaction.response.send_modal(modal)

		elif 類別.value == 2:
			modal = SettingFunction.leave_settings()
			await interaction.response.send_modal(modal)

		elif 類別.value == 3:
			modal = SettingFunction.music_settings()
			await interaction.response.send_modal(modal)

		elif 類別.value == 4:
			modal = SettingFunction.greet_settings()
			await interaction.response.send_modal(modal)
		
	
	@app_commands.command(description="擷取最後五則被刪除的訊息")
	@commands.has_permissions(view_audit_log=True)
	async def snipe(self, interaction:discord.Interaction):
		path = f"./deleted_files/{interaction.guild.id}.json"

		if not os.path.exists(path):
			await interaction.response.send_message("目前沒有被刪除的訊息")
			return

		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)

		if data["author"] == []:
			await interaction.response.send_message("目前沒有被刪除的訊息")
			return
		
		embed = SnipeFunction.ShowInfo(data, data["page"])
		view = SnipeFunction.changePage()
			
		await interaction.response.send_message(embed=embed, view=view)

	@app_commands.command(description="擷取最後五則被編輯的訊息")
	@commands.has_permissions(view_audit_log=True)
	async def history(self, interaction:discord.Interaction):
		path = f"./edited_files/{interaction.guild.id}.json"

		if not os.path.exists(path):
			await interaction.response.send_message("目前沒有被編輯的訊息")
			return

		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)

		if data["author"] == []:
			await interaction.response.send_message("目前沒有被編輯的訊息")
			return
		
		embed = HistoryFunction.ShowInfo(data, data["page"])
		view = HistoryFunction.changePage()
			
		await interaction.response.send_message(embed=embed, view=view)


	@app_commands.command(description="清除訊息")
	@app_commands.describe(目標="輸入目標字/用戶ID",數量="不建議超過200")
	@app_commands.choices(模式=[
		app_commands.Choice(name="預設刪除",value=1),
		app_commands.Choice(name="以字刪除",value=2),
		app_commands.Choice(name="以用戶刪除",value=3),
	])
	@commands.has_permissions(manage_messages=True)
	async def clear(self,interaction:discord.Interaction,數量:str,模式:app_commands.Choice[int],*,目標:str=None):
		await interaction.response.send_message("正在刪除訊息...")
		counter = 0
		channel = interaction.channel

		if int(數量) <= 0:
			await interaction.response.send_message("請輸入要刪除的數量")
			return
			
		if 模式.value == 1:
			deleted = await channel.purge(limit=int(數量) + 1)
			await interaction.channel.send(content=f"已刪除 {len(deleted)} 則訊息")

		elif 模式.value == 2:
			if not 目標:
				await interaction.edit_original_response(content="請輸入要刪除的訊息關鍵目標")
				return

			async for message in channel.history(limit=9999):
				if counter > int(數量):
					break
				
				if 目標 in message.content:
					await message.delete()
					counter = counter + 1
					await asyncio.sleep(0.5)
					
			await interaction.channel.send(content=f"已刪除 {counter} 則有關 {目標} 的訊息")
				
		elif 模式.value == 3:
			if not 目標:
				await interaction.edit_original_response(content="請輸入要刪除的訊息關鍵目標")
				return

			if 目標.startswith("<@") and 目標.endswith(">"):
				target = 目標[2:-1]

			async for message in channel.history(limit=9999):
				if counter > int(數量):
					break

				if message.author.id == int(target):
					await message.delete()
					counter += 1
					await asyncio.sleep(0.5)

			await interaction.channel.send(content=f"已刪除 {counter} 則來自 {目標} 的訊息")
			

	@app_commands.command(description="踢除某人")
	@app_commands.choices(踢除模式=[
		app_commands.Choice(name="預設踢除",value=1),
		app_commands.Choice(name="尚未驗證",value=2),
	])
	@commands.has_permissions(kick_members=True)
	async def kick(self, interaction:discord.Interaction, 踢除模式:app_commands.Choice[int], 成員:discord.User=None, 原因:str=None):
		if 踢除模式.value == 1:
			if not 成員:
				await interaction.response.send_message("踢出目標不能為空")
				return

			if 成員 not in interaction.guild.members:
				await interaction.response.send_message(f"{成員} 不存在!")
				return
			
			await 成員.send(f"你因為 {原因} 而被踢出 {interaction.guild.name}")
			await interaction.guild.kick(成員)
			await interaction.response.send_message(f"{成員} 已被踢出！")
			
		else:
			counter = 0
			for 成員 in interaction.guild.members:
				if "訪客" in 成員.roles.name:
					await interaction.guild.kick(成員)
					counter += 1
			await interaction.response.send_message(f"{counter} 位成員被踢出")


	@app_commands.command(description="封鎖某人")
	@commands.has_permissions(ban_members=True)
	async def ban(self, interaction:discord.Interaction,成員:discord.User,原因:str=None):
		if not 成員:
			await interaction.response.send_message("踢出目標不能為空")
			return

		if 成員 not in interaction.guild.members:
			await interaction.response.send_message(f"{成員} 不存在!")
			return
		
		guild = interaction.guild
		await interaction.guild.ban(成員)
		await 成員.send(f"你因為 {原因} 而被 {guild} 封鎖")
		

async def setup(bot):
	await bot.add_cog(Admin(bot))