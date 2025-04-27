import discord
import importlib
import random
import dbFunction

from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, TextInput, Modal

def register():
	hl_maxHP = random.randint(200,500)
	hl_maxMP = random.randint(50,150)

	data = {
			'money': 5000, 
			'daily': 0, 
			'reset': 0, 
			'bank':0,
			'status':{	
				'level':1,
				'class':'無',
				'HP':hl_maxHP,
				'maxHP':hl_maxHP,
				'MP':hl_maxMP,
				'maxMP':hl_maxMP,
				'SP':hl_maxHP * 3,
				'maxSP':hl_maxHP * 3,
				'STR':random.randint(0,5),
				'DEX':random.randint(0,5),
				'CON':random.randint(0,5),
				'INT':random.randint(0,5),
				'action':0,
				'maxAction':0,
				'EXP':0,
				'baseEXP':150,
				'ATTpoints':0,
				'skillpoints':0
		},
		'weapons':{},
		'items':{},
		'armour':{},
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
			'MQID':0,
			'SQlist':[],
			'DQlist':[]
		},
		"PVPchance":5,
		'mapID':"0",
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
						'enemy5':{	
							'name':'無',	
							'HP':0,	
							'MP':0,
							'ATK':0,
							'DEF':0,
							'SPD':0,
							'skills':[]
						}
					}
				}
	
	return data

def reload_db():
	importlib.reload(dbFunction)



class WalletFunction:
	class EconomyInfo:
		def __init__(self, user, data):
			money = int(data['money'])
			bank = float(data['bank'])

			self.embed = discord.Embed(title="經濟系統",description=user,color=0x3d993a)
			self.embed.add_field(name="**目前餘額**", value=money, inline=False)
			self.embed.add_field(name="**銀行存款**", value=bank, inline=False)
			
			try:
				self.embed.set_thumbnail(url=user.avatar.url)
			except:
				self.embed.set_thumbnail(url=user.default_avatar.url)

		def to_dict(self):
			return self.embed.to_dict()
		
	class BankFunction(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(
			label = "存入(save)",
			style = discord.ButtonStyle.primary
			)
		async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
			modal = WalletFunction.SaveInput()
			await interaction.response.send_modal(modal)

		@discord.ui.button(
			label = "取出(claim)",
			style = discord.ButtonStyle.primary
			)
		async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
			modal = WalletFunction.ClaimInput()
			await interaction.response.send_modal(modal)

	class SaveInput(Modal, title="請輸入要存入的金額"):
		money = TextInput(label="請輸入金額", placeholder="請輸入要存入的金額", style=discord.TextStyle.short, required=True)

		async def on_submit(self, interaction: discord.Interaction):
			await interaction.response.defer()

			try:
				money = int(self.money.value)
			except:
				await interaction.edit_original_response(content="你輸入的不是數字")
				return

			reload_db()
			ID = interaction.user.id
			data = dbFunction.get_economy(ID)

			if data["money"] < money:
				await interaction.edit_original_response(content="你沒有這麼多錢可以存入")
				return

			dbFunction.save_bank(ID, money)
			data = dbFunction.get_economy(ID)
			embed = WalletFunction.EconomyInfo(interaction.user, data)
			view = WalletFunction.BankFunction()
			await interaction.edit_original_response(embed=embed, view=view) # pyright: ignore[reportArgumentType]
			return
		
	class ClaimInput(Modal, title="請輸入要取出的金額"):
		money = TextInput(label="請輸入金額", placeholder="請輸入要取出的金額", style=discord.TextStyle.short, required=True)

		async def on_submit(self, interaction: discord.Interaction):
			await interaction.response.defer()

			try:
				money = int(self.money.value)
			except:
				await interaction.edit_original_response(content="你輸入的不是數字")
				return

			reload_db()
			ID = interaction.user.id
			data = dbFunction.get_economy(ID)

			if data["bank"] < money:
				await interaction.edit_original_response(content="你沒有這麼多錢可以取出")
				return

			dbFunction.claim_bank(ID, money)
			data = dbFunction.get_economy(ID)
			embed = WalletFunction.EconomyInfo(interaction.user, data)
			view = WalletFunction.BankFunction()
			await interaction.edit_original_response(embed=embed, view=view) # pyright: ignore[reportArgumentType]
			return

class Economy(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		self.錢包 = app_commands.ContextMenu(name="錢包",callback=self.wallet)
		self.bot.tree.add_command(self.錢包)

	async def wallet(self, interaction:discord.Interaction, user:discord.User):
		reload_db()
		if user == None:
			ID = interaction.user.id
				
		else:
			ID = user.id

		user = self.bot.get_user(ID)
		data = dbFunction.get_economy(ID)

		if not data:
			await interaction.response.send_message(f"{user.name} 尚未註冊!")
			return
		
		embed = WalletFunction.EconomyInfo(user, data)
		view = WalletFunction.BankFunction()
		await interaction.response.send_message(embed=embed, view=view) # pyright: ignore[reportArgumentType]
			
			
	@app_commands.command(name="money",description="查詢錢包")
	async def _wallet(self, interaction:discord.Interaction, 用戶:discord.User=None):
		reload_db()
		user = 用戶
		if user == None:
			ID = interaction.user.id
				
		else:
			ID = user.id

		user = self.bot.get_user(ID)
		data = dbFunction.get_economy(ID)

		if not data:
			await interaction.response.send_message(f"{user.name} 尚未註冊!")
			return
		
		embed = WalletFunction.EconomyInfo(user, data)
		view = WalletFunction.BankFunction()
		await interaction.response.send_message(embed=embed, view=view) # pyright: ignore[reportArgumentType]
		

	
	@app_commands.command(description="註冊用戶") 
	async def register(self,interaction):
		reload_db()

		data = register()
		user_data = dbFunction.get_economy(interaction.user.id)

		if user_data:
			await interaction.response.send_message("你已經註冊過了")
			return
		
		dbFunction.register(interaction.user, data)


	@app_commands.command(description="領取每日獎勵")
	async def daily(self, interaction):
		reload_db()
		ID = interaction.user.id
		data = dbFunction.get_economy(ID)

		if not data: 
			await interaction.response.send_message("你還沒註冊過，請打/register")
			return
		
		if int(data["daily"]) == 1:
			await interaction.response.send_message("你今天已經領過了!請明天再來")
			return

		dbFunction.claim_daily(ID)
		await interaction.response.send_message("簽到成功!你已領取100$")

	@app_commands.command(description="贈送禮物")	
	async def gift(self,interaction, 用戶: discord.User, 金額:int):
		reload_db()
		Sdata = dbFunction.get_economy(interaction.user.id)
		Odata = dbFunction.get_economy(用戶.id)

		if not Sdata:
			await interaction.response.send_message("你尚未註冊!")
			return

		if not Odata:
			await interaction.response.send_message(f"{用戶.mention} 尚未註冊")
			return
		
		if 金額 < 0:
			await interaction.response.send_message("你不可以給別人低於 0 元")
			return
		if 金額 > Sdata["money"]:
			await interaction.response.send_message("你沒有這麼多錢喔")
			return
		
		dbFunction.gift(interaction.user.id, 用戶.id, 金額)
		await interaction.response.send_message(f"你給 {用戶.mention} {金額} 塊錢")
		await 用戶.send(f"{interaction.user.mention} 給了你 {金額} 塊錢")


	
async def setup(bot):
	await bot.add_cog(Economy(bot))