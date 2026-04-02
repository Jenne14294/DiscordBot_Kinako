import discord
import json
import random
import requests
import asyncio

from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, TextInput

class HelpMenu:
	class DefaultMenu:
		def __init__(self):
			self.embed = discord.Embed(title="黃名子",description="所有權為 <@493411441832099861> 所有\n★為管理員以上才可使用\n■為獲得/扣除金幣量",color=0x3d993a)
			self.embed.add_field(name="**[遊戲類]**", value="不同類型的小遊戲", inline=True)
			self.embed.add_field(name="**★[管理類]**",value="給予管理員的指令",inline=True)
			self.embed.add_field(name="**[功能類]**",value="所有人都能用的功能",inline=True)
			self.embed.add_field(name="**■[經濟類]**", value="經濟系統", inline=True)
			self.embed.add_field(name="**[音樂類]**", value="音樂系統", inline=True)

		def to_dict(self):
			return self.embed.to_dict()
		
	class GameMenu:
		def __init__(self):
			self.embed = discord.Embed(title="黃名子",description="所有權為 <@493411441832099861> 所有\n★為管理員以上才可使用\n■為獲得/扣除金幣量",color=0x3d993a)
			self.embed.add_field(name="**[dice]**", value="顯示你骰出幾點", inline=True)
			self.embed.add_field(name="**(+)[gtn]**",value="遊玩[猜數字]遊戲",inline=True)
			self.embed.add_field(name="**■[ttt]**", value="遊玩[井字遊戲]", inline=True)
			self.embed.add_field(name="**■[slot <金額>]**",value="遊玩[吃角子老虎機]",inline=True)
			self.embed.add_field(name="**■[pp <金額>]**",value="遊玩[洞洞樂]",inline=True)

		def to_dict(self):
			return self.embed.to_dict()
		
	class FunctionMenu:
		def __init__(self):
			self.embed = discord.Embed(title="黃名子",description="所有權為 <@493411441832099861> 所有\n★為管理員以上才可使用\n■為獲得/扣除金幣量",color=0x3d993a)
			self.embed.add_field(name="**[ping]**", value="顯示機器人延遲", inline=True)
			self.embed.add_field(name="**[say <訊息>]**",value="讓機器人覆誦你的話",inline=True)
			self.embed.add_field(name="**[pixiv <關鍵字> (全部/普通/r18) (頁數)**",value="隨機抽取pixiv圖庫",inline=True)
			self.embed.add_field(name="**[wheel <標題> <內容>]**",value="建立輪盤",inline=True)

		def to_dict(self):
			return self.embed.to_dict()
		
	class EconomyMenu:
		def __init__(self):
			self.embed = discord.Embed(title="黃名子",description="所有權為 <@493411441832099861> 所有\n★為管理員以上才可使用\n■為獲得/扣除金幣量",color=0x3d993a)
			self.embed.add_field(name="**[register]**", value="註冊經濟資料", inline=True)
			self.embed.add_field(name="**[money]**",value="查詢錢包餘額",inline=True)
			self.embed.add_field(name="**(+)[daily]**", value="領取每日獎勵", inline=True)
			self.embed.add_field(name="**(+)[bank] <金額>**", value="存入或取出錢", inline=True)
			self.embed.add_field(name="**■[gift <@用戶> <金額>]**", value="給予該用戶金錢", inline=True)

		def to_dict(self):
			return self.embed.to_dict()
		
	class MusicMenu:
		def __init__(self):
			self.embed = discord.Embed(title="黃名子",description="所有權為 <@493411441832099861> 所有\n★為管理員以上才可使用\n■為獲得/扣除金幣量",color=0x3d993a)
			self.embed.add_field(name="**[play <網址/關鍵字>]**", value="讓機器人播放指定音樂", inline=True)
			self.embed.add_field(name="**[np]**", value="顯示目前播放的音樂", inline=True)
			self.embed.add_field(name="**[queue]**", value="顯示歌曲列表", inline=True)
			self.embed.add_field(name="**[pause]**",value="暫停當前的音樂",inline=True)
			self.embed.add_field(name="**[resume]**",value="繼續當前的音樂",inline=True)
			self.embed.add_field(name="**[loop]**",value="循環播放當前的音樂",inline=True)
			self.embed.add_field(name="**[shuffle]**",value="重新排序歌單",inline=True)
			self.embed.add_field(name="**[lyrics]**",value="查詢當前音樂的歌詞網址",inline=True)
			self.embed.add_field(name="**[skip]**",value="投票跳過當前的音樂",inline=True)
			self.embed.add_field(name="**[volume <音量>]**",value="改變現在的音量大小",inline=True)
			self.embed.add_field(name="**[dc]**",value="讓機器人離開語音頻道",inline=True)

		def to_dict(self):
			return self.embed.to_dict()
		
	class AdminMenu:
		def __init__(self):
			self.embed = discord.Embed(title="黃名子",description="所有權為 <@493411441832099861> 所有\n★為管理員以上才可使用\n■為獲得/扣除金幣量",color=0x3d993a)
			self.embed.add_field(name="**[setting <項目[用戶加入/用戶離開/音樂相關/早上招呼]>]**",value="設定特殊功能",inline=True)
			self.embed.add_field(name="**[clear <數量> (模式[以用戶刪除/以字刪除]) (目標[用戶ID/訊息內容])]**", value="清除訊息",inline=True)
			self.embed.add_field(name="**[snipe]**", value="顯示最後五則被刪掉的訊息", inline=True)
			self.embed.add_field(name="**[history]**", value="顯示最後五則被編輯的訊息", inline=True)
			self.embed.add_field(name="**[kick <@成員>]**",value="把 <@成員> 踢除",inline=True)
			self.embed.add_field(name="**[ban <@成員>]**",value="把 <@成員> 封鎖",inline=True)

		def to_dict(self):
			return self.embed.to_dict()
		
	class ChangeLogMenu:
		def __init__(self):
			# 讀取 JSON 檔案 (請確保 changelog.json 放在正確的路徑)
			with open('jsonfile/changelog.json', 'r', encoding='utf-8') as f:
				self.logs = json.load(f)
			
			self.items_per_page = 10
			self.max_pages = max(1, (len(self.logs) - 1) // self.items_per_page + 1)

		def get_page(self, page: int) -> discord.Embed:
			embed = discord.Embed(
				title=f"黃名子 開發日誌 (第 {page}/{self.max_pages} 頁)",
				description="所有權為 <@493411441832099861> 所有\n★為管理員以上才可使用\n■為獲得/扣除金幣量",
				color=0x3d993a
			)
			
			start_idx = (page - 1) * self.items_per_page
			end_idx = start_idx + self.items_per_page
			
			# 遍歷 JSON 陣列裡的字典
			for log in self.logs[start_idx:end_idx]:
				embed.add_field(name=log["name"], value=log["value"], inline=True)
				
			return embed
		
	class MenuChanger(discord.ui.View):
		def __init__(self, timeout: float | None = 180):
			super().__init__(timeout=timeout)
			
			# --- 分頁相關狀態紀錄 ---
			self.changelog_page = 1 
			self.changelog_obj = HelpMenu.ChangeLogMenu() # 實例化你上面的 ChangeLogMenu
			
			# --- 定義按鈕 (使用 row 參數將按鈕分行，避免排版混亂) ---
			self.game = Button(label="遊戲", style=discord.ButtonStyle.primary, custom_id="game", emoji="🎮", row=0)
			self.function = Button(label="功能", style=discord.ButtonStyle.primary, custom_id="function", emoji="⚙️", row=0)
			self.economy = Button(label="經濟", style=discord.ButtonStyle.primary, custom_id="money", emoji="💰", row=0)
			self.music = Button(label="音樂", style=discord.ButtonStyle.primary, custom_id="music", emoji="🎵", row=0)
			self.admin = Button(label="管理", style=discord.ButtonStyle.primary, custom_id="admin", emoji="🔧", row=1)
			self.changelog = Button(label="開發日誌", style=discord.ButtonStyle.primary, custom_id="changelog", emoji="📃", row=1)
			
			# 翻頁按鈕預設不直接加入 (稍後動態顯示)，放在 row=2
			self.prev_btn = Button(label="上一頁", style=discord.ButtonStyle.secondary, custom_id="prev_page", emoji="⬅️", row=2)
			self.next_btn = Button(label="下一頁", style=discord.ButtonStyle.secondary, custom_id="next_page", emoji="➡️", row=2)

			async def Button_callback(interaction: discord.Interaction):
				await interaction.response.defer()          
				cid = interaction.data["custom_id"]

				# 如果點擊的【不是】開發日誌或翻頁按鈕，就隱藏(移除)翻頁按鈕
				if cid not in ["changelog", "prev_page", "next_page"]:
					if self.prev_btn in self.children:
						self.remove_item(self.prev_btn)
					if self.next_btn in self.children:
						self.remove_item(self.next_btn)

				# --- 原有選單邏輯 ---
				if cid == "game":
					embed = HelpMenu.GameMenu()
					await interaction.edit_original_response(embed=embed, view=self)
					
				elif cid == "function":
					embed = HelpMenu.FunctionMenu()
					await interaction.edit_original_response(embed=embed, view=self)

				elif cid == "money":
					embed = HelpMenu.EconomyMenu()
					await interaction.edit_original_response(embed=embed, view=self)
					
				elif cid == "music":
					embed = HelpMenu.MusicMenu()
					await interaction.edit_original_response(embed=embed, view=self)
				
				elif cid == "admin":
					embed = HelpMenu.AdminMenu()
					await interaction.edit_original_response(embed=embed, view=self)

				# --- 開發日誌與翻頁邏輯 ---
				elif cid in ["changelog", "prev_page", "next_page"]:
					if cid == "changelog":
						self.changelog_page = 1  # 每次點擊開發日誌重置為第1頁
					elif cid == "prev_page":
						self.changelog_page = max(1, self.changelog_page - 1)
					elif cid == "next_page":
						self.changelog_page = min(self.changelog_obj.max_pages, self.changelog_page + 1)

					# 確保翻頁按鈕有在畫面上
					if self.prev_btn not in self.children:
						self.add_item(self.prev_btn)
					if self.next_btn not in self.children:
						self.add_item(self.next_btn)

					# 第一頁時停用上一頁，最後一頁時停用下一頁
					self.prev_btn.disabled = (self.changelog_page == 1)
					self.next_btn.disabled = (self.changelog_page == self.changelog_obj.max_pages)

					# 獲取對應頁數的 Embed，並更新 View (包含翻頁按鈕)
					embed = self.changelog_obj.get_page(self.changelog_page)
					await interaction.edit_original_response(embed=embed, view=self)

			# 綁定回呼函數 (Callbacks)
			self.game.callback = Button_callback
			self.admin.callback = Button_callback
			self.function.callback = Button_callback
			self.economy.callback = Button_callback
			self.music.callback = Button_callback
			self.changelog.callback = Button_callback
			self.prev_btn.callback = Button_callback
			self.next_btn.callback = Button_callback

			# 將初始主按鈕加進 View 裡面
			self.add_item(self.game)
			self.add_item(self.function)
			self.add_item(self.economy)
			self.add_item(self.music)
			self.add_item(self.admin)
			self.add_item(self.changelog)
	
class Function(commands.Cog):
	def __init__(self,bot): 
		self.bot = bot
		
	@app_commands.command(description="查詢指令列表")
	async def help(self,interaction):
		embed = HelpMenu.DefaultMenu()
		view = HelpMenu.MenuChanger()
		await interaction.response.send_message(embed=embed, view=view)


	@app_commands.command(description="查詢機器人延遲")
	async def ping(self,interaction):
		await interaction.response.send_message(f"{round(self.bot.latency*1000)} ms")

	
	@app_commands.command(description="讓機器人複誦訊息")
	async def say(self,interaction, 訊息:str):
		await interaction.response.send_message(訊息)

	@app_commands.command(description="建立並使用輪盤")
	@app_commands.describe(內容="輸入要轉的內容(用空格隔開)")
	async def wheel(self, interaction:discord.Interaction, 標題:str, 內容:str):
		optionlist = 內容.split()

		choice = random.choice(optionlist)
		embed = discord.Embed(title=標題,description=" ",color=0x3d993a)
		embed.add_field(name=choice, value="__ __", inline=False)
		
		await interaction.response.send_message("輪盤正在轉動中.")
		await asyncio.sleep(1)
		await interaction.edit_original_response(content="輪盤正在轉動中..")
		await asyncio.sleep(1)
		await interaction.edit_original_response(content="輪盤正在轉動中...")
		await asyncio.sleep(3)
		await interaction.edit_original_response(embed=embed)

	@app_commands.command(description="搜尋P網圖片")
	@app_commands.describe(目標="要搜尋的關鍵字", 頁數="要搜尋的頁數", 模式="搜尋不同尺度的圖片", ai="是否要顯示AI")
	@app_commands.choices(
		模式=[
		app_commands.Choice(name="無限制", value="all"),
		app_commands.Choice(name="普通版", value="safe"),
		app_commands.Choice(name="R18版", value="r18"),
		],
		ai=[
			app_commands.Choice(name="是", value="0"),
			app_commands.Choice(name="否", value="1"),
			]
	)
	async def pixiv(self, 
				interaction: discord.Interaction,
				目標:str,
				模式:app_commands.Choice[str] = None,
				ai:app_commands.Choice[str] = None,
				頁數:int = None
				):
		headers = {
			'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
			'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
			'cookie' : 'privacy_policy_notification=0; a_type=0; first_visit_datetime_pc=2024-04-21%2001%3A32%3A01; yuid_b=JEBnKFk; p_ab_id=2; p_ab_id_2=7; p_ab_d_id=1504854835; PHPSESSID=49594624_MUGA9qN0LHc7SaxiLC8zikJmDIm3y0UV; b_type=1; privacy_policy_agreement=7; c_type=24; __cf_bm=2UzltZVRO0lQ3kRBnroXGEsrQWl3hkGp38xMcr6rqxU-1731571149-1.0.1.1-ZFOcF_B4uZP_lxAy6XCRQugDqigjglohKJ4KbMoExAlCaowuBXiwbgDeCSu.RBvWBU67uphp3rEmJM_6zy50NvOlc_Jd3TUOd5yxGjRMkcU; cf_clearance=vgbaZaFEtl.ACdHRvwugj0bLRV5Gz75G4pl5AS7y6gI-1731571151-1.2.1.1-IovSe9hgs6DOz4bBU2yGTysKPZNPD2pHRmmNwCBrYjg4QWJFLJjxyMzz6NS1afb1hk5BJUiTX2UTUhLe.mogRpXqNNrRHyAdF6JByIBc6lh0khvRpwADd2QviXgng_FgEccnThXTrM9LrCl7IL68Z2YMaJFKZMyl.Y7uKaUP1tVQB2Mq9M6F2U69xOZJgKwIqo6dj9io3VAC.ukh3mIvJdB_c7IT839fa14HdKZ7yArUM.cGq62.8nEO6jT.UUglxZT3ub_8CqvHfu.LModXZz6awmWN68pj6WAmM29MM1humSBijcWDrZRCNo9BwHnJDGwg0CKtGSzJMbTCqGOanTOg_ksPMm.ATOYkDGYGMDQHfghP57tTw03K6PG1W7ybURthgGPEwYuvBkJPIKrLWQ'
		}
		
		page = 頁數 if 頁數 != None else 1
		mode = 模式.value if 模式 != None else "all"
		target = 目標
		ai_allow = ai if ai != None else 0

		site = f'https://www.pixiv.net/ajax/search/artworks/{target}?word={target}&order=date_d&mode={mode}&p={page}&csw=0&s_mode=s_tag&type=all&ai_type={ai_allow}&lang=zh_tw&version=7771f749f08256057464c8e0c95738854a753080'

		res = requests.get(site, headers=headers)
		resdict = json.loads(res.text)
		end = len(resdict['body']['illustManga']['data'])
		number = random.randint(0,end)

		try:
			ID = resdict['body']['illustManga']['data'][number]['id']
			await interaction.response.send_message(f'https://pixiv.cat/{ID}.jpg')

		except Exception as e:
			print(e)
			await interaction.response.send_message('無法找到圖片')
		


async def setup(bot):
	await bot.add_cog(Function(bot))