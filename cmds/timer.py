import scrapetube
import json
import discord
import os 
import random
import requests
import math
import AI_title
import dbFunction
import datetime
import re
import glob

from discord.ext import commands, tasks
from discord.utils import get
from discord.ui import Button, Modal, TextInput, View, Select
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from pytube import Playlist
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
from cmds.economy import register, reload_db


temp_deleted = "./deleted_files"
temp_edited = "./edited_files"
dpath = "./jsonfile/data.json"

def clean_tempfile():
	# 刪除暫存檔
	for f in glob.glob("./audio_files/temp_*"):
		os.remove(f)

class VerifyFunction:
	class ModalClass(Modal, title = "設定名稱"):
		nick = TextInput(label = "暱稱", placeholder="該怎麼稱呼你?", style=discord.TextStyle.short, custom_id="nick", required=True)

		async def on_submit(self, interaction: discord.Interaction):
			reload_db()
			visit = interaction.guild.get_role(1100377865108856882)
			await interaction.user.remove_roles(visit)
			await interaction.user.edit(nick=self.nick.value)

			data = register()
			user_data = dbFunction.get_economy(interaction.user.id)

			if not user_data:
				dbFunction.register(interaction.user, data)

			return

	class VerifyButton(View):
		def __init__(self):
			super().__init__(timeout = None)

			async def verify_function(interaction:discord.Interaction):
				await interaction.response.send_modal(VerifyFunction.ModalClass())

			self.verify = Button(label="點我驗證!", style=discord.ButtonStyle.primary, custom_id="verify")
			self.verify.callback = verify_function
			self.add_item(self.verify)

