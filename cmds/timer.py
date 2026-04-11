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
import aiohttp

from discord.ext import commands, tasks
from discord.utils import get
from discord.ui import Button, Modal, TextInput, View, Select
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from pytube import Playlist
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
from cmds.economy import register, reload_db
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()


temp_deleted = "./deleted_files"
temp_edited = "./edited_files"
dpath = "./jsonfile/data.json"

def clean_tempfile():
	# 刪除暫存檔
	for f in glob.glob("./audio_files/temp_*"):
		os.remove(f)

class MusicFunction:
	default_path = './audio_files'

	FFMPEG_OPTIONS = {
			"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
			"options": "-vn"
	}
	
	ffmpeg = "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"

	

	def show_information(self, url, guild_id):
		bilibili_opts = {
			'format': 'bestaudio/best',  # 取得最佳音訊格式
			'quiet': True,
			'noplaylist': True,
			'outtmpl': os.path.join("./audio_files", f"temp_{guild_id}.%(ext)s"),   # 以 guild.id 區分檔案
			'postprocessors': [],         # 不轉 mp3
		}

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

				cancel = Button(label="取消", style=discord.ButtonStyle.secondary, custom_id="cancel")
				cancel.callback = cancel_choose
				view.add_item(cancel)

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
	# 1. 將字典設為類別屬性，方便內部呼叫
	REGION_DATA = {
		"北部": ["臺北市", "新北市", "基隆市", "新竹縣", "新竹市", "桃園市", "宜蘭縣"],
		"中部": ["臺中市", "苗栗縣", "彰化縣", "南投縣", "雲林縣"],
		"南部": ["高雄市", "臺南市", "嘉義市", "屏東縣", "澎湖縣"],
		"東部": ["花蓮縣", "臺東縣"],
		"離島": ["金門縣", "連江縣"]
	}

	# 2. 獲取資料的方法 (設為靜態方法)
	@staticmethod
	async def fetch_data(location: str):
		url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
		api_key = os.getenv("WEATHER_KEY") # 讀取 .env 中的 Key
		
		params = {
			"Authorization": api_key,
			"locationName": location,
		}
		
		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=params, ssl=False) as response:
				if response.status == 200:
					data = await response.json()
					weather_elements = data["records"]["location"][0]["weatherElement"]
					return {
						"location": location,
						"weather_state": weather_elements[0]["time"][0]["parameter"]["parameterName"],
						"rain_prob": weather_elements[1]["time"][0]["parameter"]["parameterName"],
						"min_tem": weather_elements[2]["time"][0]["parameter"]["parameterName"],
						"comfort": weather_elements[3]["time"][0]["parameter"]["parameterName"],
						"max_tem": weather_elements[4]["time"][0]["parameter"]["parameterName"]
					}
		return None

	# 3. 建立 Embed 的方法 (設為靜態方法)
	@staticmethod
	def create_embed(data: dict, message: str = "") -> discord.Embed:
		now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		embed = discord.Embed(title=now, description=message, color=0x3d993a)
		if data:
			embed.add_field(name="當前地區", value=data["location"], inline=False)
			embed.add_field(name="天氣概況", value=data["weather_state"], inline=False)
			embed.add_field(name="舒適度", value=data["comfort"], inline=False)
			embed.add_field(name='溫度', value=f"{data['min_tem']} ~ {data['max_tem']} °C", inline=False)
			embed.add_field(name='降雨機率', value=f"{data['rain_prob']} %", inline=False)
		return embed

	class MainView(View):
		def __init__(self):
			# timeout=None 確保按鈕與選單不會因為超時而失效 (需在機器人啟動時 add_view 註冊)
			super().__init__(timeout=None) 
			
			# 初始化時，將「區域下拉選單」加入到這個主視圖中
			self.add_item(WeatherFunction.ZoneSelect())

	# 4. 單一城市按鈕 (巢狀類別)
	class CityButton(Button):
		def __init__(self, city_name: str):
			super().__init__(label=city_name, style=discord.ButtonStyle.primary, custom_id=city_name)

		async def callback(self, interaction: discord.Interaction):
			await interaction.response.defer()
			
			# 呼叫外部類別的靜態方法
			data = await WeatherFunction.fetch_data(self.custom_id)
			if data:
				embed = WeatherFunction.create_embed(data)
				await interaction.edit_original_response(embed=embed)
			else:
				await interaction.edit_original_response(content="無法獲取天氣資料，請稍後檢查 API 設定。")

	# 5. 區域下拉選單 (巢狀類別)
	class ZoneSelect(Select):
		def __init__(self):
			options = [
				discord.SelectOption(label="北部", description="臺北、新北、基隆、新竹、桃園、宜蘭"),
				discord.SelectOption(label="中部", description="臺中、苗栗、彰化、南投、雲林"),
				discord.SelectOption(label="南部", description="高雄、臺南、嘉義、屏東、澎湖"),
				discord.SelectOption(label="東部", description="花蓮、臺東"),
				discord.SelectOption(label="離島", description="金門、連江"),
			]
			super().__init__(placeholder="選擇一個區域", min_values=1, max_values=1, options=options)

		async def callback(self, interaction: discord.Interaction):
			await interaction.response.defer()
			selected_region = self.values[0]
			
			# 實例化一個新的 View
			view = View(timeout=None)
			
			# 根據選擇的區域，動態生成對應的縣市按鈕
			for city in WeatherFunction.REGION_DATA[selected_region]:
				view.add_item(WeatherFunction.CityButton(city))
				
			# 把下拉式選單加回去，讓使用者可以繼續切換區域
			view.add_item(WeatherFunction.ZoneSelect())
			
			await interaction.edit_original_response(content=f"已切換至 {selected_region}，請選擇縣市：", view=view, embed=None)

