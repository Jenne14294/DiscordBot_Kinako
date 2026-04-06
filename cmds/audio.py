import discord
import json
import os
import math
import requests
import random
import importlib
import AI_title
import re
import html

from pytube import Playlist
from discord.ext import commands
from discord.ui import Button, View, TextInput, Modal
from discord import app_commands
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL

def clean_tempfile():
	# 刪除暫存檔
	for f in glob.glob("./audio_files/temp_*"):
		os.remove(f)

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
				"cachedir": False
}

FFMPEG_OPTIONS = {
		"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
		"options": "-vn"
}
	
default_path = "./audio_files"

def reload():
	importlib.reload(AI_title)

def get_title(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/118.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        # 【關鍵修復】強制指定 UTF-8 解碼，防止 requests 預設使用 ISO-8859-1 產生亂碼
        r.encoding = 'utf-8' 
        
    except Exception as e:
        return f"[錯誤] 無法連線: {e}"

    html_text = r.text
    title = "未知標題"

    # 1. YouTube 標題擷取
    if "youtube.com" in url or "youtu.be" in url:
        # 優先：直接抓取網頁的 <title>，最單純且不易受 JSON 格式變動影響
        match = re.search(r'<title>(.*?)</title>', html_text, re.S)
        if match:
            # 清除結尾的 " - YouTube" 後綴
            title = match.group(1).replace(" - YouTube", "").strip()
            # 處理 HTML 實體符號，例如 &amp; -> &
            title = html.unescape(title)
        else:
            # 備案：從 JSON 結構中抓取
            match = re.search(r'"title":"(.*?)"', html_text)
            if match:
                try:
                    # 使用 json.loads 安全解析包含 \uXXXX 的字串
                    title = json.loads(f'"{match.group(1)}"')
                except json.JSONDecodeError:
                    title = match.group(1)

    # 2. Bilibili 標題擷取
    elif "bilibili.com" in url:
        # B站標題可能有 data-vue-meta 屬性
        match = re.search(r'<title[^>]*>(.*?)</title>', html_text, re.S)
        if match:
            # 清除 Bilibili 預設的結尾後綴
            title = match.group(1).replace("_哔哩哔哩_bilibili", "").strip()
            title = html.unescape(title)
        else:
            # 備案：從 JSON 抓取
            match = re.search(r'"title":"(.*?)"', html_text)
            if match:
                try:
                    title = json.loads(f'"{match.group(1)}"')
                except json.JSONDecodeError:
                    title = match.group(1)

    return title

def get_lyrics(title):
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

class QueueFunction:
		class QueueInfo:
			def __init__(self, data):
				page = data["page"]
				max_page = math.ceil(len(data["url"]) / 10)
				top = page * 10
				bottom = (page - 1) * 10
				self.embed = discord.Embed(title="待播清單",description=f"切換頁數時請稍後(不然機器人會停止運作)\n當前頁數:{page} / {max_page}",color=0x3d993a)
				for i in range(bottom, top):
					try:
						title = get_title(data["url"][i])
						player = data["player"][i]
						self.embed.add_field(name=f"{i + 1}. {title}", value=f"點歌人：{player}", inline=True)
					except Exception as e:
						#print(e)
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

					view = QueueFunction.QueueButton(data)
					embed = QueueFunction.QueueInfo(data)

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

				if data["page"] > 1:
					data["page"] -= 1

					with open(path, "w", encoding="utf8") as file:
						json.dump(data, file, indent=4, ensure_ascii=False)

				embed = QueueFunction.QueueInfo(data)
				view = QueueFunction.QueueButton(data)

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

				embed = QueueFunction.QueueInfo(data)
				view = QueueFunction.QueueButton(data)

				await interaction.edit_original_response(embed=embed, view=view)

			@discord.ui.button(
				label = "輸入頁數",
				style = discord.ButtonStyle.primary,
				emoji = "📄"
				)
			async def input_page(self, interaction: discord.Interaction, button: discord.ui.Button):
				modal = QueueFunction.input_page()
				await interaction.response.send_modal(modal)

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

				embed = QueueFunction.QueueInfo(data)
				view = QueueFunction.QueueButton(data)

				await interaction.edit_original_response(embed=embed, view=view)

class Audio(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@app_commands.command(name="play",description="播放音樂")
	@app_commands.describe(搜尋="關鍵字/網址")
	async def play_a_song(self,interaction:discord.Interaction, *,搜尋:str):

		async def choose_video(item:discord.Interaction):
			guildID = interaction.guild.id
			jsonfile = f"{guildID}.json"
			urlList = []
									
			path = f"./audio_files/{jsonfile}"
							
			with open(path,"r",encoding="utf8") as file:
				data = json.load(file)
				
			try:
				url = item.data["custom_id"]
				urlList.append(url)
				player_list = [interaction.user.name]

				TITLE = get_title(url)

			except:
				url = item
				
				if "list" in url and "youtube" in url:
					urlList = list(Playlist(url))
					TITLE = Playlist(url).title
					player_list = [interaction.user.name] * len(urlList)

				elif "list" in url and "bilibili" in url:
					# yt_dlp 選項
					ydl_opts = {
						'extract_flat': True,   # 只解析清單，不下載影片
						'quiet': True,
						'skip_download': True
					}

					with YoutubeDL(ydl_opts) as ydl:
						info = ydl.extract_info(url, download=False)

					# info['title'] 是播放清單標題
					TITLE = info.get('title', '未知清單')

					# 每個 entry 是清單裡的影片
					urlList = [entry['url'] for entry in info.get('entries', [])]

					# 建立對應使用者名稱的播放列表
					player_list = [interaction.user.name] * len(urlList)
					
				else:
					urlList.append(url)
					player_list = [interaction.user.name]

					TITLE = get_title(url)

			response = await interaction.edit_original_response(content=f"***{TITLE}*** 已經新增到歌單了",embed=None,view=None)
				
			path = f"./audio_files/{interaction.guild.id}.json"				
			with open(path,"r",encoding="utf8") as file:
				data = json.load(file)
					
			data["channel"] = int(interaction.channel.id)
			data["guild"] = interaction.guild_id
			data["text"] = response.id
			data["url"].extend(urlList)
			data["player"].extend(player_list)

			with open(path,"w",encoding="utf8") as file:
				json.dump(data,file,indent=4)


		voice = interaction.guild.voice_client

		if not interaction.user.voice:
			await interaction.response.send_message("你必須加入語音頻道")
			return
		
		if not voice:
			voice = await interaction.user.voice.channel.connect()
			
		else:
			await voice.move_to(interaction.user.voice.channel)

		path = f"./audio_files/{interaction.guild_id}.json"

		if not os.path.exists(path) or not voice:
			tem_path = f"./audio_files/template.json"
	
			with open(tem_path, "r", encoding="utf8") as file:
				data = json.load(file)
											
			with open(path,"w",encoding="utf8") as file:
				json.dump(data,file,indent=4)
			
		await interaction.response.send_message("正在搜尋音樂...")

		if "https://" in 搜尋 or "http://" in 搜尋:
			if "list=LL" in 搜尋:
				await interaction.edit_original_response(content="不支援 **喜歡的影片** 播放清單")
				return
			
			if "list=RD" in 搜尋:
				await interaction.edit_original_response(content="不支援 **合輯** 播放清單")
				return
			
			url = 搜尋
			await choose_video(url)
				
		else:
			embed = discord.Embed(title="搜尋列表",description="** **")
			view = View(timeout=None)
			ydl_opts = {
				'quiet': True,
				'extract_flat': 'in_playlist',
				'force_generic_extractor': True,
			}
			
			with YoutubeDL(ydl_opts) as ydl:
				search_query = f"ytsearch5:{搜尋}"  # 搜尋前 5 筆
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

			
				

	@app_commands.command(description="查詢現在正在播放的音樂")
	async def np(self,interaction:discord.Interaction):
		await interaction.response.defer()
		
		path = f"./audio_files/{interaction.guild.id}.json"
		voice = interaction.guild.voice_client

		if not os.path.exists(path) or not voice:
			await interaction.edit_original_response(content="我不在語音頻道唷!")
			return
		
		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)
			
		if not voice or not voice.is_connected():
			await interaction.edit_original_response(content="我沒有在語音頻道裡面喔!")
			return
		
		if voice.is_playing() and not voice.is_paused():
			url = data["nowurl"]
			player = data["nowplayer"]
			volume = data["volume"]

			with YoutubeDL(YDL_OPTIONS) as ydl:
				info = ydl.extract_info(url, download=False)

			THUMBNAIL = info['thumbnail']
			title = get_title(url)
			LENGTH_second = int(info["duration"] % 60)
			LENGTH_minute = (info["duration"] - LENGTH_second) // 60
				
				
			embed = discord.Embed(title="現在正在播放",description="",color=0x3d993a)
			embed.set_thumbnail(url=THUMBNAIL)
			embed.add_field(name="**標題**", value=title, inline=False)
			embed.add_field(name="**點歌人**",value=player,inline=False)
			embed.add_field(name="**網址**", value=url, inline=False)
			embed.add_field(name="**時間**", value=f"{LENGTH_minute} 分 {LENGTH_second} 秒", inline=False)
			embed.add_field(name="**音量**",value=f"{round(volume * 100)} %",inline=False)
			await interaction.edit_original_response(embed=embed)

		elif voice.is_paused():
			await interaction.edit_original_response(content="歌曲已經被暫停播放")

		else:
			await interaction.edit_original_response(content="現在沒有在播放音樂")
			

	
	@app_commands.command(description="獲取歌曲列表")
	async def queue(self, interaction:discord.Interaction):
		await interaction.response.defer()
		path = f"./audio_files/{interaction.guild.id}.json"
		
		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)
		
		embed = QueueFunction.QueueInfo(data)
		view = QueueFunction.QueueButton(data)

		await interaction.edit_original_response(embed=embed, view=view)


	@app_commands.command(description="繼續播放音樂")
	async def resume(self,interaction:discord.Interaction):
		path = f"./audio_files/{interaction.guild.id}.json"
		voice = interaction.guild.voice_client
		if not os.path.exists(path) or not voice:
			await interaction.response.send_message("我不在語音頻道裡面唷~")
			return
		
		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)

		data["pause"] = 0
		player = data["nowplayer"]

		with open(path,"w",encoding="utf8") as file:
			json.dump(data,file,indent=4)

		if interaction.user.name == player and not voice.is_playing:
			voice.resume()
			await interaction.response.send_message(f"音樂被 **{interaction.user.name}** 繼續播放")

		elif interaction.user.name == player and voice.is_playing:
			await interaction.response.send_message("音樂已經被繼續播放了")

		else:
			await interaction.response.send_message("你無法繼續播放該音樂")
			

	@app_commands.command(description="暫停播放音樂")
	async def pause(self,interaction:discord.Interaction):
		path = f"./audio_files/{interaction.guild.id}.json"
		voice = interaction.guild.voice_client

		if not os.path.exists(path) or not voice:
			await interaction.response.send_message("我不在語音頻道裡面唷~")
			return

		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)

		player = data["nowplayer"]

		if interaction.user.name == player and voice.is_playing():
			voice.pause()
			data["pause"] = 1

			with open(path,"w",encoding="utf8") as file:
				json.dump(data,file,indent=4)

			await interaction.response.send_message(f"音樂被 **{interaction.user.name}** 暫停播放")

		elif interaction.user.name == player and voice.is_paused():
			await interaction.response.send_message("音樂已經被暫停")
		
		else:
			await interaction.response.send_message("你無法暫停播放該音樂")

			

	@app_commands.command(description="跳過當前音樂")
	async def skip(self,interaction:discord.Interaction):
		path = f"./audio_files/{interaction.guild.id}.json"
		voice = interaction.guild.voice_client

		if not os.path.exists(path) or not voice:
			await interaction.response.send_message("我不在語音頻道裡面唷~")
			return
		
		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)
			
		vote = data["vote"]
		
		player = data["nowplayer"]

		if not voice.is_playing():
			await interaction.response.send_message("目前沒有音樂在播放")
			return

		if interaction.user.name == player:
			voice.stop()
			await interaction.response.send_message(f"**{player}** 跳過當前音樂")

		elif interaction.user.name != player:
			if interaction.user.name in vote:
				await interaction.response.send_message("你已經投票跳過這首歌了")
				return
			
			with open(path,"r",encoding="utf8") as file:
				data = json.load(file)

			Max = data["max_vote"]			
			data["vote"].append(interaction.user.name)
			vote = data["vote"]

			if len(vote) >= Max:
				await interaction.response.send_message("音樂已被跳過")
				voice.stop()
				data["vote"] = []
				data["loop"] = 0

				with open(path,"w",encoding="utf8") as file:
					json.dump(data,file,indent=4)
							
			else:
				data["vote"] = vote

				with open(path,"w",encoding="utf8") as file:
					json.dump(data,file,indent=4)

				votecount = len(vote)
				await interaction.response.send_message(f"跳過此音樂的人數：{votecount} / {Max}")


	@app_commands.command(description="循環播放音樂")
	async def loop(self,interaction:discord.Interaction):
		path = f"./audio_files/{interaction.guild.id}.json"
		voice = interaction.guild.voice_client

		if not os.path.exists(path) or not voice:
			await interaction.response.send_message("我不在語音頻道裡面唷~")
			return

		if not voice.is_playing():
			await interaction.response.send_message("沒有音樂正在被播放")
			return
		
		with open(path,"r",encoding="utf8") as file:
			data = json.load(file)

		player = data["nowplayer"]

		if interaction.user.name != player:
			await interaction.response.send_message("你無法循環播放該音樂")
			return

		if data["loop"] == 0:
			data["loop"] = 1

			with open(path,"w",encoding="utf8") as file:
				json.dump(data,file,indent=4)
			
			await interaction.response.send_message(f"音樂開始循環播放")
		elif data["loop"] == 0:
			data["loop"] = 0

			with open(path,"w",encoding="utf8") as file:
				json.dump(data,file,indent=4)
			
			await interaction.response.send_message("音樂停止循環播放")
			return
			

	
	@app_commands.command(description="重新排序待播清單")
	async def shuffle(self, interaction:discord.Interaction):
		path = f"./audio_files/{interaction.guild_id}.json"
		voice = interaction.guild.voice_client
		if not (os.path.exists(path) or voice):
			await interaction.response.send_message("我不在語音頻道裡面唷~")
			return
		
		with open(path, "r", encoding="utf8") as file:
			data = json.load(file)

		url = data["url"]
		player = data["player"]
		combined = list(zip(url, player))
		random.shuffle(combined)
		url, player = zip(*combined)

		data["url"] = url
		data["player"] = player

		with open(path, "w", encoding="utf8") as file:
			json.dump(data, file, indent=4, ensure_ascii=False)

		await interaction.response.send_message("待播清單已重新排序")

	@app_commands.command(description="查詢當前歌曲歌詞")
	async def lyrics(self, interaction:discord.Interaction):
		await interaction.response.defer()
		reload()
		path = f"./audio_files/{interaction.guild_id}.json"
		voice = interaction.guild.voice_client

		if not os.path.exists(path) or not voice:
			await interaction.edit_original_response(content="我不在語音頻道裡面唷~")
			return
		
		with open(path, "r", encoding="utf8") as file:
			data = json.load(file)

		title = AI_title.ask_ai(f"{get_title(data['nowurl'])}\n給我這首歌的歌名，只要歌名就好").replace("\n", "")

		lyrics = get_lyrics(title)
		statusText = f"{title} 的歌詞網址：{lyrics}\n**此功能尚在測試，可能有些許錯誤**" if lyrics != None else "找不到歌詞"

		await interaction.edit_original_response(content=statusText)


	@app_commands.command(description="改變播放音量")
	@app_commands.describe(音量="要改變的音量(請輸入1 ~ 150)")
	async def volume(self,interaction:discord.Interaction,音量:float):
		path = f"./audio_files/{interaction.guild.id}.json"
		voice = interaction.guild.voice_client

		try:
			with open(path,"r",encoding="utf8") as file:
				data = json.load(file)
			if interaction.guild.voice_client != None:
				
					try:
						if 1 <= 音量 <= 150:
							volume = round(音量 / 100,2)
							data["volume"] = volume
							with open(path,"w",encoding="utf8") as file:
								json.dump(data,file,indent=4)
	
							await interaction.response.send_message(f"音量已改變為 {round(音量)} %")
							voice.source.volume = float(volume)

						else:
							await interaction.response.send_message("請輸入在正確的音量範圍")
						
					except:
						pass

		except:
			await interaction.response.send_message("我不在語音頻道裡面唷~")
		
	

	@app_commands.command(name="dc",description="讓我離開語音頻道")
	async def leave(self,interaction:discord.Interaction):
		path = f"./audio_files/{interaction.guild.id}.json"
		try:
			os.remove(path)
			clean_tempfile()
			voice = interaction.guild.voice_client
			await voice.disconnect()
			await interaction.response.send_message("我已經離開了唷~")
		except:
			await interaction.response.send_message("我不在語音頻道裡面唷~")
		
		

			
async def setup(bot):
	await bot.add_cog(Audio(bot))