class MusicFunction:
	default_path = './audio_files'

	YDL_OPTIONS = {
					"format": "bestaudio/best",
					"extractaudio": True,
					"audioformat": "mp3",
					"outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
					"restrictfilenames": True,
					"noplaylist": True,
					"nocheckcertificate": True,
					"ignoreerrors": False,
					"logtostderr": False,
					"quiet": True,
					"no_warnings": True,
					"default_search": "auto",
					"source_address": "0.0.0.0",
					"force-ipv4": True,
					"cachedir": False,
					"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
	}

	FFMPEG_OPTIONS = {
			"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
			"options": "-vn"
	}
	
	ffmpeg = "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"

	

	def show_information(self, url, guild_id):
		# 🔹 Bilibili
		if "bilibili.com" in url:
			bilibili_opts = {
				'format': 'bestaudio/best',  # 取得最佳音訊格式
				'quiet': True,
				'noplaylist': True,
				'outtmpl': os.path.join("./audio_files", f"temp_{guild_id}.%(ext)s"),   # 以 guild.id 區分檔案
				'postprocessors': [],         # 不轉 mp3
			}

			clean_tempfile()

			with YoutubeDL(bilibili_opts) as ydl:
				info = ydl.extract_info(url, download=True)

			# 正確取得實際檔名
			file_path = os.path.abspath(f"./audio_files/temp_{guild_id}.{info['ext']}")


			# 回傳整理後資訊
			return {
				"title": info.get("title", "未知標題"),
				"thumbnail": info.get("thumbnail", None),
				"duration": info.get("duration", 0),
				"url": file_path
			}

		# 🔹 YouTube 或其他網站
		else:
			with YoutubeDL(MusicFunction.YDL_OPTIONS) as ydl:
				info = ydl.extract_info(url, download=False)

			return info
	
	def get_title(self,url: str) -> str:
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
						"AppleWebKit/537.36 (KHTML, like Gecko) "
						"Chrome/118.0.0.0 Safari/537.36"
		}

		try:
			r = requests.get(url, headers=headers, timeout=10)
			r.raise_for_status()
		except Exception as e:
			return f"[錯誤] 無法連線: {e}"

		html = r.text
		title = "未知標題"

		# YouTube 標題擷取
		if "youtube.com" in url or "youtu.be" in url:
			match = re.search(r'"title":"(.*?)"', html)
			if match:
				title = match.group(1).encode('utf-8').decode('unicode_escape')  # JSON escape 才 decode

		# Bilibili 標題擷取
		if "bilibili.com" in url:
			# 直接抓 <title> 標籤或 JSON 內 title
			match = re.search(r'<title>(.*?)</title>', html, re.S)
			if match:
				title = match.group(1).strip()
			else:
				# fallback: JSON 格式 title
				match = re.search(r'"title":"(.*?)"', html)
				if match:
					title = match.group(1).encode('utf-8').decode('unicode_escape')

		return title
	
	def get_lyrics(self, title):
		client_access_token = "aW0PCZtUaF6ol8tBEFw6iAQ0dYakXRLpb_1nYzoOJBnAIbzctmdBK7c3IvcvE5Hs"
		url = f"http://api.genius.com/search?q={title}&access_token={client_access_token}"

		try:
			response = requests.get(url)
			json_data = response.json()

			song = json_data['response']['hits'][0]['result']['relationships_index_url']
			return song
		except Exception as e:
			print(e)
			return None

	
	def check_permission(self, interaction):
		if not interaction.user.voice:
			return False
		
		if interaction.guild.voice_client.channel != interaction.user.voice.channel:
			return False
		
		return True

	class Information:
		def __init__(self, data, info, statusText):
			seconds = int(info["duration"] % 60)
			minutes = (info["duration"] - seconds) // 60
			status = "暫停播放" if data["pause"] == 1 else "一般播放" if data["pause"] == 0 and data["loop"] == 0 else "循環播放" if data["loop"] == 1 else ""
			volume = data["volume"]

			self.embed = discord.Embed(title="現在正在播放",description="",color=0x3d993a)
			self.embed.set_thumbnail(url=info["thumbnail"])
			self.embed.add_field(name="**音樂標題**", value=info["title"], inline=False)
			self.embed.add_field(name="**音樂點歌人**",value=data["nowplayer"],inline=False)
			self.embed.add_field(name="**音樂網址**",value=data["nowurl"],inline=False)
			self.embed.add_field(name="**音樂時長**", value=f"{minutes} 分 {seconds} 秒", inline=True)
			self.embed.add_field(name="**音樂音量**", value=f"{round(volume * 100)} %", inline=True)
			self.embed.add_field(name="**開始時間**", value=data["play_time"], inline=True)
			self.embed.add_field(name="**目前狀態**", value=status, inline=True)
			self.embed.add_field(name="**跳過人數**", value=f"{len(data['vote'])} / {data['max_vote']}", inline=True)
			self.embed.add_field(name="**狀態訊息**", value=statusText, inline=False)

		def to_dict(self):
			return self.embed.to_dict()
		
	class MusicButton(View):
		def __init__(self):
			super().__init__(timeout = None)


		@discord.ui.button(
			label = "播放/暫停",
			style = discord.ButtonStyle.primary,
			emoji = "⏯️"
			)
		async def play_or_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()
			path = f"./audio_files/{interaction.guild_id}.json"
			voice = interaction.guild.voice_client

			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return

			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			text = await interaction.channel.fetch_message(data["text"])

			if data["nowplayer"] != interaction.user.name:
				statusText = f"**{interaction.user.name}** 無法暫停/播放此音樂"

			else:
				status = "一般播放" if data["loop"] == 0 else "循環播放"

				if data["pause"] == 0:
					voice.pause()
					data["pause"] = 1
					statusText = f"音樂已被 **{interaction.user.name}** 暫停播放"
					status = f"暫停播放"

				else:
					voice.resume()
					data["pause"] = 0
					statusText = f"音樂已被 **{interaction.user.name}** 繼續播放"

			dict = text.embeds[0].to_dict()
			dict['fields'][-1]['value'] = statusText
			dict['fields'][-3]['value'] = status
			embed = discord.Embed.from_dict(dict)
			view = MusicFunction.MusicButton()
			
			await interaction.edit_original_response(embed=embed, view=view)

			with open(path, "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)

		@discord.ui.button(
			label = "檢視歌單",
			style = discord.ButtonStyle.primary,
			emoji = "📃"
			)
		async def queue(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()
			path = f"./audio_files/{interaction.guild_id}.json"

			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			embed = MusicFunction.QueueFunction.QueueInfo(data)
			view = MusicFunction.QueueFunction.QueueButton(data)

			await interaction.edit_original_response(embed=embed, view=view)

		@discord.ui.button(
			label = "跳過音樂",
			style = discord.ButtonStyle.primary,
			emoji = "⏭️"
			)
		async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()

			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return

			path = f"./audio_files/{interaction.guild_id}.json"
			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			vote = data["vote"]
			Max = data["max_vote"]
			player = data["nowplayer"]
			channel = interaction.channel
			text = await channel.fetch_message(data["text"])
			voice = interaction.guild.voice_client

			if not voice.is_playing():
				return
			
			if interaction.user.name == player:
				voice.stop()
				statusText = f"**{player}** 跳過當前音樂"
				data["vote"] = []
				data["loop"] = 0
			
			else:
				if not interaction.user.name in vote:
					data["vote"].append(interaction.user.name)
					vote = data["vote"]
					statusText = ""

					if len(vote) >= Max:
						statusText = "音樂已被跳過"
						voice.stop()
						data["vote"] = []
						data["loop"] = 0
						
				else:
					statusText = "你已經投票跳過這首歌了"

			with open(path,"w",encoding="utf8") as file:
				json.dump(data,file,indent=4)

			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			votecount = len(data["vote"])
			Max = data["max_vote"]

			status = f"{votecount} / {Max}"
			dict = text.embeds[0].to_dict()
			dict['fields'][-1]['value'] = statusText
			dict['fields'][-2]['value'] = status
			embed = discord.Embed.from_dict(dict)
			view = MusicFunction.MusicButton()
			await interaction.edit_original_response(embed=embed, view=view)

		@discord.ui.button(
			label = "循環播放",
			style = discord.ButtonStyle.primary,
			emoji = "🔁"
			)
		async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()

			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return
			
			path = f"./audio_files/{interaction.guild_id}.json"
			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			text = await interaction.channel.fetch_message(data["text"])

			if data["nowplayer"] != interaction.user.name:
				statusText = f"**{interaction.user.name}** 無法循環播放此音樂"

			else:
				status = "一般播放" if data["loop"] == 0 else "循環播放"

				if data["loop"] == 0:
					data["loop"] = 1
					statusText = f"音樂已被 **{interaction.user.name}** 循環播放"
					status = f"循環播放"

				else:
					data["loop"] = 0
					statusText = f"音樂已被 **{interaction.user.name}** 普通播放"

				with open(path, "w", encoding="utf8") as file:
					json.dump(data, file, indent=4, ensure_ascii=False)

			dict = text.embeds[0].to_dict()
			dict['fields'][-1]['value'] = statusText
			dict['fields'][-3]['value'] = status
			embed = discord.Embed.from_dict(dict)
			view = MusicFunction.MusicButton()
			
			await interaction.edit_original_response(embed=embed, view=view)

		@discord.ui.button(
			label = "隨機播放",
			style = discord.ButtonStyle.primary,
			emoji = "🔀"
			)
		async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()

			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return

			path = f"./audio_files/{interaction.guild_id}.json"
			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			text = await interaction.channel.fetch_message(data["text"])

			url = data["url"]
			player = data["player"]
			combined = list(zip(url, player))
			random.shuffle(combined)
			url, player = zip(*combined)

			data["url"] = url
			data["player"] = player

			with open(path, "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)

			dict = text.embeds[0].to_dict()
			dict['fields'][-1]['value'] = "播放清單已重新排序"
			embed = discord.Embed.from_dict(dict)
			view = MusicFunction.MusicButton()
			
			await interaction.edit_original_response(embed=embed, view=view)

		@discord.ui.button(
			label = "查看歌詞",
			style = discord.ButtonStyle.primary,
			emoji = "🎶"
			)
		async def show_lyrics(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()

			path = f"./audio_files/{interaction.guild_id}.json"

			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			title = AI_title.ask_ai(f"{MusicFunction.get_title(self, data['nowurl'])}\n給我這首歌的歌名，只要歌名就好")
			lyrics_url = MusicFunction.get_lyrics(self, title)
			statusText = f"歌詞網址：{lyrics_url}\n**此功能正在測試中，可能會有些許錯誤**" if lyrics_url != None else "找不到歌詞!"

			channel = interaction.channel
			text = await channel.fetch_message(data["text"])

			dict = text.embeds[0].to_dict()
			dict['fields'][-1]['value'] = statusText
			embed = discord.Embed.from_dict(dict)
			view = MusicFunction.MusicButton()

			await interaction.edit_original_response(embed=embed, view=view)

		@discord.ui.button(
			label = "變更音量",
			style = discord.ButtonStyle.primary,
			emoji = "🔉"
			)
		async def volume(self, interaction: discord.Interaction, button: discord.ui.Button):
			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return
			
			modal = MusicFunction.change_volume()
			await interaction.response.send_modal(modal)

		@discord.ui.button(
			label = "新增歌曲",
			style = discord.ButtonStyle.primary,
			emoji = "▶️"
			)
		async def add_song(self, interaction: discord.Interaction, button: discord.ui.Button):
			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return
			
			modal = MusicFunction.add_song()
			await interaction.response.send_modal(modal)

		@discord.ui.button(
			label = "離開語音",
			style = discord.ButtonStyle.danger,
			emoji = "🚫",
			row = 2
			)
		async def leave_voice(self, interaction: discord.Interaction, button: discord.ui.Button):
			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return
			
			await interaction.response.defer()
			view = MusicFunction.ExitButton()

			await interaction.edit_original_response(view=view)

	class ExitButton(View):
		def __init__(self):
			super().__init__(timeout = None)

		@discord.ui.button(
			label = "確認離開",
			style = discord.ButtonStyle.danger,
			emoji = "🚫"
			)
		async def leave_confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return

			await interaction.response.defer()
			path = f"./audio_files/{interaction.guild_id}.json"
			os.remove(path)
			clean_tempfile()
			voice = interaction.guild.voice_client
			await voice.disconnect()
			await interaction.edit_original_response(content=f"{interaction.user.mention} 我已經離開了唷~", embed=None, view=None)

		@discord.ui.button(
			label = "返回",
			style = discord.ButtonStyle.secondary,
			emoji = "↩️"
			)
		async def leave_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
			permission = MusicFunction.check_permission(self, interaction)
			if not permission:
				return

			await interaction.response.defer()
			view = MusicFunction.MusicButton()
			await interaction.edit_original_response(view=view)

	class add_song(Modal, title = "新增歌曲"):
		search = TextInput(label="影片網址(僅限YT，其他無法播放)", placeholder="請輸入 影片網址 或 關鍵字", style=discord.TextStyle.short, custom_id="search", required=True)

		async def on_submit(self, interaction: discord.Interaction):
			await interaction.response.defer()
			path = f"./audio_files/{interaction.guild_id}.json"
								
			with open(path,"r",encoding="utf8") as file:
				data = json.load(file)

			channel = interaction.channel
			text = await channel.fetch_message(data["text"])

			async def cancel_choose(interaction):
				await interaction.response.defer()

				path = f"./audio_files/{interaction.guild_id}.json"
				with open(path,"r",encoding="utf8") as file:
					data = json.load(file)

				info = MusicFunction.show_information(self, data["nowurl"], interaction.guild_id)
				statusText = "已取消選歌"

				embed = MusicFunction.Information(data, info, statusText)
				view = MusicFunction.MusicButton()

				await interaction.edit_original_response(embed=embed, view=view)

			async def choose_video(item:discord.Interaction):
				urlList = []					
				path = f"./audio_files/{interaction.guild_id}.json"
								
				with open(path,"r",encoding="utf8") as file:
					data = json.load(file)

				channel = interaction.channel
				text = await channel.fetch_message(data["text"])

				try:
					url = item.data["custom_id"]
					urlList.append(url)
					player_list = [interaction.user.name]

					TITLE = MusicFunction.get_title(self, url)

				except:
					url = item
					
					if "list" in url:
						urlList = list(Playlist(url))
						TITLE = Playlist(url).title
						player_list = [interaction.user.name] * len(urlList)
						
					else:
						urlList.append(url)
						player_list = [interaction.user.name]

						TITLE = MusicFunction.get_title(self, url)

				statusText = f"***{TITLE}*** 已經新增到歌單了"
				
				data["url"].extend(urlList)
				data["player"].extend(player_list)

				with open(path,"w",encoding="utf8") as file:
					json.dump(data,file,indent=4)

				info = MusicFunction.show_information(self, data["nowurl"], interaction.guild_id)

				embed = MusicFunction.Information(data, info, statusText)
				view = MusicFunction.MusicButton()

				await interaction.edit_original_response(embed=embed, view=view)

			search = self.search.value

			if "https://" in search or "http://" in search:
				statusText = ""

				if "list=LL" in search:
					statusText = "不支援 **喜歡的影片** 播放清單"
				
				elif "list=RD" in search:
					statusText = "不支援 **合輯** 播放清單"

				if statusText == "":
					await choose_video(search)
				
				else:
					dict = text.embeds[0].to_dict()
					dict['fields'][-1]['value'] = statusText
					embed = discord.Embed.from_dict(dict)
					view = MusicFunction.MusicButton()

					await interaction.edit_original_response(embed=embed, view=view)

			else:
				embed = discord.Embed(title="搜尋列表",description="** **")
				view = View(timeout=None)
				ydl_opts = {
					'quiet': True,
					'extract_flat': 'in_playlist',
					'force_generic_extractor': True,
				}
				
				with YoutubeDL(ydl_opts) as ydl:
					search_query = f"ytsearch5:{search}"  # 搜尋前 5 筆
					results = ydl.extract_info(search_query, download=False)

				entries = results.get('entries', [results])
				for i, entry in enumerate(entries):
					video_url = f"https://www.youtube.com/watch?v={entry['id']}" if 'id' in entry else entry['url']
					title = entry.get('title', video_url)
						
					music = Button(label= str(i + 1),style=discord.ButtonStyle.primary,custom_id=video_url)
					music.callback = choose_video
					view.add_item(music)

					embed.add_field(name=f"{i + 1} . {title}",value=" ",inline=False)

				await interaction.edit_original_response(content=None,embed=embed,view=view)

	class change_volume(Modal, title = "變更音量"):
		volume = TextInput(label="音量大小(建議不要太大)", placeholder="請輸入音量大小", style=discord.TextStyle.short, custom_id="volume", required=True, max_length=3)

		async def on_submit(self, interaction: discord.Interaction):
			await interaction.response.defer()
			volume = int(self.volume.value)

			if isinstance(volume, int):
				path = f"./audio_files/{interaction.guild_id}.json"
				with open(path,"r",encoding="utf8") as file:
					data = json.load(file)

				data["volume"] = volume / 100

				voice = interaction.guild.voice_client
				voice.source.volume = float(data["volume"])
				channel = interaction.channel
				text = await channel.fetch_message(data["text"])

				statusText = f"音量已改變為 {volume} %"

				with open(path,"w",encoding="utf8") as file:
					json.dump(data, file, indent=4, ensure_ascii=False)

				dict = text.embeds[0].to_dict()
				dict['fields'][-1]['value'] = statusText
				dict['fields'][-5]['value'] = f"{volume} %"
				embed = discord.Embed.from_dict(dict)
				view = MusicFunction.MusicButton()

				await interaction.edit_original_response(embed=embed, view=view)

	class QueueFunction:
		class QueueInfo:
			def __init__(self, data):
				max_page = math.ceil(len(data["url"]) / 10)
				page = max_page if data["page"] > max_page else data["page"]

				top = page * 10
				bottom = (page - 1) * 10
	
				self.embed = discord.Embed(title="待播清單",description=f"切換頁數時請稍後(不然機器人會停止運作)\n當前頁數:{page} / {max_page}",color=0x3d993a)
				for i in range(bottom, top):
					try:
						title = MusicFunction.get_title(self, data["url"][i])
						player = data["player"][i]
						self.embed.add_field(name=f"{i + 1}. {title}", value=f"點歌人：{player}", inline=True)
					except:
						pass

			def to_dict(self):
				return self.embed.to_dict()
			
		class QueueButton(View):
			def __init__(self, data):
				super().__init__(timeout = None)

				async def remove_song(interaction:discord.Interaction):
					await interaction.response.defer()
					index = int(interaction.data["custom_id"]) - 1

					path = f"./audio_files/{interaction.guild_id}.json"
					with open(path, "r", encoding="utf8") as file:
						data = json.load(file)

					if data["player"][index] == interaction.user.name:
						data["player"].pop(index)
						data["url"].pop(index)

						with open(path, "w", encoding="utf8") as file:
							json.dump(data, file, indent=4, ensure_ascii=False)

					view = MusicFunction.QueueFunction.QueueButton(data)
					embed = MusicFunction.QueueFunction.QueueInfo(data)

					await interaction.edit_original_response(embed=embed, view=view)

				page = data["page"]
				top = page * 10
				middle = page * 10 - 5
				bottom = (page - 1) * 10

				for i in range(bottom, middle):
					try:
						data["player"][i]
						button = Button(label=f"{i + 1}", style=discord.ButtonStyle.danger, custom_id=f"{i + 1}", row=2) 
						button.callback = remove_song
						self.add_item(button)
					except:
						pass

				for i in range(middle, top):
					try:
						data["player"][i]
						button = Button(label=f"{i + 1}", style=discord.ButtonStyle.danger, custom_id=f"{i + 1}", row=3) 
						button.callback = remove_song
						self.add_item(button)
					except:
						pass

			@discord.ui.button(
			label = "上一頁",
			style = discord.ButtonStyle.primary,
			emoji = "⬅️"
			)
			async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
				await interaction.response.defer()
				path = f"./audio_files/{interaction.guild_id}.json"
				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)

				if data["page"] > math.ceil(len(data["url"]) / 10):
					data["page"] = math.ceil(len(data["url"]) / 10)

				if data["page"] > 1:
					data["page"] -= 1

					with open(path, "w", encoding="utf8") as file:
						json.dump(data, file, indent=4, ensure_ascii=False)

				embed = MusicFunction.QueueFunction.QueueInfo(data)
				view = MusicFunction.QueueFunction.QueueButton(data)

				await interaction.edit_original_response(embed=embed, view=view)
				
				
			@discord.ui.button(
				label = "下一頁",
				style = discord.ButtonStyle.primary,
				emoji = "➡️"
				)
			async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
				await interaction.response.defer()
				path = f"./audio_files/{interaction.guild_id}.json"
				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)

				if data["page"] < math.ceil(len(data["url"]) / 10):
					data["page"] += 1

					with open(path, "w", encoding="utf8") as file:
						json.dump(data, file, indent=4, ensure_ascii=False)

				embed = MusicFunction.QueueFunction.QueueInfo(data)
				view = MusicFunction.QueueFunction.QueueButton(data)

				await interaction.edit_original_response(embed=embed, view=view)

			@discord.ui.button(
				label = "輸入頁數",
				style = discord.ButtonStyle.primary,
				emoji = "📄"
				)
			async def input_page(self, interaction: discord.Interaction, button: discord.ui.Button):
				modal = MusicFunction.QueueFunction.input_page()
				await interaction.response.send_modal(modal)

			@discord.ui.button(
				label = "返回",
				style = discord.ButtonStyle.secondary,
				emoji = "↩️"
				)
			async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
				await interaction.response.defer()
				path = f"./audio_files/{interaction.guild_id}.json"
				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)

				info = MusicFunction.show_information(self, data["nowurl"], interaction.guild_id)
				embed = MusicFunction.Information(data, info, "")
				view = MusicFunction.MusicButton()

				await interaction.edit_original_response(embed=embed, view=view)


		class input_page(Modal, title = "輸入頁數"):
			page = TextInput(label="輸入頁數", placeholder="請輸入頁數", style=discord.TextStyle.short, custom_id="page", required=True)

			async def on_submit(self, interaction: discord.Interaction):
				await interaction.response.defer()
				path = f"./audio_files/{interaction.guild_id}.json"
				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)

				page = int(self.page.value)

				if page >= math.ceil(len(data["url"]) / 10):
					data["page"] = math.ceil(len(data["url"]) / 10)

				elif page <= 1:
					data["page"] = 1
				
				else:
					data["page"] = page

				with open(path, "w", encoding="utf8") as file:
					json.dump(data, file, indent=4, ensure_ascii=False)

				embed = MusicFunction.QueueFunction.QueueInfo(data)
				view = MusicFunction.QueueFunction.QueueButton(data)

				await interaction.edit_original_response(embed=embed, view=view)

