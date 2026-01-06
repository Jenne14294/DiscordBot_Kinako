import json
import math
import os
import random
import importlib
import AI_kinako
import discord

from datetime import datetime
from discord.ext import commands

path = "./jsonfile/data.json" 
default_deleted_path = "./deleted_files/template.json"
default_edited_path = "./edited_files/template.json"
default_guild_setting = "./guild_settings/template.json"

def reload_ai():
	importlib.reload(AI_kinako)

class AI_HelpMenu:
	def __init__(self):
		self.embed = discord.Embed(title="黃名子",description="所有權為 <@493411441832099861> 所有\n★為傑尼才可使用",color=0x3d993a)
		self.embed.add_field(name="**show(顯示)**", value="顯示可切換的角色", inline=True)
		self.embed.add_field(name="**list(紀錄)**",value="顯示可恢復的存檔",inline=True)
		self.embed.add_field(name="**clear(清除)**", value="清除當前的歷史紀錄", inline=True)
		self.embed.add_field(name="**restore(恢復) [檔案名稱]**", value="讀取指定的紀錄檔案", inline=True)
		self.embed.add_field(name="**export(導出) [名稱]**",value="儲存當前的歷史紀錄",inline=True)
		self.embed.add_field(name="**switch(切換) [角色ID]**", value="切換到指定的角色", inline=True)
		self.embed.add_field(name="**★reload**",value="重新載入 AI 功能",inline=True)

	def to_dict(self):
		return self.embed.to_dict()