class Timer(commands.Cog):
	tz = datetime.timezone(datetime.timedelta(hours = 8))
	morning = datetime.time(hour = 7, minute = 0, tzinfo = tz)
	midnight = datetime.time(hour = 0, minute = 0, tzinfo = tz)
	every_hour = [datetime.time(hour = i, minute = 0, tzinfo = datetime.timezone(datetime.timedelta(hours = 8))) for i in range(24)]


	def __init__(self, bot):
		self.bot = bot
		self.weather_refresh.start()
		self.daily_refresh.start()
		self.greeting.start()
		self.auto_disconnect.start()
		self.play_next.start()
		self.social_update.start()

	def cog_unload(self):
		self.weather_refresh.cancel()
		self.daily_refresh.cancel()
		self.greeting.cancel()
		self.auto_disconnect.cancel()
		self.play_next.cancel()
		self.social_update.cancel()

	@tasks.loop(minutes=10)
	async def weather_refresh(self):
		tem_dir = "./guild_settings"
		
		for guild in self.bot.guilds:
			path = os.path.join(tem_dir, f"{guild.id}.json")

			# 1. 檢查檔案是否存在
			if not os.path.exists(path):
				continue

			# 2. 讀取設定 (建議之後改用記憶體快取)
			try:
				with open(path, "r", encoding="utf8") as file:
					data = json.load(file)
			except Exception as e:
				print(f"讀取 {guild.id} 設定失敗: {e}")
				continue

			# 3. 檢查頻道與訊息 ID 是否存在
			channel_id = data.get("greet_channel")
			message_id = data.get("greet_message_id")
			if not channel_id or not message_id:
				continue

			channel = self.bot.get_channel(channel_id)
			if not channel:
				continue

			# 4. 抓取並編輯訊息 (加上錯誤處理)
			try:
				# 使用 fetch 確保訊息還在
				msg = await channel.fetch_message(message_id)
				
				# 重新實例化 View 並更新
				# 提示：如果按鈕不需要動態改變文字，其實不需要每 10 分鐘重新 edit 訊息
				# 除非你的 View 裡面有顯示「最後更新時間」
				view = WeatherFunction.MainView() 
				await msg.edit(view=view)
				
			except discord.NotFound:
				print(f"在伺服器 {guild.id} 找不到打招呼訊息，可能已被刪除。")
			except discord.Forbidden:
				print(f"機器人沒有權限在 {guild.id} 編輯該訊息。")
			except Exception as e:
				print(f"更新 {guild.id} 發生未知錯誤: {e}")

	@tasks.loop(time=midnight)
	async def daily_refresh(self):
		channel = self.bot.get_channel(1109828487189123133)
		message_record = self.bot.get_channel(1109828448626679888)

		await message_record.purge(limit=200)

		reload_db()
		dbFunction.daily_refresh()
		
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
		
		await channel.send("每日已刷新")


	@tasks.loop(time=morning, count=1)
	async def greeting(self):
		tem = "./guild_settings"
		
		for guild in self.bot.guilds:
			path = os.path.join(tem, f"{guild.id}.json")

			# 1. 檢查設定檔是否存在
			if not os.path.exists(path):
				continue

			with open(path, "r", encoding="utf8") as file:
				data = json.load(file)

			# 2. 檢查是否有設定早安頻道 (使用 .get() 比較安全，避免 KeyError)
			if not data.get("greet_channel"):
				continue
			
			# 3. 獲取頻道物件，並防呆檢查頻道是否還存在(可能被刪除了)
			channel = self.bot.get_channel(data["greet_channel"])
			if channel is None:
				continue

			# 4. 設定早安訊息內容
			msg = data.get("greet_message") if data.get("greet_message") else "大家早安~今天又是新的一天，請選擇你想查詢天氣的區域："

			# 🟢 5. 關鍵修正：呼叫我們稍早定義的 create_embed 與 MainView
			# 這裡 data 傳入 None，create_embed 會只顯示 msg，不會報錯 (因為我們之前有寫 if data: 判斷)
			embed = WeatherFunction.create_embed(data=None, message=msg)
			view = WeatherFunction.MainView()
			
			try:
				# 6. 發送包含「早安訊息」與「天氣下拉選單」的訊息
				message = await channel.send(embed=embed, view=view)

				# 7. 儲存發送出去的訊息 ID，方便未來更新或刪除
				data["greet_message_id"] = message.id
				with open(path, "w", encoding="utf8") as file:
					json.dump(data, file, indent=4, ensure_ascii=False)
					
			except discord.Forbidden:
				print(f"❌ 錯誤：機器人沒有權限在 {guild.name} 的頻道發送訊息。")
			except Exception as e:
				print(f"❌ 發送早安訊息時發生未知的錯誤: {e}")


	@tasks.loop(seconds=1)
	async def auto_disconnect(self):
		tem = "./audio_files"
		for filename in os.listdir(tem):
			if not filename.endswith(".json") or filename == "template.json":
				continue

			path = os.path.join(tem, filename)
			
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

				clean_tempfile()
				info = MusicFunction.show_information(self, url, guild.id)
				URL = info['url']

				# 判斷是本地檔案還是網路 URL
				# if os.path.exists(URL):
					# 本地檔案 → 不加 reconnect
				source = PCMVolumeTransformer(FFmpegPCMAudio(URL), volume=data["volume"])


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