class WeatherFunction:
	def get_data(location):
		
		url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-16DF2507-7442-40B1-9532-3608485F6ED1"
		params = {
			"Authorization": "CWA-16DF2507-7442-40B1-9532-3608485F6ED1",
			"locationName": location,
		}
		response = requests.get(url, params=params)

		if response.status_code == 200:
			data = json.loads(response.text)

			weather_elements = data["records"]["location"][0]["weatherElement"]
			weather_state = weather_elements[0]["time"][0]["parameter"]["parameterName"]
			rain_prob = weather_elements[1]["time"][0]["parameter"]["parameterName"]
			min_tem = weather_elements[2]["time"][0]["parameter"]["parameterName"]
			comfort = weather_elements[3]["time"][0]["parameter"]["parameterName"]
			max_tem = weather_elements[4]["time"][0]["parameter"]["parameterName"]

			weather_data = {}
			weather_data["location"] = location
			weather_data["weather_state"] = weather_state
			weather_data["comfort"] = comfort
			weather_data["min_tem"] = min_tem
			weather_data["max_tem"] = max_tem
			weather_data["rain_prob"] = rain_prob

			return weather_data
		
		return None
	
	class Information:
		def __init__(self, data, message):
			now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.embed = discord.Embed(title=now, description=message, color=0x3d993a)
			if data:
				self.embed.add_field(name="當前地區", value=data["location"], inline=False)
				self.embed.add_field(name="天氣概況", value=data["weather_state"], inline=False)
				self.embed.add_field(name="舒適度", value=data["comfort"], inline=False)
				self.embed.add_field(name='溫度', value=f"{data['min_tem']} ~ {data['max_tem']} °C", inline=False)
				self.embed.add_field(name='降雨機率', value=f"{data['rain_prob']} %", inline=False)

		def to_dict(self):
			return self.embed.to_dict()
		
	class WeatherView(View):
		def __init__(self):
			super().__init__(timeout = None)

			self.add_item(WeatherFunction.ZoneSelect())

	class NorthButton(View):
		def __init__(self):
			super().__init__(timeout=None)

			async def show_info(interaction):
				await interaction.response.defer()
				locate = interaction.data["custom_id"]
				data = WeatherFunction.get_data(locate)
				embed = WeatherFunction.Information(data, "")

				await interaction.edit_original_response(embed=embed)

			Taipei = Button(label="臺北市", style=discord.ButtonStyle.primary, custom_id="臺北市")
			Newpei = Button(label="新北市", style=discord.ButtonStyle.primary, custom_id="新北市")
			Keelung = Button(label="基隆市", style=discord.ButtonStyle.primary, custom_id="基隆市")
			hsinchu = Button(label="新竹縣", style=discord.ButtonStyle.primary, custom_id="新竹縣")
			Hsinchu = Button(label="新竹市", style=discord.ButtonStyle.primary, custom_id="新竹市")
			Taoyuan = Button(label="桃園市", style=discord.ButtonStyle.primary, custom_id="桃園市")
			Yilan = Button(label="宜蘭縣", style=discord.ButtonStyle.primary, custom_id="宜蘭縣")

			self.add_item(Taipei)
			self.add_item(Newpei)
			self.add_item(Keelung)
			self.add_item(hsinchu)
			self.add_item(Hsinchu)
			self.add_item(Taoyuan)
			self.add_item(Yilan)

			for child in self.children:
				child.callback = show_info

	class CenterButton(View):
		def __init__(self):
			super().__init__(timeout=None)

			async def show_info(interaction):
				await interaction.response.defer()
				locate = interaction.data["custom_id"]
				data = WeatherFunction.get_data(locate)
				embed = WeatherFunction.Information(data, "")

				await interaction.edit_original_response(embed=embed)

			Taichung = Button(label="臺中市", style=discord.ButtonStyle.primary, custom_id="臺中市")
			Mioali = Button(label="苗栗縣", style=discord.ButtonStyle.primary, custom_id="苗栗縣")
			Changhua = Button(label="彰化縣", style=discord.ButtonStyle.primary, custom_id="彰化縣")
			Nantou = Button(label="南投縣", style=discord.ButtonStyle.primary, custom_id="南投縣")
			Yunlin = Button(label="雲林縣", style=discord.ButtonStyle.primary, custom_id="雲林縣")

			self.add_item(Taichung)
			self.add_item(Mioali)
			self.add_item(Changhua)
			self.add_item(Nantou)
			self.add_item(Yunlin)

			for child in self.children:
				child.callback = show_info

	class SouthButton(View):
		def __init__(self):
			super().__init__(timeout=None)

			async def show_info(interaction):
				await interaction.response.defer()
				locate = interaction.data["custom_id"]
				data = WeatherFunction.get_data(locate)
				embed = WeatherFunction.Information(data, "")

				await interaction.edit_original_response(embed=embed)

			Kaosiung = Button(label="高雄市", style=discord.ButtonStyle.primary, custom_id="高雄市")
			Tainan = Button(label="臺南市", style=discord.ButtonStyle.primary, custom_id="臺南市")
			Chiayi = Button(label="嘉義市", style=discord.ButtonStyle.primary, custom_id="嘉義市")
			Pington = Button(label="屏東縣", style=discord.ButtonStyle.primary, custom_id="屏東縣")
			Penghu = Button(label="澎湖縣", style=discord.ButtonStyle.primary, custom_id="澎湖縣")

			self.add_item(Kaosiung)
			self.add_item(Tainan)
			self.add_item(Chiayi)
			self.add_item(Pington)
			self.add_item(Penghu)

			for child in self.children:
				child.callback = show_info

	class EastButton(View):
		def __init__(self):
			super().__init__(timeout=None)

			async def show_info(interaction):
				await interaction.response.defer()
				locate = interaction.data["custom_id"]
				data = WeatherFunction.get_data(locate)
				embed = WeatherFunction.Information(data, "")

				await interaction.edit_original_response(embed=embed)

			Taitung = Button(label="臺東縣", style=discord.ButtonStyle.primary, custom_id="臺東縣")
			Hualien = Button(label="花蓮縣", style=discord.ButtonStyle.primary, custom_id="花蓮縣")

			self.add_item(Taitung)
			self.add_item(Hualien)
	
			for child in self.children:
				child.callback = show_info

	class IslandButton(View):
		def __init__(self):
			super().__init__(timeout=None)

			async def show_info(interaction):
				await interaction.response.defer()
				locate = interaction.data["custom_id"]
				data = WeatherFunction.get_data(locate)
				embed = WeatherFunction.Information(data, "")

				await interaction.edit_original_response(embed=embed)

			Kinmen = Button(label="金門縣", style=discord.ButtonStyle.primary, custom_id="金門縣")
			Lienchiang = Button(label="連江縣", style=discord.ButtonStyle.primary, custom_id="連江縣")

			self.add_item(Kinmen)
			self.add_item(Lienchiang)
	
			for child in self.children:
				child.callback = show_info

			

				
	class ZoneSelect(Select): 
		def __init__(self):
			options = [
				discord.SelectOption(label="北部", description="臺北、新北、基隆、新竹縣、新竹市、桃園、宜蘭"),
				discord.SelectOption(label="中部", description="臺中、苗栗、彰化、南投、雲林"),
				discord.SelectOption(label="南部", description="高雄、臺南、嘉義、屏東、澎湖"),
				discord.SelectOption(label="東部", description="花蓮、臺東"),
				discord.SelectOption(label="離島", description="金門、連江"),
				]
			super().__init__(placeholder="選擇一個縣市", min_values=1, max_values=1, options=options)
			
	
		async def callback(self, interaction: discord.Interaction):
			await interaction.response.defer()
			value = self.values[0]

			if value == "北部":
				view = WeatherFunction.NorthButton()
			elif value == "中部":
				view = WeatherFunction.CenterButton()
			elif value == "南部":
				view = WeatherFunction.SouthButton()
			elif value == "東部":
				view = WeatherFunction.EastButton()
			else:
				view = WeatherFunction.IslandButton()

			view.add_item(WeatherFunction.ZoneSelect())
			
			await interaction.edit_original_response(view=view)