class Event(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self,member):
		guild = member.guild

		path = f"./guild_settings/{guild.id}.json"
		with open(path, "r", encoding="utf8") as file:
			data = json.load(file)

		if guild.id == 808332107758698528:
			visit = guild.get_role(1100377865108856882)
			await member.add_roles(visit)

		channel = self.bot.get_channel(data["join_channel"])
		await channel.send(f"{member.mention} {data['join_message']}")
		
			
	@commands.Cog.listener()
	async def on_member_remove(self,member):
		guild = member.guild

		path = f"./guild_settings/{guild.id}.json"
		with open(path, "r", encoding="utf8") as file:
			data = json.load(file)

		channel = self.bot.get_channel(data["leave_channel"])
		await channel.send(f"{member.mention} {data['leave_message']}")


	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		with open(default_guild_setting, "r", encoding="utf8") as file:
			data = json.load(file)

		with open(f"./guild_settings/{guild.id}.json", "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		path = f"./guild_settings/{guild.id}.json"
		if os.path.exists(path):
			os.remove(path)

	@commands.Cog.listener()
	async def on_message(self, msg):
		user = msg.author
		try:
			if not user.bot:
				num = random.randint(1, 25) 
				emoji_list = [f"<:{emoji.name}:{emoji.id}>" for guild in self.bot.guilds for emoji in guild.emojis] 
				if num == 9 and not msg.author.bot: 
					await msg.add_reaction(random.choice(emoji_list))

				if msg.content.lower() == "wtf":
						await msg.channel.send("https://cdn.discordapp.com/emojis/588950160399269889.png?v=1")
						return

				elif msg.content.lower() == "hmmm":
					await msg.channel.send("<:Jenne_HMMM:1011160230844973086>")
					return

				elif msg.content in ["<@!808341883981791242>","<@808341883981791242>"]:
					if user.id == 493411441832099861:
						await msg.channel.send("わあ！ジェニーさんだよね")

					else:
						await msg.channel.send("ちーっす～(你好~)")
					
					return

				elif ":Jenne_play:" in msg.content:
					with open("./jsonfile/data.json", "r", encoding="utf8") as file:
						data = json.load(file)

					await msg.channel.send(random.choice(data["play_message"]))
					return

				if self.bot.user in msg.mentions:
					try:
						if msg.content.startswith("<@808341883981791242>"):
							input_text = msg.content.split(" ", 1)
							query = input_text[1]
						else:
							query = msg.content

						if query == "reload" and user.id in [493411441832099861, 660099488228311050]:
							await msg.reply("AI功能已重新載入")
							reload_ai()
							return
						
						if query in ['show', '顯示']:
							files = os.listdir("./AI_functions/characters")
							characters = ""
							for file in files:
								if "rules" not in file:
									characters = characters + " " + file[:-3] + " &"

							characters = characters[:-1]

							if characters != "":
								await msg.reply(f"可用角色：{characters}")

							else:
								await msg.reply("沒有可用的角色")

							return
						
						if query in ['list', "紀錄"]:
							files = os.listdir("./AI_functions/output_data")
							sorted_files = sorted(files, key=lambda x: int(x.split("_")[0]))
							data = ""
							for file in sorted_files:
								data = data + " " + file[:-5] + " &"

							data = data[:-1]

							if data != "":
								await msg.reply(f"可用紀錄：{data}")

							else:
								await msg.reply("沒有可用的紀錄")

							return
						
						if query in ['help', '功能']:
							embed = AI_HelpMenu()
							await msg.reply(embed=embed)
							return
						
						# image = msg.attachments[0].url if msg.attachments else None
						image = None
						response = AI_kinako.ask_ai(query, image, user.id)

						await msg.reply(response)
					except Exception as e:
						print(e)
						await msg.reply("人家不太懂你的意思呢 (｡•́︿•̀｡)")

					return

			else:
				channel = self.bot.get_channel(809294389795880971)
				server_announce = await channel.fetch_message(886199654058962975)
				if "伺服器已開啟" in msg.content:
					await server_announce.edit(content="> 伺服器路線:直連\n> 目前狀態:開啟\n> IP:DestroyGeneration.ddns.net\n> Port:25565\n> 版本:隨意(通常為最新版)\n> 平台:Java&Bedrock")
					return
				
				elif "伺服器已關閉" in msg.content:
					await server_announce.edit(content="> 伺服器路線:直連\n> 目前狀態:關閉\n> IP:DestroyGeneration.ddns.net\n> Port:25565\n> 版本:隨意(通常為最新版)\n> 平台:Java&Bedrock")
					return
		except:
			pass


	@commands.Cog.listener()
	async def on_raw_reaction_add(self,payload):
		guild = self.bot.get_guild(payload.guild_id)
		channel = self.bot.get_channel(payload.channel_id)
		user = guild.get_member(payload.user_id)
		msg = await channel.fetch_message(payload.message_id)
		reaction = payload.emoji.name

		Sandbox = guild.get_role(815216596825014272)
		PVP = guild.get_role(815216698856439848)
		Music = guild.get_role(851377111938891776)
		RPG = guild.get_role(851800108793462804)
		tower = guild.get_role(1458092136468582532)
		Growth = guild.get_role(1009416690213326899)

		if msg.id == 815219247382003734 and reaction == '🌏':
			await user.add_roles(Sandbox)

		elif msg.id == 815219247382003734 and reaction == '⚔':	
			await user.add_roles(PVP)

		elif msg.id == 815219247382003734 and reaction == '🎶':	
			await user.add_roles(Music)

		elif msg.id == 815219247382003734 and reaction == '🧛‍♀️':	
			await user.add_roles(RPG)

		elif msg.id == 815219247382003734 and reaction == '🏰':
			await user.add_roles(tower)

		elif msg.id == 815219247382003734 and reaction == '🌿':	
			await user.add_roles(Growth)



	@commands.Cog.listener()
	async def on_raw_reaction_remove(self,payload):
		guild = self.bot.get_guild(payload.guild_id)
		channel = self.bot.get_channel(payload.channel_id)
		user = guild.get_member(payload.user_id)
		msg = await channel.fetch_message(payload.message_id)
		reaction = payload.emoji.name

		Sandbox = guild.get_role(815216596825014272)
		PVP = guild.get_role(815216698856439848)
		Music = guild.get_role(851377111938891776)
		RPG = guild.get_role(851800108793462804)
		tower = guild.get_role(1458092136468582532)
		Growth = guild.get_role(1009416690213326899)
		
		if msg.id == 815219247382003734 and reaction == '🌏':
			await user.remove_roles(Sandbox)

		elif msg.id == 815219247382003734 and reaction == '⚔':	
			await user.remove_roles(PVP)

		elif msg.id == 815219247382003734 and reaction == '🎶':	
			await user.remove_roles(Music)

		elif msg.id == 815219247382003734 and reaction == '🧛‍♀️':	
			await user.remove_roles(RPG)

		elif msg.id == 815219247382003734 and reaction == '🏰':
			await user.remove_roles(tower)

		elif msg.id == 815219247382003734 and reaction == '🌿':	
			await user.remove_roles(Growth)


	@commands.Cog.listener()
	async def on_message_delete(self,msg):
		if msg.author.bot:
			return
		
		deleted = self.bot.get_channel(1109828448626679888)
		path = f"./deleted_files/{msg.guild.id}.json"

		attachments = [msg.attachments[i].proxy_url for i in range(len(msg.attachments))]
		content = msg.content if msg.content != "" else ""
		author = msg.author.name
		channel = msg.channel.id
		time = datetime.now().strftime("%m-%d %H:%M:%S")

		if os.path.exists(path):
			with open(path,"r",encoding="utf8") as file:
				data = json.load(file)
		
		else:
			with open(default_deleted_path, "r", encoding="utf8") as file:
				data = json.load(file)

		if len(data["author"]) == 5:
			data["author"].pop(0)
			data["content"].pop(0)
			data["channel"].pop(0)
			data["attachments"].pop(0)
			data["time"].pop(0)

		data["author"].append(author)
		data["content"].append(content)
		data["channel"].append(channel)
		data["attachments"].append(attachments)
		data["time"].append(time)
			
		with open(path, "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)

		fromcha = msg.channel.id
		await deleted.send(f"訊息：{msg.content}\n傳送者：{msg.author.name}\n附件：{attachments}\n頻道：<#{fromcha}>\n時間：{time}")

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if before.author.bot:
			return
		
		if before.content == after.content:
			return
		
		edited = self.bot.get_channel(1109828448626679888)
		path = f"./edited_files/{before.guild.id}.json"

		Bcontent = before.content if before.content != "" else ""
		Acontent = after.content if after.content != "" else ""
		author = before.author.name
		channel = before.channel.id
		date = datetime.now().strftime("%m-%d %H:%M:%S")
		BID = before.id
		
		if os.path.exists(path):
			with open(path,"r",encoding="utf8") as file:
				data = json.load(file)
		
		else:
			with open(default_edited_path, "r", encoding="utf8") as file:
				data = json.load(file)

		if len(data["author"]) > 4:
			data["BID"].pop(0)
			data["author"].pop(0)
			data["Bcontent"].pop(0)
			data["Acontent"].pop(0)
			data["channel"].pop(0)
			data["date"].pop(0)

		if BID not in data["BID"]:
			data["BID"].append(BID)
			data["author"].append(author)
			data["Bcontent"].append(Bcontent)
			data["Acontent"].append([Acontent])
			data["channel"].append(channel)
			data["date"].append(date)

		else:
			index = data["BID"].index(BID)
			
			if len(data["Acontent"][index]) < 21:
				data["Acontent"][index].append(Acontent)
			
		with open(path, "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)

		fromcha = before.channel.id
		await edited.send(f"編輯前訊息：{Bcontent}\n編輯後訊息：{Acontent}\n傳送者：{author}\n頻道：<#{fromcha}>\n時間：{date}")

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		

		if member.bot:
			return
		
		voice_guild = member.guild
		voice = voice_guild.voice_client

		if not voice:
			return
		
		path = f"./audio_files/{voice_guild.id}.json"

		with open(path, "r", encoding="utf8") as file:
			data = json.load(file)

		channel = voice.channel


		if before.channel == channel or after.channel == channel:
			voice_channel = before.channel if before.channel != None else after.channel if after.channel != None else None
			max_player_count = len([listener for listener in voice_channel.members if not listener.bot])

			data["max_vote"] = math.ceil(max_player_count / 2)

			if len(data["vote"]) >= data["max_vote"]:
				voice.stop()
				data["vote"] = []
				data["loop"] = 0

			with open(path, "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)
		
async def setup(bot):
	await bot.add_cog(Event(bot))