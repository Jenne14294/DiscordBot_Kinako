import discord
import random
import asyncio
import json

from discord.ext import commands
from discord.ui import Button, View, TextInput, Modal
from discord import app_commands

maps_file = open("./holy_legend/maps.json", "r",encoding="utf-8")
maps_data = json.load(maps_file)

items_file = open("./holy_legend/items.json","r",encoding="utf-8")
items_data = json.load(items_file)

class_file = open("./holy_legend/classes.json","r",encoding="utf-8")
class_data = json.load(class_file)

chest_file = open("./holy_legend/chests.json","r",encoding="utf-8")
chest_data = json.load(chest_file)

event_file = open("./holy_legend/events.json","r",encoding="utf-8")
event_data = json.load(event_file)

skills_file = open("./holy_legend/skills.json","r",encoding="utf-8")
skills_data = json.load(skills_file)

tech_file = open("./holy_legend/tech.json","r",encoding="utf-8")
tech_data = json.load(tech_file)

daily_file = open("./holy_legend/daily_quest.json","r",encoding="utf-8")
daily_data = json.load(daily_file)



class hl(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

		self.holy_legend = app_commands.ContextMenu(name="聖魂傳奇",callback=self._hl)
		self.bot.tree.add_command(self.holy_legend)

	async def intro_page(self,interaction):
		await interaction.response.defer()
		embed = discord.Embed(title="聖魂傳奇",description="遊戲介紹")
		embed.add_field(name="探索",value="探索當前地圖可能會出現的東西(敵人/寶箱/事件/商人)",inline=False)
		embed.add_field(name="戰鬥",value="以回合制進行，能夠使用【攻擊】、【技能】、【防禦】、【道具】",inline=False)
		embed.add_field(name="技能",value="自己選擇想要學習的技能，並能在戰鬥中使用",inline=False)
		embed.add_field(name="能力",value="分配自己的能力，讓戰鬥更加簡單",inline=False)
		embed.add_field(name="復活",value="戰鬥中死亡會回到村莊，需要花費1000塊錢才可以在祝福之泉復活，或是戰鬥死亡後自動使用【祝福之圖騰】",inline=False)

		view = View(timeout=None)
		start = Button(label="開始冒險",style=discord.ButtonStyle.primary,custom_id="start")
		data = Button(label="資料介面",style=discord.ButtonStyle.primary,custom_id="data")
		view.add_item(start)
		view.add_item(data)
		start.callback = self._hl
		data.callback = self.data_page
		
		await interaction.edit_original_response(embed=embed,view=view)

	async def skill_page(self,interaction):
		await interaction.response.defer()
		
		view = View(timeout=None)

		skillID = interaction.data['custom_id']

		for i in range(len(skills_data)):
			if skillID == str(i):
				if db[f'{interaction.user.id}'][1]['status']['skillpoints'] >= skills_data[f'{i}']['needPoints'] and skills_data[f'{i}']['name'] not in db[f'{interaction.user.id}'][1]['skills']:
					db[f'{interaction.user.id}'][1]['skills'].append(skills_data[f'{i}']['name'])
					db[f'{interaction.user.id}'][1]['status']['skillpoints'] -= skills_data[f'{i}']['needPoints']
			

		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}")
		
		embed.add_field(name="剩餘技能點",value=f"{db[f'{interaction.user.id}'][1]['status']['skillpoints']}",inline=False)

		class_name = db[f'{interaction.user.id}'][1]['status']['class']
		
		try:
			for i in range(len(class_data)):
				if class_name == class_data[f'{i}']['name']:
					class_type = class_data[f'{i}']['name']
			for i in range(len(skills_data)):
				if class_type == skills_data[f'{i}']['class']:
					name = skills_data[f'{i}']['name']
					describe = skills_data[f'{i}']['describe']
					times = skills_data[f'{i}']['times']
					type = skills_data[f'{i}']['consumeType']
					amount = skills_data[f'{i}']['consume']
					point = skills_data[f'{i}']['needPoints']
					STRmultiply = skills_data[f'{i}']['STRmultiply']
					DEXmultiply = skills_data[f'{i}']['DEXmultiply']
					CONmultiply = skills_data[f'{i}']['CONmultiply']
					INTmultiply = skills_data[f'{i}']['INTmultiply']
				
					embed.add_field(name=f"{name}\n{describe}",value=f"消耗 {amount * times} 點 {type}\n力量倍率：{STRmultiply}\n敏捷倍率：{DEXmultiply}\n體質倍率：{CONmultiply}\n智力倍率：{INTmultiply}\n所需點數：{point}")
				
					if name not in db[f'{interaction.user.id}'][1]['skills'] and db[f'{interaction.user.id}'][1]['status']['skillpoints'] >= point:
						skill = Button(label=name,style=discord.ButtonStyle.primary,custom_id=f'{i}')
						skill.callback = self.skill_page
						view.add_item(skill)

		except:
			pass
				

		back = Button(label="上一頁",style=discord.ButtonStyle.secondary,custom_id="back")
		back.callback = self.data_page
		
		view.add_item(back)

		
		

		await interaction.edit_original_response(embed=embed,view=view)


	async def ATT_point(self,interaction):
		await interaction.response.defer()

		ATTtype = interaction.data['custom_id']
		try:
			if db[f"{interaction.user.id}"][1]['status']['ATTpoints'] >= 1:
				db[f"{interaction.user.id}"][1]['status'][ATTtype] += 1
				if ATTtype == 'STR':
					db[f"{interaction.user.id}"][1]['status']['maxHP'] += 2
					db[f"{interaction.user.id}"][1]['status']['HP'] += 2
				elif ATTtype == 'CON':
					db[f"{interaction.user.id}"][1]['status']['maxHP'] += 5
					db[f"{interaction.user.id}"][1]['status']['HP'] += 5
				elif ATTtype == 'INT':
					db[f"{interaction.user.id}"][1]['status']['maxMP'] += 7
					db[f"{interaction.user.id}"][1]['status']['MP'] += 7
				db[f"{interaction.user.id}"][1]['status']['ATTpoints'] -= 1
		except:
			pass
			
		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}")
		
		embed.add_field(name="力量",value=f"{db[f'{interaction.user.id}'][1]['status']['STR']}",inline=False)
		embed.add_field(name="敏捷",value=f"{db[f'{interaction.user.id}'][1]['status']['DEX']}",inline=False)
		embed.add_field(name="體質",value=f"{db[f'{interaction.user.id}'][1]['status']['CON']}",inline=False)
		embed.add_field(name="智力",value=f"{db[f'{interaction.user.id}'][1]['status']['INT']}",inline=False)
		embed.add_field(name="剩餘能力點",value=f"{db[f'{interaction.user.id}'][1]['status']['ATTpoints']}",inline=False)

		view = View(timeout=None)

		STR = Button(label="力量",style=discord.ButtonStyle.primary,custom_id="STR")
		DEX = Button(label="敏捷",style=discord.ButtonStyle.primary,custom_id="DEX")
		CON = Button(label="體質",style=discord.ButtonStyle.primary,custom_id="CON")
		INT = Button(label="智力",style=discord.ButtonStyle.primary,custom_id="INT")
		back = Button(label="上一頁",style=discord.ButtonStyle.secondary,custom_id="back")

		view.add_item(STR)
		view.add_item(DEX)
		view.add_item(CON)
		view.add_item(INT)
		view.add_item(back)

		STR.callback = self.ATT_point
		DEX.callback = self.ATT_point
		CON.callback = self.ATT_point
		INT.callback = self.ATT_point
		back.callback = self.data_page



		await interaction.edit_original_response(embed=embed,view=view)

	async def change_class(self,interaction):
		await interaction.response.defer()
		view = View(timeout=None)
		StatusText = ""
		
		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}")
		
		for i in range(len(class_data)):
			STR = class_data[str(i)]['STR']
			DEX = class_data[str(i)]['DEX']
			CON = class_data[str(i)]['CON']
			INT = class_data[str(i)]['INT']
			name = class_data[str(i)]['name']
			describe = class_data[str(i)]['describe']
			tech = class_data[str(i)]['technique']
			minLevel = class_data[str(i)]['minLevel']
			
			
			embed.add_field(name=f"名字：{name}\n介紹：{describe}\n最低等級：{minLevel	}",value=f"天賦：{tech}\n基礎力量:{STR}\n基礎敏捷:{DEX}\n基礎體質:{CON}\n基礎智力:{INT}")

			if db[f'{interaction.user.id}'][1]['status']['level'] >= minLevel:
				Class = Button(label=name,style=discord.ButtonStyle.primary,custom_id=str(i))
				Class.callback = self.change_class
				view.add_item(Class)


		
		oldClassID = db[f'{interaction.user.id}'][1]['status']['class']
		for i in range(len(class_data)):
			if class_data[str(i)]['name'] == oldClassID:
				oldClassID = str(i)
				break
		newClassID = interaction.data['custom_id']

		
		

		if newClassID in class_data:
			if oldClassID == "無":
				old_HP = 0
				old_MP = 0
				old_STR = 0
				old_DEX = 0
				old_CON = 0
				old_INT = 0
				oldTech = "無"
			else:
				old_HP = class_data[oldClassID]['HP']
				old_MP = class_data[oldClassID]['MP']
				old_STR = class_data[oldClassID]['STR']
				old_DEX = class_data[oldClassID]['DEX']
				old_CON = class_data[oldClassID]['CON']
				old_INT = class_data[oldClassID]['INT']
				oldTech = class_data[oldClassID]['technique']

			new_HP = class_data[newClassID]['HP']
			new_MP = class_data[newClassID]['MP']
			new_STR = class_data[newClassID]['STR']
			new_DEX = class_data[newClassID]['DEX']
			new_CON = class_data[newClassID]['CON']
			new_INT = class_data[newClassID]['INT']
			newTech = class_data[newClassID]['technique']

			db[f'{interaction.user.id}'][1]['status']['HP'] -= old_HP
			db[f'{interaction.user.id}'][1]['status']['maxHP'] -= old_HP
			db[f'{interaction.user.id}'][1]['status']['MP'] -= old_MP
			db[f'{interaction.user.id}'][1]['status']['maxMP'] -= old_MP
			db[f'{interaction.user.id}'][1]['status']['STR'] -= old_STR
			db[f'{interaction.user.id}'][1]['status']['DEX'] -= old_DEX
			db[f'{interaction.user.id}'][1]['status']['CON'] -= old_CON
			db[f'{interaction.user.id}'][1]['status']['INT'] -= old_INT
			if oldTech in db[f'{interaction.user.id}'][1]['skills']:
				db[f'{interaction.user.id}'][1]['skills'].remove(oldTech)
				

			db[f'{interaction.user.id}'][1]['status']['HP'] += new_HP
			db[f'{interaction.user.id}'][1]['status']['maxHP'] += new_HP
			db[f'{interaction.user.id}'][1]['status']['MP'] += new_MP
			db[f'{interaction.user.id}'][1]['status']['maxMP'] += new_MP
			db[f'{interaction.user.id}'][1]['status']['STR'] += new_STR
			db[f'{interaction.user.id}'][1]['status']['DEX'] += new_DEX
			db[f'{interaction.user.id}'][1]['status']['CON'] += new_CON
			db[f'{interaction.user.id}'][1]['status']['INT'] += new_INT
			if newTech not in db[f'{interaction.user.id}'][1]['skills']:
				db[f'{interaction.user.id}'][1]['skills'].append(newTech)
			

			db[f'{interaction.user.id}'][1]['status']['class'] = class_data[str(newClassID)]['name']
			StatusText = f"你的職業已變更成{class_data[str(newClassID)]['name']}"

		cancel = Button(label=f"取消",style=discord.ButtonStyle.secondary,custom_id=f"cancel")
		cancel.callback = self.data_page
		view.add_item(cancel)

		embed.add_field(name="==========================================================",value="",inline=False)
		embed.add_field(name="狀態訊息",value=StatusText,inline=False)

		await interaction.edit_original_response(embed=embed,view=view)
		
	async def reset_comfirm(self,interaction):
		await interaction.response.defer()
		view = View(timeout=None)
		
		author = self.bot.get_user(493411441832099861)
		user = interaction.user
		
		true = Button(label="我很確定!!",style=discord.ButtonStyle.danger,custom_id="true",disabled=True)
		false = Button(label="還是不要好了...",style=discord.ButtonStyle.success,custom_id="false",disabled=True)
		
		view.add_item(true)
		view.add_item(false)
		
		keylist = []
		keys = db.keys()
		for key in keys:
			keylist.append(key)
			
		hlmaxHP = random.randint(200,500)
		hlmaxMP = random.randint(50,150)
		hlSTR = random.randint(0,5)
		hlDEX = random.randint(0,5)
		hlCON = random.randint(0,5)
		hlINT = random.randint(0,5)
			
		if interaction.data["custom_id"] == "true":
			if str(user.id) in keylist:
				try:
					await interaction.edit_original_response(content="資料重置中...",embed=None,view=None)
					db[f"{user.id}"][1] = {
						'status':
								{	
									'level':1,
									'class': "無",
									'actions':0,
									'maxActions':0,
									'HP':hlmaxHP,
									 'maxHP':hlmaxHP,
									 'MP':hlmaxMP,
									 'maxMP':hlmaxMP,
									 'STR':hlSTR,
									 'DEX':hlDEX,
									 'CON':hlCON,
									 'INT':hlINT,
									 'EXP':0,
									 'baseEXP':150,
									'totalEXP':0,
									'ATTpoints':0,
									'skillpoints':0
								},
						'weapons':[],
						'items':{},
						'armour':[],
						'equipments':
								{
									'mainhand': "無",
									'offhand': "無",
									'helmet': "無",
									'armor': "無",
									'leggings': "無",
									'boots': "無",
									'necklace': "無",
									'ring1': "無",
									'ring2': "無",
									'cloak': "無",
									'amulet': "無"
								},
						'skills':[],
						'Quests':
						{
							"MQID":0,
							"SQlist":[],
							"DQlist":[]
						},
						'enemies':
						{
							'enemy1':
							{
								'name':'無',
								'HP':0,
								'MP':0,
								'ATK':0,
								'DEF':0,
								'SPD':0,
								'skills':[]
							},
							'enemy2':
							{
								'name':'無',
								'HP':0,
								'MP':0,
								'ATK':0,
								'DEF':0,
								'SPD':0,
								'skills':[]
							},
							'enemy3':
							{
								'name':'無',
								'HP':0,
								'MP':0,
								'ATK':0,
								'DEF':0,
								'SPD':0,
								'skills':[]
							},
							'enemy4':
							{
								'name':'無',
								'HP':0,
								'MP':0,
								'ATK':0,
								'DEF':0,
								'SPD':0,
								'skills':[]
							},
							'enemy5':
							{
								'name':'無',
								'HP':0,
								'MP':0,
								'ATK':0,
								'DEF':0,
								'SPD':0,
								'skills':[]
							},
							'mapID':"0"
						}
					}
					await asyncio.sleep(5)
					await interaction.edit_original_response(content=f"{user.mention}的資料重置成功!",view=None,embed=None)
				except:
					await author.send(f"{interaction.user.name}的資料有點問題")
			else:
				await interaction.edit_original_response(content=f"無法重置{user.mention}的資料,因為尚未註冊",embed=None)
		else:
			await interaction.edit_original_response(content=f"{user.mention}已取消重置",view=None,embed=None)
	
	
	async def reset_data(self,interaction):
			user = interaction.user
			await interaction.response.defer()
			true = Button(label="我很確定!!",style=discord.ButtonStyle.danger,custom_id="true")
			false = Button(label="還是不要好了...",style=discord.ButtonStyle.success,custom_id="false")

			true.callback = self.reset_comfirm
			false.callback = self.reset_comfirm
			view = View(timeout=None)
			view.add_item(true)
			view.add_item(false)
			await interaction.edit_original_response(content=f"{user.mention}你真的要重置資料嗎?該動作無法復原",view=view)


	async def quest_menu(self,interaction):
		await interaction.response.defer()

		view = View(timeout=None)

		quest_id = interaction.data['custom_id']

		if quest_id != 'quest':
			for i in range(len(daily_data)):
				if daily_data[f'{i}']['title'] == quest_id:
					complete_needItem = daily_data[f'{i}']['needItem']
					complete_amount = daily_data[f'{i}']['amount']
					complete_reward = daily_data[f'{i}']['reward']
					complete_rewardItem = daily_data[f'{i}']['rewardItem']

					try:
						if db[f'{interaction.user.id}'][1]['items'][complete_needItem] >= complete_amount:
							db[f'{interaction.user.id}'][1]['items'][complete_needItem] -= complete_amount
							if complete_rewardItem == "金錢":
								db[f'{interaction.user.id}'][0]['money'] += complete_reward
							else:
								pass
							db[f'{interaction.user.id}'][1]['Quests']['DQlist'].remove(daily_data[f'{i}']['title'])
					except:
						pass

		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}")

		for i in range(len(db[f'{interaction.user.id}'][1]['Quests']['DQlist'])):
			quest_name = db[f'{interaction.user.id}'][1]['Quests']['DQlist'][i]
			for j in range(len(daily_data)):
				if quest_name == daily_data[f'{j}']['title']:
					content = daily_data[f'{j}']['content']
					needItem = daily_data[f'{j}']['needItem']
					amount = daily_data[f'{j}']['amount']
					reward = daily_data[f'{j}']['reward']
					rewardItem = daily_data[f'{j}']['rewardItem']
					
					embed.add_field(name=f"{quest_name}",value=f"內容:{content}\n目標：{amount} 個 {needItem}\n獎勵：{reward} {rewardItem}")
					complete = Button(label=quest_name,style=discord.ButtonStyle.primary,custom_id=quest_name)
					complete.callback = self.quest_menu
					view.add_item(complete)

		back = Button(label="上一頁",style=discord.ButtonStyle.secondary)
		back.callback = self.data_page
		view.add_item(back)

		await interaction.edit_original_response(embed=embed,view=view)

	async def data_page(self,interaction):
		await interaction.response.defer()
		
		maxHP = db[f'{interaction.user.id}'][1]['status']['maxHP']
		maxMP = db[f'{interaction.user.id}'][1]['status']['maxMP']
		HP = db[f'{interaction.user.id}'][1]['status']['HP']
		MP = db[f'{interaction.user.id}'][1]['status']['MP']
		STR = db[f'{interaction.user.id}'][1]['status']['STR']
		DEX = db[f'{interaction.user.id}'][1]['status']['DEX']
		CON = db[f'{interaction.user.id}'][1]['status']['CON']
		INT = db[f'{interaction.user.id}'][1]['status']['INT']
		
		PATK = round(10 + (STR / 2) + DEX / 5, 2)
		MATK = round(7.5 + (STR / 5) + INT / 3, 2)
		PDEF = round(CON * 0.75 + STR / 7, 2)
		MDEF = round(CON * 0.25 + INT / 4, 2)
		SPD = round(DEX / 1.5, 2)
		Dodge = round(DEX / 4,2)
		Crit = round(DEX / 1.5 + INT / 4.5, 2)

		if Dodge < 0:
			Dodge = 0.00

		if Crit < 0:
			Crit = 0.00
		
		
		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}")

		embed.add_field(name="生命值",value=f"{round(HP)} / {round(maxHP)}")
		embed.add_field(name="魔力值",value=f"{round(MP)} / {round(maxMP)}")
		embed.add_field(name="物理攻擊",value=f"{PATK}")
		embed.add_field(name="魔法攻擊",value=f"{MATK}")
		embed.add_field(name="物理防禦",value=f"{PDEF}")
		embed.add_field(name="魔法防禦",value=f"{MDEF}")
		embed.add_field(name="速度",value=f"{SPD}")
		embed.add_field(name="迴避率",value=f"{Dodge} %")
		embed.add_field(name="爆擊率",value=f"{Crit} %")

		view = View(timeout=None)
		equip = Button(label="裝備介面",style=discord.ButtonStyle.primary,custom_id="equip",row=1)
		items = Button(label="道具介面",style=discord.ButtonStyle.primary,custom_id="items",row=1)
		quest = Button(label="任務介面",style=discord.ButtonStyle.primary,custom_id="quest",row=1)
		
		classes = Button(label="變更職業",style=discord.ButtonStyle.primary,custom_id="classes",row=2)
		ATT = Button(label="分配能力",style=discord.ButtonStyle.primary,custom_id="ATT",row=2)
		skill = Button(label="學習技能",style=discord.ButtonStyle.primary,custom_id="skill",row=2)
		
		reset = Button(label="重置資料",style=discord.ButtonStyle.danger,custom_id="reset",row=3)
		start = Button(label="繼續冒險",style=discord.ButtonStyle.secondary,custom_id="start",row=3)

		equip.callback = None#self.change_equip
		items.callback = self.item_page
		ATT.callback = self.ATT_point
		skill.callback = self.skill_page
		start.callback = self.start_adventure
		reset.callback = self.reset_data
		classes.callback = self.change_class
		quest.callback = self.quest_menu
		
		view.add_item(equip)
		view.add_item(items)
		view.add_item(quest)
		
		view.add_item(ATT)
		view.add_item(skill)
		view.add_item(classes)
		
		view.add_item(reset)
		view.add_item(start)

		await interaction.edit_original_response(embed=embed,view=view)		

	async def change_map(self,interaction:discord.Interaction):
		await interaction.response.defer()

		try:
			int(interaction.data['custom_id'])
			if db[f'{interaction.user.id}'][1]['status']['HP'] > 0 or interaction.data['custom_id'] in ["0","6"]:
				str(interaction.data['custom_id'])
				db[f'{interaction.user.id}'][1]['enemies']['mapID'] = interaction.data['custom_id']
				StatusText = "已切換地圖"
			else:
				StatusText = "你目前無法戰鬥，無法前往該地圖，請先去【祝福之泉】復活"

		except:
			pass


		mapID = db[f'{interaction.user.id}'][1]['enemies']['mapID']
		embed = discord.Embed(title="聖魂傳奇",description=f"當前地圖：{maps_data[f'{mapID}']['name']}")
		view = View(timeout=None)
		
		for i in range(-4,5):
			NPCs = ""
			Maplist = int(mapID) + i
			try:
				for j in range(0,len(maps_data[f'{Maplist}']['NPCs'])):
					NPCname = maps_data[f'{Maplist}']['NPCs'][f'{j}']['name']
					NPCs = NPCs + NPCname + "、"
		
				if NPCs.endswith("、"):
					NPCs = NPCs[:len(NPCs) - 1]
				
				embed.add_field(name=f"MAP00{int(mapID) + i}",value=f"名字：{maps_data[f'{Maplist}']['name']}\n推薦等級：{maps_data[f'{Maplist}']['level']}\n出沒生物：{NPCs}")
				map = Button(label=f"{maps_data[f'{Maplist}']['name']}",style=discord.ButtonStyle.primary,custom_id=f"{Maplist}")
				map.callback = self.change_map
				view.add_item(map)

			except:
				pass

		back = Button(label="繼續冒險",style=discord.ButtonStyle.secondary,custom_id="back",row=2)
		view.add_item(back)
		
		back.callback = self.start_adventure
		

		await interaction.edit_original_response(embed=embed,view=view)


	async def item_page(self,interaction:discord.Interaction):
		await interaction.response.defer()

		item_name = interaction.data['custom_id']
		for i in range(len(items_data)):
			if items_data[f'{i}']['name'] == item_name:
				if items_data[f'{i}']['type'] in ["HP","MP"]:
					type = items_data[f'{i}']['type']
					if db[f'{interaction.user.id}'][1]['status'][f'{type}'] != db[f'{interaction.user.id}'][1]['status'][f'max{type}']:
						if db[f'{interaction.user.id}'][1]['status'][f'{type}'] + items_data[f'{i}']['utility'] > db[f'{interaction.user.id}'][1]['status'][f'max{type}']:
							db[f'{interaction.user.id}'][1]['status'][f'{type}'] = db[f'{interaction.user.id}'][1]['status'][f'max{type}']
							db[f'{interaction.user.id}'][1]['items'][f'{item_name}'] -= 1
						else:
							db[f'{interaction.user.id}'][1]['status'][f'{type}'] += items_data[f'{i}']['utility']
							db[f'{interaction.user.id}'][1]['items'][f'{item_name}'] -= 1
							
				elif items_data[f'{i}']['type'] == 'revive':
					if db[f'{interaction.user.id}'][1]['status']['HP'] <= 0:
						db[f'{interaction.user.id}'][1]['status']['HP'] = db[f'{interaction.user.id}'][1]['status']['maxHP']
						db[f'{interaction.user.id}'][1]['items'][f'{item_name}'] -= 1
					else:
						pass
						

		view = View(timeout=None)

		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}\n生命值：{round(db[f'{interaction.user.id}'][1]['status']['HP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxHP'])}\n魔力值：{round(db[f'{interaction.user.id}'][1]['status']['MP'])} /{round(db[f'{interaction.user.id}'][1]['status']['maxMP'])}")
		
		for i in range(0,len(items_data)):
			item_name = items_data[f'{i}']['name']
			describe = items_data[f'{i}']['describe']
			item_type = items_data[f'{i}']['type']
			try:
				if db[f'{interaction.user.id}'][1]['items'][f'{item_name}'] >= 1:
					if item_type != "item":
						item = Button(label=f"{item_name}",style=discord.ButtonStyle.primary,custom_id=f"{item_name}")
						item.callback = self.item_page
						view.add_item(item)
						embed.add_field(name=f"{item_name}\n{describe}\n剩餘數量：{db[f'{interaction.user.id}'][1]['items'][f'{item_name}']}",value=" ")
					else:
						embed.add_field(name=f"{item_name}\n{describe}\n剩餘數量：{db[f'{interaction.user.id}'][1]['items'][f'{item_name}']}",value=" ")
			except:
				pass

		back = Button(label="上一頁",style=discord.ButtonStyle.secondary)
		back.callback = self.data_page
		view.add_item(back)

		await interaction.edit_original_response(embed=embed,view=view)

	async def battle_item(self,interaction:discord.Interaction):
		await interaction.response.defer()

		view = View(timeout=None)
		for i in range(0,len(items_data)):
			item_name = items_data[f'{i}']['name']
			try:
				if db[f'{interaction.user.id}'][1]['items'][f'{item_name}'] >= 1 and items_data[f'{i}']['type'] in ["HP","MP"]:
					item = Button(label=f"{item_name}",style=discord.ButtonStyle.primary,custom_id=f"{item_name}")
					item.callback = self.battle_action
					view.add_item(item)
			except:
				pass

		cancel = Button(label=f"取消",style=discord.ButtonStyle.secondary,custom_id=f"cancel")
		cancel.callback = self.battle_action
		view.add_item(cancel)

		await interaction.edit_original_response(view=view)

	async def battle_skill(self,interaction:discord.Interaction):
		await interaction.response.defer()

		view = View(timeout=None)

		#獲取技能列表
		for j in range(len(class_data)):
			class_name = db[f'{interaction.user.id}'][1]['status']['class']
			if class_name == class_data[f'{j}']['name']:
				class_type = class_data[f'{j}']['name']
		for i in range(0,len(skills_data)):
			skill_name = skills_data[f'{i}']['name']
			skill_type = skills_data[f'{i}']['class']
			if skill_type == class_type:
				if skill_name in db[f'{interaction.user.id}'][1]['skills']:
					if db[f'{interaction.user.id}'][1]['status']['MP'] >= skills_data[f'{i}']['consume'] * skills_data[f'{i}']['times']:
						skill = Button(label=f"{skill_name}",style=discord.ButtonStyle.primary,custom_id=f"{skill_name}")
						skill.callback = self.battle_action
						view.add_item(skill)


		cancel = Button(label=f"取消",style=discord.ButtonStyle.secondary,custom_id=f"cancel")
		cancel.callback = self.battle_action
		view.add_item(cancel)

		await interaction.edit_original_response(view=view)


	async def trigger_event(self,interaction):
		await interaction.response.defer()
		view = View(timeout=None)
		eventType = str(random.randint(0,len(event_data) - 1))
		
		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}\n生命值：{round(db[f'{interaction.user.id}'][1]['status']['HP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxHP'])}\n魔力值：{round(db[f'{interaction.user.id}'][1]['status']['MP'])} /{round(db[f'{interaction.user.id}'][1]['status']['maxMP'])}")

		describe = event_data[eventType]['describe']
		type = event_data[eventType]['type']
		amount = event_data[eventType]['amount']
		multiply = event_data[eventType]['multiply']

		leave = Button(label="離開",style=discord.ButtonStyle.secondary)
		leave.callback = self.search_field
		view.add_item(leave)

		if type == 'money':
			db[f'{interaction.user.id}'][0]['money'] += amount
			db[f'{interaction.user.id}'][0]['money'] = round(db[f'{interaction.user.id}'][0]['money'] * multiply)
		
		embed.add_field(name="==========================================================",value="",inline=False)
		embed.add_field(name="狀態訊息",value= describe,inline=False)

		await interaction.edit_original_response(embed=embed,view=view)


	async def open_chest(self,interaction):
		await interaction.response.defer()

		view = View(timeout=None)
		
		chestType = str(random.randint(0,len(chest_data) - 1))
		
		embed = discord.Embed(title=f"{interaction.user.name}\n職業：{db[f'{interaction.user.id}'][1]['status']['class']}",description=f"等級：{db[f'{interaction.user.id}'][1]['status']['level']}\n經驗值：{db[f'{interaction.user.id}'][1]['status']['EXP']} / {db[f'{interaction.user.id}'][1]['status']['baseEXP']}\n生命值：{round(db[f'{interaction.user.id}'][1]['status']['HP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxHP'])}\n魔力值：{round(db[f'{interaction.user.id}'][1]['status']['MP'])} /{round(db[f'{interaction.user.id}'][1]['status']['maxMP'])}")

		describe = chest_data[chestType]['describe']
		item = chest_data[chestType]['item']

		leave = Button(label="離開",style=discord.ButtonStyle.secondary)
		leave.callback = self.search_field
		view.add_item(leave)

		try:
			db[f'{interaction.user.id}'][1]['items'][item] += 1
		except:
			db[f'{interaction.user.id}'][1]['items'][item] = 1
		
		embed.add_field(name="==========================================================",value="",inline=False)
		embed.add_field(name="狀態訊息",value= describe,inline=False)

		await interaction.edit_original_response(embed=embed,view=view)

	async def battle_action(self,interaction:discord.Interaction):
		await interaction.response.defer()

		mapID = db[f"{interaction.user.id}"][1]['enemies']['mapID']
		action_name = interaction.data['custom_id']

		view = View(timeout=None)

		attack = Button(label="攻擊",style=discord.ButtonStyle.primary,custom_id="attack")
		defend = Button(label="防禦",style=discord.ButtonStyle.primary,custom_id="defend")
		skill = Button(label="技能",style=discord.ButtonStyle.primary,custom_id="skill")
		item = Button(label="道具",style=discord.ButtonStyle.primary,custom_id="item")
		run = Button(label="逃跑",style=discord.ButtonStyle.secondary,custom_id="run",row=2)

		attack.callback = self.battle_action
		defend.callback = self.battle_action
		skill.callback = self.battle_skill
		item.callback = self.battle_item
		run.callback = self.start_adventure

		view.add_item(attack)
		view.add_item(defend)
		view.add_item(skill)
		view.add_item(item)
		view.add_item(run)

		StatusText = ""
		damageReduce = 1

		#選擇普攻
		if action_name == 'attack':
			db[f"{interaction.user.id}"][1]['status']['actions'] -= 1

			CritBuff = 1
				
			player_crit = round(db[f'{interaction.user.id}'][1]['status']["DEX"] / 1.5 + db[f'{interaction.user.id}'][1]['status']["INT"] / 4.5, 2)
			system_crit = round(random.uniform(1,100), 2)

			if system_crit <= player_crit:
				CritBuff = 2
				StatusText = "好耶！命中要害！"

			
			multiply = round(random.uniform(0.8,1.2),2)
				
			player_damage = (round(10 + (db[f'{interaction.user.id}'][1]['status']['STR'] // 2.5) + db[f'{interaction.user.id}'][1]['status']['DEX'] // 5)) * 4
			enemy_defend = round(db[f'{interaction.user.id}'][1]['enemies']['enemy1']['DEF'] * 2)
	
			total_damage = round((player_damage - enemy_defend) * multiply)
				
			StatusText += f"\n你對 {db[f'{interaction.user.id}'][1]['enemies']['enemy1']['name']} 造成了 {total_damage} 點傷害"
			db[f"{interaction.user.id}"][1]['enemies']['enemy1']['HP'] -= total_damage

		#選擇防禦
		elif action_name == 'defend':
			db[f"{interaction.user.id}"][1]['status']['actions'] -= 1
			damageReduce = 0.75
			StatusText = f"你正在防禦!"

		#使用道具
		for i in range(len(items_data)):
			if items_data[f'{i}']['name'] == action_name:
				if items_data[f'{i}']['type'] in ["HP","MP"]:
					type = items_data[f'{i}']['type']
					if db[f'{interaction.user.id}'][1]['status'][f'{type}'] < db[f'{interaction.user.id}'][1]['status'][f'max{type}']:
						if db[f'{interaction.user.id}'][1]['status'][f'{type}'] + items_data[f'{i}']['utility'] > db[f'{interaction.user.id}'][1]['status'][f'max{type}']:
							db[f'{interaction.user.id}'][1]['status'][f'{type}'] = db[f'{interaction.user.id}'][1]['status'][f'max{type}']
							db[f'{interaction.user.id}'][1]['items'][f'{action_name}'] -= 1
						else:
							db[f'{interaction.user.id}'][1]['status'][f'{type}'] += items_data[f'{i}']['utility']
							db[f'{interaction.user.id}'][1]['items'][f'{action_name}'] -= 1

						db[f"{interaction.user.id}"][1]['status']['actions'] -= 1
						StatusText = f"你使用了 {action_name}"

		#使用技能
		for i in range(len(skills_data)):
			if action_name == skills_data[f'{i}']['name']:
				player_damage = 0

				CritBuff = 1
				
				player_crit = round(db[f'{interaction.user.id}'][1]['status']["DEX"] / 1.5 + db[f'{interaction.user.id}'][1]['status']["INT"] / 4.5, 2)
				system_crit = round(random.uniform(1,100), 2)

				if system_crit <= player_crit:
					CritBuff = 2
					StatusText = "好耶！命中要害!"
				
				db[f"{interaction.user.id}"][1]['status']['actions'] -= 1
				
				tempSTR = db[f"{interaction.user.id}"][1]['status']['STR'] * skills_data[f'{i}']['STRmultiply']
				tempDEX = db[f"{interaction.user.id}"][1]['status']['DEX'] * skills_data[f'{i}']['DEXmultiply']
				tempCON = db[f"{interaction.user.id}"][1]['status']['CON'] * skills_data[f'{i}']['CONmultiply']
				tempINT = db[f"{interaction.user.id}"][1]['status']['INT'] * skills_data[f'{i}']['INTmultiply']
				
				if skills_data[f'{i}']['target'] == "one":
					for j in range(skills_data[f'{i}']['times']):
						multiply = round(random.uniform(0.8,1.2),2)
						Type = skills_data[f'{i}']['consumeType']
						Amount = skills_data[f'{i}']['consume']
						db[f'{interaction.user.id}'][1]['status'][Type] -= Amount
							
						player_damage += round(10 + (tempSTR) + (tempDEX) + (tempCON) + (tempINT)) * 4
					enemy_defend = round(db[f'{interaction.user.id}'][1]['enemies']['enemy1']['DEF'] * 2)
					total_damage = round((player_damage - enemy_defend) * multiply * CritBuff)
					StatusText = f"\n你使用了 {action_name} 對 {db[f'{interaction.user.id}'][1]['enemies']['enemy1']['name']} 造成了 {total_damage} 點傷害"
					db[f"{interaction.user.id}"][1]['enemies']['enemy1']['HP'] -= total_damage
						
				elif skills_data[f'{i}']['target'] == "all":
					player_damage += round(10 + (tempSTR) + (tempDEX) + (tempCON) + (tempINT)) * 4
					enemy_defend = round(db[f'{interaction.user.id}'][1]['enemies']['enemy1']['DEF'] * 2)
					total_damage = round((player_damage - enemy_defend) * multiply * CritBuff)
					StatusText = f"\n你使用了 {action_name} 對敵方全體造成了 {total_damage} 點傷害"
					db[f"{interaction.user.id}"][1]['enemies']['enemy1']['HP'] -= total_damage
					db[f"{interaction.user.id}"][1]['enemies']['enemy2']['HP'] -= total_damage
					db[f"{interaction.user.id}"][1]['enemies']['enemy3']['HP'] -= total_damage
					db[f"{interaction.user.id}"][1]['enemies']['enemy4']['HP'] -= total_damage
					db[f"{interaction.user.id}"][1]['enemies']['enemy5']['HP'] -= total_damage

				elif skills_data[f'{i}']['target'] == "self":
					HPplus = round(db[f"{interaction.user.id}"][1]['status']['maxHP'] * tempCON)
					MPplus = round(db[f"{interaction.user.id}"][1]['status']['maxMP'] * tempINT)

					db[f"{interaction.user.id}"][1]['status']['HP'] += HPplus
					db[f"{interaction.user.id}"][1]['status']['MP'] += MPplus

				elif skills_data[f'{i}']['target'] == 'random':
					enemylist = []
					for a in range(1,6):
						enemyname = db[f'{interaction.user.id}'][1]['enemies'][f'enemy{a}']['name']
						if enemyname != "無":
							enemylist.append(enemyname)
					
					for j in range(skills_data[f'{i}']['times']):
						multiply = round(random.uniform(0.8,1.2),2)
						Type = skills_data[f'{i}']['consumeType']
						Amount = skills_data[f'{i}']['consume']
						db[f'{interaction.user.id}'][1]['status'][Type] -= Amount
							
						player_damage = round(10 + (tempSTR) + (tempDEX) + (tempCON) + (tempINT)) * 4

						number = random.randint(1,len(enemylist))
						enemy_defend = round(db[f'{interaction.user.id}'][1]['enemies'][f'enemy{number}']['DEF'] * 2)
						total_damage = round((player_damage - enemy_defend) * multiply * CritBuff)
						StatusText += f"\n你使用了 {action_name} 對 {db[f'{interaction.user.id}'][1]['enemies'][f'enemy{number}']['name']} 造成了 {total_damage} 點傷害"
						db[f"{interaction.user.id}"][1]['enemies'][f'enemy{number}']['HP'] -= total_damage

		#敵人死亡前移
		for i in range(1,6):
			if db[f"{interaction.user.id}"][1]['enemies'][f'enemy1']['HP'] <= 0 and db[f"{interaction.user.id}"][1]['enemies'][f'enemy1']['name'] != "無":
				enemyname = db[f"{interaction.user.id}"][1]['enemies'][f'enemy1']['name']
			
			#獲取經驗值
				for i in range(len(maps_data[f'{mapID}']['NPCs'])):
					if maps_data[f'{mapID}']['NPCs'][f'{i}']['name'] == enemyname:
						
						EXP = random.randint(maps_data[f'{mapID}']['NPCs'][f'{i}']['minEXP'],maps_data[f'{mapID}']['NPCs'][f'{i}']['maxEXP'])
						db[f"{interaction.user.id}"][1]['status']['totalEXP'] += EXP
	
						#給予掉落物
						for j in range(len(maps_data[f'{mapID}']['NPCs'][f'{i}']['drops'])):
							drop_name = maps_data[f'{mapID}']['NPCs'][f'{i}']['drops'][f'{j}']['name']
							drop_chance = maps_data[f'{mapID}']['NPCs'][f'{i}']['drops'][f'{j}']['minChance']
							drop_count = random.randint(1,maps_data[f'{mapID}']['NPCs'][f'{i}']['drops'][f'{j}']['maxCount'])
	
							
							system_chance = round(random.uniform(0,1),2)
							
							if system_chance <= drop_chance:
								try:
									db[f'{interaction.user.id}'][1]['items'][drop_name] += drop_count
									StatusText += f"\n你獲得了 {drop_count} 個 {drop_name}"
								except:
									db[f'{interaction.user.id}'][1]['items'][drop_name] = drop_count
									StatusText += f"\n你獲得了 {drop_count} 個 {drop_name}"
	
				for i in range(1,5):
					db[f"{interaction.user.id}"][1]['enemies'][f'enemy{i}'] = db[f"{interaction.user.id}"][1]['enemies'][f'enemy{i+1}']
	
				db[f"{interaction.user.id}"][1]['enemies']['enemy5']['name'] = "無"
				db[f"{interaction.user.id}"][1]['enemies']['enemy5']['HP'] = 0
				db[f"{interaction.user.id}"][1]['enemies']['enemy5']['MP'] = 0
				db[f"{interaction.user.id}"][1]['enemies']['enemy5']['skills'] = []

			#戰鬥結束
			if db[f"{interaction.user.id}"][1]['enemies']['enemy1']['name'] == "無":
				totalEXP = db[f"{interaction.user.id}"][1]['status']['totalEXP']
				StatusText += f"\n戰鬥結束!你獲得了{totalEXP}點經驗值"
				db[f"{interaction.user.id}"][1]['status']['EXP'] += totalEXP
				db[f"{interaction.user.id}"][1]['status']['totalEXP'] = 0
			
				view = View(timeout=None)
					
				map = Button(label="切換地圖",style=discord.ButtonStyle.success,custom_id="change_map")
				search = Button(label="繼續探索",style=discord.ButtonStyle.primary,custom_id="continue")
				data = Button(label="資料介面",style=discord.ButtonStyle.secondary,custom_id="data")
					
				view.add_item(search)
				view.add_item(map)
				view.add_item(data)
					
				map.callback = self.change_map
				search.callback = self.search_field
				data.callback = self.data_page

			#升等
			if db[f"{interaction.user.id}"][1]['status']['EXP'] >= db[f"{interaction.user.id}"][1]['status']['baseEXP']:
				randomSTR = random.randint(0,2)
				randomDEX = random.randint(0,2)
				randomCON = random.randint(0,2)
				randomINT = random.randint(0,2)
				
				level = db[f"{interaction.user.id}"][1]['status']['level']
				StatusText += f"\n你升級了!目前是 {level + 1} 等"
				db[f"{interaction.user.id}"][1]['status']['EXP'] -= db[f"{interaction.user.id}"][1]['status']['baseEXP']
				db[f"{interaction.user.id}"][1]['status']['baseEXP'] = db[f"{interaction.user.id}"][1]['status']['baseEXP'] + (db[f"{interaction.user.id}"][1]['status']['level'] * 15)
				
				db[f"{interaction.user.id}"][1]['status']['level'] += 1
				db[f"{interaction.user.id}"][1]['status']['ATTpoints'] += 3
				db[f"{interaction.user.id}"][1]['status']['skillpoints'] += 1

				db[f"{interaction.user.id}"][1]['status']['STR'] += randomSTR
				db[f"{interaction.user.id}"][1]['status']['DEX'] += randomDEX
				db[f"{interaction.user.id}"][1]['status']['CON'] += randomCON
				db[f"{interaction.user.id}"][1]['status']['INT'] += randomINT
		
		#玩家行動結束
		if db[f"{interaction.user.id}"][1]['status']['actions'] <= 0 and db[f"{interaction.user.id}"][1]['enemies'][f'enemy1']['name'] != "無":
			
			enemyDamage = 0
			namelist = []
			for i in range(1,6):
				name = db[f"{interaction.user.id}"][1]['enemies'][f'enemy{i}']['name']
				HP = db[f"{interaction.user.id}"][1]['enemies'][f'enemy{i}']['HP']
				if name != "無" and HP >= 0:
					namelist.append(name)
			enemyCount = len(namelist)

			for i in range(1,enemyCount + 1):
				enemyDamage += db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['ATK']

			enemyDamage = enemyDamage * 4

			player_defend = round(db[f'{interaction.user.id}'][1]['status']['CON'] // 3 + db[f'{interaction.user.id}'][1]['status']['STR'] // 7)

			enemy_all_damage = round((enemyDamage - player_defend) * damageReduce)

			#閃避成功
			player_dodge = round(db[f'{interaction.user.id}'][1]['status']['DEX'] / 4, 2)
			system_dodge = random.uniform(0,player_dodge + 15)
			if system_dodge <= player_dodge:
				enemy_all_damage = 0
				StatusText += "\n你閃避了敵人的攻擊!"
			else:
				if enemy_all_damage > 0:
					StatusText += f"\n敵人對你造成了 {enemy_all_damage} 點傷害"
				else:
					enemy_all_damage = 0
					StatusText += "\n敵人沒有對你造成傷害!"
				
				
			db[f'{interaction.user.id}'][1]['status']['HP'] -= enemy_all_damage

			if db[f'{interaction.user.id}'][1]['status']['HP'] <= 0:
				if "祝福之圖騰" in db[f'{interaction.user.id}'][1]['items'] and db[f'{interaction.user.id}'][1]['items']['祝福之圖騰'] >= 1:
					db[f'{interaction.user.id}'][1]['status']['HP'] = db[f'{interaction.user.id}'][1]['status']['maxHP']
					db[f'{interaction.user.id}'][1]['items']['祝福之圖騰'] -= 1 
					StatusText = "祝福之圖騰化作光芒，你成功復活了!"
				else:
					StatusText = "戰鬥失敗!將把你傳送回隨機村莊"
					db[f'{interaction.user.id}'][1]['enemies']['mapID'] = random.choice(['0'])
					db[f'{interaction.user.id}'][1]['status']['HP'] = 0
			
			if interaction.data['custom_id'] == 'defend':
				db[f'{interaction.user.id}'][1]['status']['CON'] = round(db[f'{interaction.user.id}'][1]['status']['CON'] - 15)
					
			db[f'{interaction.user.id}'][1]['status']['actions'] = db[f'{interaction.user.id}'][1]['status']['maxActions']

		embed = discord.Embed(title="聖魂傳奇",description=" ")
		embed.add_field(name="敵人一",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人二",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人三",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人四",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人五",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['skills'][19:-1]}",inline=True)
		
		embed.add_field(name="==========================================================",value=" ",inline=False)
		
		embed.add_field(name=f"{interaction.user.name}",value=f"生命值：{round(db[f'{interaction.user.id}'][1]['status']['HP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxHP'])}\n魔力值：{round(db[f'{interaction.user.id}'][1]['status']['MP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxMP'])}\n回合數：{db[f'{interaction.user.id}'][1]['status']['actions']}\n當前地圖：{maps_data[f'{mapID}']['name']}",inline=False)

		embed.add_field(name="==========================================================",value=" ",inline=False)
		embed.add_field(name="狀態訊息",value=StatusText,inline=False)

		await interaction.edit_original_response(embed=embed,view=view)
		
		

	async def start_battle(self,interaction:discord.Interaction):
		await interaction.response.defer()

		mapID = db[f"{interaction.user.id}"][1]['enemies']['mapID']
		PSPD = db[f"{interaction.user.id}"][1]['status']['DEX'] // 1.5
		db[f"{interaction.user.id}"][1]['status']['totalEXP'] = 0
		
		maxenemy = random.randint(1,maps_data[mapID]['max'])
		for i in range(1,maxenemy + 1):
			choice = random.randint(0,len(maps_data[mapID]['NPCs']) - 1)
			
			ESPD = maps_data[f'{mapID}']['NPCs'][str(choice)]['SPD']
			
			actions = PSPD // ESPD
			if actions >= 1:
				db[f'{interaction.user.id}'][1]['status']['actions'] = round(actions)
				db[f'{interaction.user.id}'][1]['status']['maxActions'] = round(actions)
			else:
				db[f'{interaction.user.id}'][1]['status']['actions'] = 1
				db[f'{interaction.user.id}'][1]['status']['maxActions'] = 1

			
				
			db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['skills'] = maps_data[mapID]['NPCs'][str(choice)]['skills']
			db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['name'] = maps_data[mapID]['NPCs'][str(choice)]['name']
			db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['HP'] = maps_data[mapID]['NPCs'][str(choice)]['maxHP']
			db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['MP'] = maps_data[mapID]['NPCs'][str(choice)]['maxMP']
			db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['SPD'] = maps_data[mapID]['NPCs'][str(choice)]['SPD']
			db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['ATK'] = maps_data[mapID]['NPCs'][str(choice)]['ATK']
			db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['DEF'] = maps_data[mapID]['NPCs'][str(choice)]['DEF']

		StatusText = ""
		view = View(timeout=None)

		attack = Button(label="攻擊",style=discord.ButtonStyle.primary,custom_id="attack")
		defend = Button(label="防禦",style=discord.ButtonStyle.primary,custom_id="defend")
		skill = Button(label="技能",style=discord.ButtonStyle.primary,custom_id="skill")
		item = Button(label="道具",style=discord.ButtonStyle.primary,custom_id="item")
		run = Button(label="逃跑",style=discord.ButtonStyle.secondary,custom_id="run",row=2)

		attack.callback = self.battle_action
		defend.callback = self.battle_action
		skill.callback = self.battle_action
		item.callback = self.battle_action
		run.callback = self.start_adventure

		view.add_item(attack)
		view.add_item(defend)
		view.add_item(skill)
		view.add_item(item)
		view.add_item(run)


		embed = discord.Embed(title="聖魂傳奇",description=" ")
		embed.add_field(name="敵人一",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人二",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人三",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人四",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['skills'][19:-1]}",inline=True)
			
		embed.add_field(name="敵人五",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['skills'][19:-1]}",inline=True)
		
		embed.add_field(name="==========================================================",value=" ",inline=False)
		
		embed.add_field(name=f"{interaction.user.name}",value=f"生命值：{round(db[f'{interaction.user.id}'][1]['status']['HP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxHP'])}\n魔力值：{round(db[f'{interaction.user.id}'][1]['status']['MP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxMP'])}\n回合數：{actions}\n當前地圖：{maps_data[f'{mapID}']['name']}",inline=False)

		embed.add_field(name="==========================================================",value=" ",inline=False)
		embed.add_field(name="狀態訊息",value=StatusText,inline=False)

		await interaction.edit_original_response(embed=embed,view=view)


	async def search_field(self,interaction:discord.Interaction):
		await interaction.response.defer()

		view = View(timeout=None)

		event = random.randint(1,100)
		mapID = db[f'{interaction.user.id}'][1]['enemies']['mapID']

		if 1 <= event <= 75:
			StatusText = "發現怪物!"
			battle = Button(label="開始戰鬥",style=discord.ButtonStyle.primary,custom_id="battle")
			view.add_item(battle)
			battle.callback = self.start_battle

		elif 76 <= event <= 90:
			StatusText = "啥都沒有...!"
	
		elif 91 <= event <= 95:
			StatusText = "突發事件!"
			event = Button(label="開始事件",style=discord.ButtonStyle.primary,custom_id="event")
			view.add_item(event)
			event.callback = self.trigger_event

		elif 1 <= event <= 100:
			StatusText = "發現寶箱"
			chest = Button(label="打開寶箱",style=discord.ButtonStyle.primary,custom_id="chest")
			view.add_item(chest)
			chest.callback = self.open_chest

		map = Button(label="切換地圖",style=discord.ButtonStyle.success,custom_id="change_map",row=2)
		search = Button(label="繼續探索",style=discord.ButtonStyle.primary,custom_id="continue",row=2)
		data = Button(label="資料介面",style=discord.ButtonStyle.secondary,custom_id="data",row=2)
		
		view.add_item(search)
		view.add_item(map)
		view.add_item(data)
		
		map.callback = self.change_map
		search.callback = self.search_field
		data.callback = self.data_page
			
			

		embed = discord.Embed(title="聖魂傳奇",description=" ")
		embed.add_field(name="敵人一",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['skills']}",inline=True)
			
		embed.add_field(name="敵人二",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['skills']}",inline=True)
			
		embed.add_field(name="敵人三",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['skills']}",inline=True)
			
		embed.add_field(name="敵人四",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['skills']}",inline=True)
			
		embed.add_field(name="敵人五",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['skills']}",inline=True)
		
		embed.add_field(name="==========================================================",value=" ",inline=False)
		
		embed.add_field(name=f"{interaction.user.name}",value=f"生命值：{round(db[f'{interaction.user.id}'][1]['status']['HP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxHP'])}\n魔力值：{round(db[f'{interaction.user.id}'][1]['status']['MP'])} / {round(db[f'{interaction.user.id}'][1]['status']['maxMP'])}\n當前地圖：{maps_data[f'{mapID}']['name']}",inline=False)

		embed.add_field(name="==========================================================",value=" ",inline=False)
		embed.add_field(name="狀態訊息",value=StatusText,inline=False)


		await interaction.edit_original_response(embed=embed,view=view)


	async def sell_item(self,interaction):
		await interaction.response.defer()

		view = View(timeout=None)
		
		sell_name = interaction.data['custom_id']
		StatusText = ""
			
		for i in range(len(items_data)):
			if items_data[f'{i}']['name'] == sell_name:
				money = items_data[f'{i}']['sell']
				db[f'{interaction.user.id}'][0]['money'] += money
				db[f'{interaction.user.id}'][1]['items'][f'{sell_name}'] -= 1
				StatusText = f"你出售了 {sell_name}，獲得了 {money} 塊錢"
					
					
		
		embed = discord.Embed(title="聖魂傳奇-出售物品",description=f"剩餘金錢：{db[f'{interaction.user.id}'][0]['money']}")
		
		for i in range(0,len(items_data)):
			item_name = items_data[f'{i}']['name']
			describe = items_data[f'{i}']['describe']
			money = items_data[f'{i}']['sell']
			try:
				if db[f'{interaction.user.id}'][1]['items'][f'{item_name}'] >= 1:
					item = Button(label=f"{item_name}",style=discord.ButtonStyle.primary,custom_id=f"{item_name}")
					item.callback = self.sell_item
					view.add_item(item)
					embed.add_field(name=f"{item_name}\n{describe}\n剩餘數量：{db[f'{interaction.user.id}'][1]['items'][f'{item_name}']}\n出售價格：{money}",value=" ")
			except:
				pass

		back = Button(label="取消",style=discord.ButtonStyle.secondary)
		back.callback = self.start_adventure
		view.add_item(back)
		
		await interaction.edit_original_response(embed=embed,view=view)

	

	async def purchase(self,interaction):
		await interaction.response.defer()

		view = View(timeout=None)

		purchase_name = interaction.data['custom_id']
		StatusText = ""
		
		for i in range(len(items_data)):
			if items_data[f'{i}']['name'] == purchase_name:
				money = items_data[f'{i}']['buy']
				if db[f'{interaction.user.id}'][0]['money'] >= money:
					if purchase_name not in db[f'{interaction.user.id}'][1]['items']:
						db[f'{interaction.user.id}'][1]['items'][purchase_name] = 1
						db[f'{interaction.user.id}'][0]['money'] -= money
					else:
						db[f'{interaction.user.id}'][1]['items'][purchase_name] += 1
						db[f'{interaction.user.id}'][0]['money'] -= money
						
					StatusText = f"你花費了 {money}，購買了 {purchase_name}"

				else:
					StatusText = "你的錢不夠喔"

		embed = discord.Embed(title="聖魂傳奇-購買物品",description=f"剩餘金錢：{db[f'{interaction.user.id}'][0]['money']}")
			
		for i in range(len(items_data)):
			item_name = items_data[f'{i}']['name']
			describe = items_data[f'{i}']['describe']
			try:
				item_price = items_data[f'{i}']['buy']
				item = Button(label=item_name,style=discord.ButtonStyle.primary,custom_id=item_name)
				item.callback = self.purchase
				view.add_item(item)
				embed.add_field(name=f"{item_name}\n{describe}",value=f"價格：{item_price}",inline=True)
			except:
				pass

		embed.add_field(name="==========================================================",value="",inline=False)
		embed.add_field(name="狀態訊息",value=StatusText,inline=False)

		cancel = Button(label="取消",style=discord.ButtonStyle.secondary,custom_id="cancel")
		cancel.callback = self.start_adventure
		view.add_item(cancel)
		
		await interaction.edit_original_response(embed=embed,view=view)

	

	async def NPC_function(self,interaction:discord.Interaction):
		await interaction.response.defer()

		view = View(timeout=None)

		embed = discord.Embed(title="聖魂傳奇",description=f"剩餘金錢：{db[f'{interaction.user.id}'][0]['money']}")

		StatusText = ""

		if interaction.data['custom_id'] == "復活點":
			if db[f'{interaction.user.id}'][1]['status']['HP'] <= 0:
				if db[f'{interaction.user.id}'][0]['money'] >= 1000:
					db[f'{interaction.user.id}'][0]['money'] -= 1000
					db[f'{interaction.user.id}'][1]['status']['HP'] = db[f'{interaction.user.id}'][1]['status']['maxHP']
					db[f'{interaction.user.id}'][1]['status']['MP'] = db[f'{interaction.user.id}'][1]['status']['maxMP']
					StatusText = "你花費了1000塊錢復活了"
				else:
					StatusText = "你的錢不夠喔!"
			else:
				StatusText = "你目前不需要復活"

		if interaction.data['custom_id'] == "道具商人":
			buy_function = Button(label="購買物品",style=discord.ButtonStyle.primary,custom_id="buy")
			sell_function = Button(label="出售物品",style=discord.ButtonStyle.primary,custom_id="sell")

			buy_function.callback = self.purchase
			sell_function.callback = self.sell_item
			
			view.add_item(buy_function)
			view.add_item(sell_function)
		embed.add_field(name="==========================================================",value="",inline=False)
		embed.add_field(name="狀態訊息",value=StatusText,inline=False)
				

		cancel = Button(label="取消",style=discord.ButtonStyle.secondary,custom_id="cancel")
		cancel.callback = self.start_adventure
		view.add_item(cancel)
		
		await interaction.edit_original_response(embed=embed,view=view)
			

	async def start_adventure(self,interaction:discord.Interaction):
		await interaction.response.defer()

		view = View(timeout=None)
		
		change = Button(label="切換地圖",style=discord.ButtonStyle.success,custom_id="change",row=2)
		data = Button(label="資料介面",style=discord.ButtonStyle.secondary,custom_id="data",row=2)

		view.add_item(change)
		view.add_item(data)

		change.callback = self.change_map
		data.callback = self.data_page

		mapID = db[f'{interaction.user.id}'][1]['enemies']['mapID']
		
		embed = discord.Embed(title="聖魂傳奇",description=" ")

		if interaction.data['custom_id'] == "run":
			for i in range(1,6):
				db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['name'] = "無"
				db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['HP'] = 0
				db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['MP'] = 0
				db[f'{interaction.user.id}'][1]['enemies'][f'enemy{i}']['skills'] = []
				
		if db[f'{interaction.user.id}'][1]['enemies']['mapID'] in ["0","6"]:
			for i in range(len(maps_data[f'{mapID}']['NPCs'])):
				name = maps_data[f'{mapID}']['NPCs'][f'{i}']['name']
				type = maps_data[f'{mapID}']['NPCs'][f'{i}']['type']
				if type == "任務":
					embed.add_field(name=f"{name}",value="可接取任務!",inline=True)
				elif type == "商人":
					embed.add_field(name=f"{name}",value="可購買物品!",inline=True)
				NPC = Button(label=f"{name}",style=discord.ButtonStyle.primary,custom_id=f"{type}")
				NPC.callback = self.NPC_function
				view.add_item(NPC)

		else:
				search = Button(label="探索四周",style=discord.ButtonStyle.primary,custom_id="search")
				view.add_item(search)
				search.callback = self.search_field
			
				embed.add_field(name="敵人一",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy1']['skills']}",inline=True)
				
				embed.add_field(name="敵人二",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy2']['skills']}",inline=True)
				
				embed.add_field(name="敵人三",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy3']['skills']}",inline=True)
				
				embed.add_field(name="敵人四",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy4']['skills']}",inline=True)
				
				embed.add_field(name="敵人五",value=f"名字：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['name']}\n生命值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['HP']}\n魔力值：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['MP']}\n技能：{db[f'{interaction.user.id}'][1]['enemies']['enemy5']['skills']}",inline=True)
				
		
		embed.add_field(name=f"{interaction.user.name}",value=f"生命值：{db[f'{interaction.user.id}'][1]['status']['HP']} / {db[f'{interaction.user.id}'][1]['status']['maxHP']}\n魔力值：{db[f'{interaction.user.id}'][1]['status']['MP']} / {db[f'{interaction.user.id}'][1]['status']['maxMP']}\n當前地圖：{maps_data[f'{mapID}']['name']}",inline=False)

		embed.add_field(name="==========================================================",value=" ",inline=False)
		embed.add_field(name="狀態訊息",value=" ",inline=False)
		
		await interaction.edit_original_response(embed=embed,view=view)

		
	
	async def _hl(self,interaction,user:discord.User):
		embed = discord.Embed(title="聖魂傳奇",description=" ")
		embed.add_field(name="開始遊戲",value="開啟傳奇的冒險!",inline=False)
		embed.add_field(name="資料介面",value="設定自己的資料!",inline=False)
		embed.add_field(name="遊戲介紹",value="遊戲的各種介紹!",inline=False)

		view = View(timeout=None)
		start = Button(label="開始遊戲",style=discord.ButtonStyle.primary,custom_id="start")
		data = Button(label="資料介面",style=discord.ButtonStyle.primary,custom_id="data")
		intro = Button(label="遊戲介紹",style=discord.ButtonStyle.primary,custom_id="intro")
		
		view.add_item(start)
		view.add_item(data)
		view.add_item(intro)

		start.callback = self.start_adventure
		intro.callback = self.intro_page
		data.callback = self.data_page

		await interaction.response.send_message(embed=embed,view=view)

async def setup(bot):
	await bot.add_cog(hl(bot))