class Timer(commands.Cog):
	tz = datetime.timezone(datetime.timedelta(hours = 8))
	morning = datetime.time(hour = 7, minute = 0, tzinfo = tz)
	midnight = datetime.time(hour = 0, minute = 0, tzinfo = tz)
	every_hour = [datetime.time(hour = i, minute = 0, tzinfo = datetime.timezone(datetime.timedelta(hours = 8))) for i in range(24)]


	def __init__(self, bot):
		self.bot = bot
		self.verify_refresh.start()
		self.weather_refresh.start()
		self.daily_refresh.start()
		self.greeting.start()
		self.auto_disconnect.start()
		self.play_next.start()
		self.social_update.start()

	def cog_unload(self):
		self.verify_refresh.cancel()
		self.weather_refresh.cancel()
		self.daily_refresh.cancel()
		self.greeting.cancel()
		self.auto_disconnect.cancel()
		self.play_next.cancel()
		self.social_update.cancel()


	@tasks.loop(minutes = 5)
	async def verify_refresh(self):
		channel = self.bot.get_channel(1277331531043438593)
		msg = await channel.fetch_message(1280097031251296267)

		view = VerifyFunction.VerifyButton()
		await msg.edit(view=view)


	@tasks.loop(minutes=10)
	async def weather_refresh(self):
		tem = "./guild_settings"
		for guild in self.bot.guilds:
			path = os.path.join(tem, f"{guild.id}.json")

			if not os.path.exists(path):
				continue

			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			if not data["greet_channel"]:
				continue
				
			channel = self.bot.get_channel(data["greet_channel"])
			msg = await channel.fetch_message(data["greet_message_id"])

			if msg:
				view = WeatherFunction.WeatherView()
				await msg.edit(view=view)

	@tasks.loop(time=midnight)
	async def daily_refresh(self):
		channel = self.bot.get_channel(1109828487189123133)
		message_record = self.bot.get_channel(1109828448626679888)

		await message_record.purge(limit=200)

		reload_db()
		dbFunction.daily_refresh()
		Quests = [item['Id'] for item in dbFunction.get_DQ()]
		Members = list({member.id for guild in self.bot.guilds for member in guild.members if not member.bot})
		
		for file in os.listdir(temp_deleted):
			if file == "template.json":
				continue

			path = os.path.join(temp_deleted, file)
			os.remove(path)

		for file in os.listdir(temp_edited):
			if file == "template.json":
				continue

			path = os.path.join(temp_edited, file)
			os.remove(path)

		for id in Members:
			dbFunction.DQ_refresh(random.sample(Quests, 3), id)
		
		await channel.send("每日已刷新")


	@tasks.loop(time=morning, count=1)
	async def greeting(self):
		tem = "./guild_settings"
		for guild in self.bot.guilds:
			path = os.path.join(tem, f"{guild.id}.json")

			if not os.path.exists(path):
				continue

			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			if not data["greet_channel"]:
				continue
			
			channel = self.bot.get_channel(data["greet_channel"])
			msg = data["greet_message"] if data["greet_message"] != None else "大家早安~今天又是新的一天"

			embed = WeatherFunction.Information(None, msg)
			view = WeatherFunction.WeatherView()
			message = await channel.send(embed=embed, view=view)

			data["greet_message_id"] = message.id

			with open(path, "w", encoding="utf8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)


	@tasks.loop(seconds=1)
	async def auto_disconnect(self):
		tem = "./audio_files"
		for file in os.listdir(tem):
			path = os.path.join(tem, file)
			
			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			guild = self.bot.get_guild(data["guild"])

			if data["leave_time"] == None and data["max_vote"] != 0:
				continue
	

			if guild.voice_client != None and data["max_vote"] == 0:
				if data['leave_time'] == 0:
					channel = self.bot.get_channel(data["channel"])
					text = await channel.fetch_message(data["text"])
					await text.edit(content="語音頻道裡面沒有人，機器人已自動斷線", embed=None, view=None)
		
					os.remove(path)
					clean_tempfile()
					await guild.voice_client.disconnect()
					continue

				if data['leave_time'] == None:
					data['leave_time'] = 180

					with open(path, "w", encoding="utf8") as file:
						json.dump(data,file,indent=4)

					channel = self.bot.get_channel(data["channel"])
					text = await channel.fetch_message(data["text"])
					dict = text.embeds[0].to_dict()
					dict['fields'][-1]['value'] = f"語音頻道沒有其他人，{data['leave_time']} 秒後將會自動斷線"
					dict['fields'][-2]['value'] = f"{len(data['vote'])} / {data['max_vote']}"
				
					embed = discord.Embed.from_dict(dict)
				
					await text.edit(embed=embed)
					continue
										
				if data['leave_time'] > 0:
					data['leave_time'] -= 1
					with open(path, "w", encoding="utf8") as file:
						json.dump(data, file, indent=4, ensure_ascii=False)
					continue
					
			data['leave_time'] = None
			channel = self.bot.get_channel(data["channel"])
			text = await channel.fetch_message(data["text"])
								
			with open(path, "w", encoding="utf8") as file:
				json.dump(data,file,indent=4)
				
			dict = text.embeds[0].to_dict()
			dict['fields'][-1]['value'] = ""
			dict['fields'][-2]['value'] = f"{len(data['vote'])} / {data['max_vote']}"
			embed = discord.Embed.from_dict(dict)

			await text.edit(embed=embed)
			




	@tasks.loop(seconds=1)
	async def play_next(self):
		tem = "./audio_files"
		for file in os.listdir(tem):
			try:
				path = os.path.join(tem, file)
				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)

				guild = self.bot.get_guild(data["guild"])
				voice = guild.voice_client

				if voice.is_playing():
					continue

				if data["pause"] == 1:
					continue

				channel = self.bot.get_channel(data["channel"])
				text = await channel.fetch_message(data["text"])

				if data["loop"] == 1:
					url = data["nowurl"]

				else:
					url = data["url"][0]

					data["nowurl"] = data["url"][0]
					data["nowplayer"] = data["player"][0]

					data["url"].pop(0)
					data["player"].pop(0)
					data["loop"] = 0

				data["vote"] = []
				data["pause"] = 0
				data["play_time"] = datetime.datetime.now().strftime("%p %H:%M:%S")

				with open(path, "w", encoding="utf8") as file:
					json.dump(data, file, indent=4, ensure_ascii=False)

				info = MusicFunction.show_information(self, url, guild.id)
				URL = info['url']

				# 判斷是本地檔案還是網路 URL
				if os.path.exists(URL):
					# 本地檔案 → 不加 reconnect
					source = PCMVolumeTransformer(FFmpegPCMAudio(URL), volume=data["volume"])
				else:
					# 網路串流 → 加 reconnect 選項
					ffmpeg_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
					source = PCMVolumeTransformer(FFmpegPCMAudio(URL, options=ffmpeg_options), volume=data["volume"])

				embed = MusicFunction.Information(data, info, "")
				view = MusicFunction.MusicButton()

				

				await text.edit(content=None, embed=embed, view=view)

				voice.play(source)

				

			except Exception as e:
				# print(e)
				pass

		

	@tasks.loop(minutes=1)
	async def social_update(self):
		YTUpdate = self.bot.get_channel(1112978654809575505)
		videos = scrapetube.get_channel("UCR4-1FIAu5hKt6wuz7RTj2w")

		ID = next(videos)['videoId']
		text = [message async for message in YTUpdate.history(limit=5)][0]

		yt_msg = f"https://www.youtube.com/watch?v={ID}"

		if yt_msg not in text.content:
			await YTUpdate.send(f"傑尼已經出片了喔~還不趕快去看!\n{yt_msg}")


async def setup(bot):
		await bot.add_cog(Timer(bot))
