import discord
import json
import random
import asyncio
import dbFunction

from discord.ext import commands
from discord.ui import Button,View
from discord import app_commands


dpath = "./jsonfile/data.json"	

class Main(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
	

	@app_commands.command(description="骰一顆骰子")
	async def dice(self,ctx):
		dice = random.randint(1, 6)
		await ctx.response.send_message(f"你骰出了 {dice} 點")


	@app_commands.command(description="遊玩猜數字")
	async def gtn(self,ctx):
		easy = Button(label="簡單",style=discord.ButtonStyle.primary,custom_id="easy")
		normal = Button(label="普通",style=discord.ButtonStyle.success,custom_id="normal")
		hard = Button(label="困難",style=discord.ButtonStyle.danger,custom_id="hard")
		EX = Button(label="極限",style=discord.ButtonStyle.secondary,custom_id="EX")
		
		async def button_callback(interaction):
			await interaction.response.defer()
			if interaction.data["custom_id"] ==	"easy":
				number = random.randint(0, 200)
				chance = 40
				multiply = 1			
	
			elif interaction.data["custom_id"] == "normal":
				number = random.randint(0, 500)
				chance = 20
				multiply = 10
	
			elif interaction.data["custom_id"] == "hard":
				number = random.randint(0, 1000)
				chance = 15
				multiply = 75
	
			elif interaction.data["custom_id"] == "EX":
				number = random.randint(0, 2000)
				chance = 10
				multiply = 200

			easy.disabled = True
			normal.disabled = True
			hard.disabled = True
			EX.disabled = True
			await ctx.edit_original_response(content="請輸入數字",view=view)
			
			
			player = interaction.user
			while chance > 0:
				response = await self.bot.wait_for("message")
	
				if response.author.bot:
					continue
	
				if player == response.author:
					try:
						guess = int(response.content)
						await response.delete()
					except:
						await ctx.response_send_message(f"{player.mention}\n輸入錯誤!請重新輸入/gtn來遊玩")
						return
	
					chance = chance - 1
					
	
					if guess == number:
						winner = ctx.user.id
						money = multiply * (chance+1)
						newmoney = dbFunction.get_economy(winner) + money
						dbFunction.GTN_gain(winner, money)
						await ctx.edit_original_response(content=f"回答正確，答案是 {number}\n你獲得 {money} 塊錢\n目前你擁有 {newmoney} 塊錢")
						return
	
					elif guess > number:
						await ctx.edit_original_response(content=f"{player.mention}\n請輸入一個數字\n再小一點\n你選擇了 {guess} \n還剩下 {chance} 次機會")
					else:
						await ctx.edit_original_response(content=f"{player.mention}\n請輸入一個數字\n再大一點\n你選擇了 {guess} \n還剩下 {chance} 次機會")
						
			await ctx.edit_original_response(content=f"{player.mention}\n遊戲結束!本局數字為 {number},請再次輸入`/gtn`來遊玩")

		easy.callback = button_callback
		normal.callback = button_callback
		hard.callback = button_callback
		EX.callback = button_callback
		view = View(timeout=False)
		view.add_item(easy)
		view.add_item(normal)
		view.add_item(hard)
		view.add_item(EX)
		await ctx.response.send_message(f"選擇難度後輸入數字",view=view)


	@app_commands.command(description="遊玩井字遊戲")
	async def ttt(self,ctx):
		player = ctx.user
		newmoney = db[f"{player.id}"][0]["money"] - 50
		db[f"{player.id}"][0]["money"] = newmoney
		slot = ["	 "] * 9
		db[f'{player.id}'][0]['TTTround'] = 4
		
		async def choose_position(interaction):
			if interaction.user == player:
					await interaction.response.defer()
					slot_p = int(interaction.data["custom_id"])
					num_p = int(slot_p - 1)
					if slot[num_p] == "	 ":
						slot[num_p] = "O"
						num_c = random.randint(0, 8)
						while slot[num_c] in ["X","O"]:
							num_c = random.randint(0, 8)
						slot[num_c] = "X"
						await ctx.edit_original_response(content=f"你花費50塊錢來和小幫手玩井字遊戲\n__{slot[6]}__|__{slot[7]}__|__{slot[8]}__\n__{slot[3]}__|__{slot[4]}__|__{slot[5]}__\n__{slot[0]}__|__{slot[0]}__|__{slot[2]}__")
						db[f'{interaction.user.id}'][0]['TTTround'] -= 1

					if slot[0] == slot[3] == slot[6] == "O" or slot[0] == slot[4] == slot[7] == "O" or slot[2] == slot[5] == slot[8] == "O" or slot[6] == slot[7] == slot[8] == "O" or slot[3] == slot[4] == slot[5] == "O" or slot[0] == slot[0] == slot[2] == "O" or slot[0] == slot[4] == slot[8] == "O" or slot[6] == slot[4] == slot[2] == "O":
						keylist = []
						keys = db.keys()
						for key in keys:
							keylist.append(key)
						winner = ctx.user.id
						newmoney = db[f"{winner}"][0]['money'] + 100
						db[f"{winner}"][0]['money'] = newmoney
						await ctx.edit_original_response(content=f"__{slot[6]}__|__{slot[7]}__|__{slot[8]}__\n__{slot[3]}__|__{slot[4]}__|__{slot[5]}__\n__{slot[0]}__|__{slot[0]}__|__{slot[2]}__\n{player.mention}\n你贏了T_T\n你獲得了100塊錢\n目前你擁有 {newmoney} 塊錢")
						return

					elif slot[0] == slot[3] == slot[6] == "X" or slot[0] == slot[4] == slot[7] == "X" or slot[2] == slot[5] == slot[8] == "X" or slot[6] == slot[7] == slot[8] == "X" or slot[3] == slot[4] == slot[5] == "X" or slot[0] == slot[0] == slot[2] == "X" or slot[0] == slot[4] == slot[8] == "X" or slot[6] == slot[4] == slot[2] == "X":
						await ctx.edit_original_response(content=f"__{slot[6]}__|__{slot[7]}__|__{slot[8]}__\n__{slot[3]}__|__{slot[4]}__|__{slot[5]}__\n__{slot[0]}__|__{slot[0]}__|__{slot[2]}__\n{player.mention}\n你輸了AwA")
						return

					elif db[f'{interaction.user.id}'][0]['TTTround'] <= 0:
						await ctx.edit_original_response(content=f"__{slot[6]}__|__{slot[7]}__|__{slot[8]}__\n__{slot[3]}__|__{slot[4]}__|__{slot[5]}__\n__{slot[0]}__|__{slot[0]}__|__{slot[2]}__\n平手了0.0")
						return
					
		leftup = Button(label="左上",style=discord.ButtonStyle.primary,custom_id="7",row=1)
		leftmid = Button(label="左中",style=discord.ButtonStyle.primary,custom_id="4",row=2)
		leftdown = Button(label="左下",style=discord.ButtonStyle.primary,custom_id="1",row=3)
		midup = Button(label="中上",style=discord.ButtonStyle.primary,custom_id="8",row=1)
		middle = Button(label="中間",style=discord.ButtonStyle.primary,custom_id="5",row=2)
		middown = Button(label="中下",style=discord.ButtonStyle.primary,custom_id="2",row=3)
		rightup = Button(label="右上",style=discord.ButtonStyle.primary,custom_id="9",row=1)
		rightmid = Button(label="中右",style=discord.ButtonStyle.primary,custom_id="6",row=2)
		rightdown = Button(label="右下",style=discord.ButtonStyle.primary,custom_id="3",row=3)
		leftup.callback = choose_position
		leftmid.callback = choose_position
		leftdown.callback = choose_position
		midup.callback = choose_position
		middle.callback = choose_position
		middown.callback = choose_position
		rightup.callback = choose_position
		rightmid.callback = choose_position
		rightdown.callback = choose_position


		view = View(timeout=False)


		view.add_item(leftup)
		view.add_item(leftmid)
		view.add_item(leftdown)
		view.add_item(midup)
		view.add_item(middle)
		view.add_item(middown)
		view.add_item(rightup)
		view.add_item(rightmid)
		view.add_item(rightdown)
		await ctx.response.send_message(f"你花費 50 塊錢來和小幫手玩井字遊戲\n__{slot[6]}__|__{slot[7]}__|__{slot[8]}__\n__{slot[3]}__|__{slot[4]}__|__{slot[5]}__\n__{slot[0]}__|__{slot[0]}__|__{slot[2]}__",view=view)


	@app_commands.command(description="遊玩吃角子老虎機")
	async def slot(self,ctx, 金錢:int):
		player = ctx.user.id
		
		with open(dpath,"r",encoding="utf8") as dfile:
			ddata = json.load(dfile)
		if 金錢 <= 0:
			await ctx.response.send_message("請投入金額(至少1塊錢)")
			return
		if int(db[f"{player}"][0]['money']) >= 金錢:
			db[f"{player}"][0]['money'] -= 金錢
			await ctx.response.send_message(f'你投入了 {金錢} 塊錢到吃角子老虎機')			
		else:
			await ctx.response.send_message("你的錢不夠喔~")
			return
		for i in range(1,6):
			slot = []
			for j in range(1,10):
				item = random.choice(ddata["slot"])
				slot.append(item)

			await ctx.edit_original_response(content=f"-----------------\n{slot[0]}|{slot[0]}|{slot[2]}\n\n{slot[3]}|{slot[4]}|{slot[5]}	<<<\n\n{slot[6]}|{slot[7]}|{slot[8]}")
			await asyncio.sleep(0.5)

		
		# 定義獎勵倍率
		MULTIPLIERS = {
			":black_joker:": (10, 8),
			":peach:": (5, 4.5),
			":cherries:": (5, 4.5),
			":strawberry:": (3, 2.25),
			":tangerine:": (3, 2.25),
			":apple:": (2, 1),
		}

		# 取中間三格
		mid_row = slot[3:6]

		# 檢查中間三格中哪種圖案最多
		for symbol, (full_match, partial_match) in MULTIPLIERS.items():
			if mid_row.count(symbol) == 3:
				金錢 *= full_match
				break
			elif mid_row.count(symbol) == 2:
				金錢 = round(金錢 * partial_match)
				break
		else:
			金錢 = 0  # 沒有符合條件，輸掉


		
		winner = ctx.user.id
		keylist = []
		keys = db.keys()
		for key in keys:
			keylist.append(key)
		newmoney = db[f"{winner}"][0]['money'] + 金錢
		db[f"{winner}"][0]['money'] = newmoney

		await ctx.edit_original_response(content=f"-----------------\n{slot[0]}|{slot[0]}|{slot[2]}\n\n{slot[3]}|{slot[4]}|{slot[5]}	<<<\n\n{slot[6]}|{slot[7]}|{slot[8]}\n-----------------\n你獲得了{金錢}塊錢\n目前你擁有 {newmoney} 塊錢")


	@app_commands.command(description="遊玩洞洞樂")
	async def pp(self,interaction:discord.Interaction,金錢:int):
		if 金錢 > 0:
			if db[f"{interaction.user.id}"][0]['money'] > 金錢:
				db[f"{interaction.user.id}"][0]['money'] -= 金錢
				global chance, first, second, third, number, money
				money = 金錢
				chance = -1
				holes = []
				first, second, third = "無", "無", "無"
				prizes = ["*3","*1","*0","-500","+300","+100","/2"]
		
				async def choose_hole(interaction):
					await interaction.response.defer()
					global chance, money
					chance += 1
					
					if chance == 0:
						global first
						first = holes[int(interaction.data["custom_id"])-1]
						number = interaction.data["custom_id"]

						if first.startswith("+"):
							money += int(first[1:])
						elif first.startswith("-"):
							money -= int(first[1:])
						elif first.startswith("/"):
							money //= int(first[1:])
						elif first.startswith("*"):
							money *= int(first[1:])

						await interaction.edit_original_response(content=f"```[01] [02] [03] [04] [05]\n[06] [07] [08] [09] [10]\n[11] [12] [13] [14] [15]\n[16] [17] [18] [19] [20]\n[21] [22] [23] [24] [25]\n你翻開了：{number}\n目前獲得:{first}、無、無\n目前累計：{money}```",view=view)
					if chance == 1:
						global second
						second = holes[int(interaction.data["custom_id"])-1]
						number = interaction.data["custom_id"]

						if second.startswith("+"):
							money += int(second[1:])
						elif second.startswith("-"):
							money -= int(second[1:])
						elif second.startswith("/"):
							money //= int(second[1:])
						elif second.startswith("*"):
							money *= int(second[1:])

						await interaction.edit_original_response(content=f"```[01] [02] [03] [04] [05]\n[06] [07] [08] [09] [10]\n[11] [12] [13] [14] [15]\n[16] [17] [18] [19] [20]\n[21] [22] [23] [24] [25]\n你翻開了：{number}\n目前獲得:{first}、{second}、無\n目前累計：{money}```",view=view)
					if chance == 2:
						global third
						third = holes[int(interaction.data["custom_id"])-1]
						number = interaction.data["custom_id"]

						if third.startswith("+"):
							money += int(third[1:])
						elif third.startswith("-"):
							money -= int(third[1:])
						elif third.startswith("/"):
							money //= int(third[1:])
						elif third.startswith("*"):
							money *= int(third[1:])

						db[f"{interaction.user.id}"][0]['money'] += int(money)
						round(db[f"{interaction.user.id}"][0]['money'])
						
						
						await interaction.edit_original_response(content=f"```[01] [02] [03] [04] [05]\n[06] [07] [08] [09] [10]\n[11] [12] [13] [14] [15]\n[16] [17] [18] [19] [20]\n[21] [22] [23] [24] [25]\n你翻開了：{number}\n目前獲得:{first}、{second}、{third}\n你獲得了 {money} 塊錢\n現在你有 {db[f'{interaction.user.id}'][0]['money']} 塊錢```",view=None)
		
				view = View(timeout=False)
				for i in range(1,26):
					prize = random.choice(prizes)
					holes.append(prize)
					hole = Button(label=f"[{i}]",custom_id=str(i),style=discord.ButtonStyle.primary)
					view.add_item(hole)
					hole.callback = choose_hole
					
				await interaction.response.send_message(f"```[01] [02] [03] [04] [05]\n[06] [07] [08] [09] [10]\n[11] [12] [13] [14] [15]\n[16] [17] [18] [19] [20]\n[21] [22] [23] [24] [25]\n目前獲得:無、無、無```",view=view)
		else:
			await interaction.response.send_message("請至少投入1塊錢")
		

async def setup(bot):
	await bot.add_cog(Main(bot))