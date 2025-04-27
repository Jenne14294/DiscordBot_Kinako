import discord
import json
import random
import asyncio
import dbFunction

from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from cmds.economy import reload_db

dpath = "./jsonfile/data.json"

class GTN:
	data = {
		"easy": (random.randint(0, 200), 200, 40, 1),
		"normal": (random.randint(0, 500), 500, 20, 10),
		"hard": (random.randint(0, 1000), 1000, 15, 75),
		"EX": (random.randint(0, 2000), 2000, 10, 200)
	}

	class GTNInfo:
		def __init__(self, data):
			self.embed = discord.Embed(title="終極密碼", description=data['name'], color=0x3d993a)
			self.embed.add_field(name="**數字範圍**", value=f"{data['GuessBottom']} ~ {data['GuessTop']}", inline=False)
			self.embed.add_field(name="**剩餘機會**", value=data["chance"], inline=False)

		def to_dict(self):
			return self.embed.to_dict()

	class GTNButton(View):
		def __init__(self, bot):
			super().__init__(timeout=None)
			self.bot = bot  # 儲存 bot
			self.result = asyncio.get_event_loop().create_future()

			async def button_callback(interaction):
				await interaction.response.defer()
				# 禁用所有按鈕
				for item in self.children:
					if isinstance(item, Button):
						item.disabled = True

				# 更新訊息畫面
				dbFunction.GTN_set(interaction.user.id, GTN.data[interaction.data['custom_id']])

				new_data = dbFunction.GTN_get(interaction.user.id)
				embed = GTN.GTNInfo(new_data)
				await interaction.message.edit(content=None, embed=embed, view=self)

				await self.start_game(interaction, new_data)

			easy = Button(label="簡單", style=discord.ButtonStyle.primary, custom_id="easy")
			normal = Button(label="普通", style=discord.ButtonStyle.success, custom_id="normal")
			hard = Button(label="困難", style=discord.ButtonStyle.danger, custom_id="hard")
			EX = Button(label="極限", style=discord.ButtonStyle.secondary, custom_id="EX")

			easy.callback = button_callback
			normal.callback = button_callback
			hard.callback = button_callback
			EX.callback = button_callback

			self.add_item(easy)
			self.add_item(normal)
			self.add_item(hard)
			self.add_item(EX)

		async def start_game(self, interaction, game_data):
			# 遊戲邏輯開始
			player = interaction.user
			number = game_data['GuessNumber']
			chance = game_data['chance']  # 假設你存的是 'chance' 在 game_data 中

			while chance > 0:
				response = await self.bot.wait_for("message")

				if response.author.bot:
					continue

				try:
					guess = int(response.content)
					await response.delete()
				except Exception as e:
					await interaction.edit_original_response(content=f"{player.mention}\n輸入錯誤!請重新輸入/gtn來遊玩", embed=None, view=None)
					return

				if guess == number:
					winner = player.id
					data = dbFunction.GTN_get(winner)
					money = data["multiply"] * (data["chance"] + 1)
					newmoney = dbFunction.get_economy(winner)['money'] + money
					dbFunction.GTN_gain(winner, money)
					await interaction.edit_original_response(content=f"回答正確，答案是 {number}\n你獲得 {money} 塊錢\n目前你擁有 {newmoney} 塊錢", view=None, embed=None)
					return

				elif guess > number:
					dbFunction.GTN_greater(player.id, guess)
					new_data = dbFunction.GTN_get(player.id)
					embed = GTN.GTNInfo(new_data)
					await interaction.edit_original_response(embed=embed)

				else:
					dbFunction.GTN_less(player.id, guess)
					new_data = dbFunction.GTN_get(player.id)
					embed = GTN.GTNInfo(new_data)
					await interaction.edit_original_response(embed=embed)

			await interaction.edit_original_response(content=f"{player.mention}\n遊戲結束!本局數字為 {number},請再次輸入`/gtn`來遊玩", view=None, embed=None)

class TTT:
	win_combinations = [
    (7, 8, 9),  # 第一行
    (4, 5, 6),  # 第二行
    (1, 2, 3),  # 第三行
    (1, 4, 7),  # 第一列
    (2, 5, 8),  # 第二列
    (3, 6, 9),  # 第三列
    (1, 5, 9),  # 主要對角線
    (3, 5, 7)   # 次要對角線
]

	# 檢查是否有獲勝
	def check_winner(self, slot):
		for combination in TTT.win_combinations:
			if slot[f"slot_{combination[0]}"] == slot[f"slot_{combination[1]}"] == slot[f"slot_{combination[2]}"] != "⬛":
				return slot[f"slot_{combination[0]}"]  # 返回贏的符號（"O" 或 "X"）
		return None  # 沒有獲勝
	

	class TTTInfo:
		def __init__(self, slot):
			# 初始化Embed物件
			self.embed = discord.Embed(title="井字遊戲", description="", color=0x3d993a)
			
			# 動態設置每個格子的內容
			self.embed.add_field(name=f"{slot['slot_7']} | {slot['slot_8']} | {slot['slot_9']}", value="", inline=False)
			self.embed.add_field(name=f"{slot['slot_4']} | {slot['slot_5']} | {slot['slot_6']}", value="", inline=False)
			self.embed.add_field(name=f"{slot['slot_1']} | {slot['slot_2']} | {slot['slot_3']}", value="", inline=False)

		def to_dict(self):
			return self.embed.to_dict()
		
	class TTTButton(View):
		def __init__(self):
			super().__init__(timeout=None)

			async def choose_position(interaction):
				await interaction.response.defer()
				num_p = int(interaction.data["custom_id"])
				slot = dbFunction.TTT_getslot(interaction.user.id)
				round = dbFunction.TTT_getRound(interaction.user.id)['Round']
					
				# 檢查該位置是否已被佔用
				if slot[f"slot_{num_p}"] == "⬛":
					# 玩家選擇位置並標記為"O"
					slot[f"slot_{num_p}"] = "⭕"

					empty_slots = [i for i in range(1, 10) if slot[f"slot_{i}"] == "⬛"]
					if empty_slots:
						num_c = random.choice(empty_slots)
						slot[f"slot_{num_c}"] = "❌"

					dbFunction.TTT_select(interaction.user.id, num_p, num_c)
					slot = dbFunction.TTT_getslot(interaction.user.id)
					round = dbFunction.TTT_getRound(interaction.user.id)['Round']
					# 更新遊戲畫面
					await update_game_board(interaction)

					# 主遊戲邏輯：檢查是否有贏家
					winner = TTT.check_winner(self, slot)
					if winner == "⭕":
						# 玩家獲勝
						winner = interaction.user.id
						dbFunction.TTT_gain(winner)
						await interaction.edit_original_response(content="你贏了T_T，100 塊錢就給你吧！哼", view = None)
						return

					elif winner == "❌":
						# 電腦獲勝
						await interaction.edit_original_response(content="你輸了 AwA，50 塊錢歸我啦～～", view = None)
						return

					# 如果回合已結束並且沒有人贏
					elif round == 0:
						await interaction.edit_original_response(content="0.0，竟然平手了呢～～", view = None)
						return
						
			async def update_game_board(interaction):
				# 創建TTTInfo物件，並根據目前的遊戲板更新視覺內容
				slot = dbFunction.TTT_getslot(interaction.user.id)
				embed = TTT.TTTInfo(slot)
				
				# 更新井字遊戲畫面
				await interaction.edit_original_response(embed=embed)


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

			self.add_item(leftup)
			self.add_item(leftmid)
			self.add_item(leftdown)
			self.add_item(midup)
			self.add_item(middle)
			self.add_item(middown)
			self.add_item(rightup)
			self.add_item(rightmid)
			self.add_item(rightdown)
		
class Slot:
	def check_result(self, slot, input_money):
		# 定義獎勵倍率
		MULTIPLIERS = {
			":black_joker:": (20, 18),   # 最少出現，倍率最高
			":peach:": (7, 6),            # 較少出現，倍率較高
			":cherries:": (7, 6),         # 較少出現，倍率較高
			":melon:": (6, 5.5),          # 中等偏高
			":strawberry:": (4, 3.5),     # 中等
			":banana:": (4, 3.5),         # 中等
			":grapes:": (3, 2.5),         # 中等偏低
			":tangerine:": (3, 2.5),      # 中等偏低
			":lemon:": (2, 2),            # 稍微高
			":apple:": (1, 1),            # 最常出現，倍率最低
		}

		# 取中間三格
		mid_row = slot[3:6]

		# 檢查中間三格中哪種圖案最多
		for symbol, (full_match, partial_match) in MULTIPLIERS.items():
			if mid_row.count(symbol) == 3:
				input_money *= full_match
				break
			elif mid_row.count(symbol) == 2:
				input_money = round(input_money * partial_match)
				break
		else:
			input_money = 0  # 沒有符合條件，輸掉

		return input_money

	class SlotInfo:
		def __init__(self, slot, input_money, result, now_money):
			# 初始化Embed物件
			self.embed = discord.Embed(title="吃角子老虎機", description="", color=0x3d993a)
			
			# 動態設置每個格子的內容
			self.embed.add_field(name=f"投入金額：{input_money}\n獲得獎金：{result}\n當前擁有：{now_money}", value="", inline=False)
			self.embed.add_field(name=f"{slot[0]} | {slot[1]} | {slot[2]}", value="", inline=False)
			self.embed.add_field(name=f"{slot[3]} | {slot[4]} | {slot[5]} <<<<", value="", inline=False)
			self.embed.add_field(name=f"{slot[6]} | {slot[7]} | {slot[8]}", value="", inline=False)

		def to_dict(self):
			return self.embed.to_dict()
		
	async def start_game(self, interaction, input_money):
		await interaction.response.defer()
		slot = []

		with open(dpath,"r",encoding="utf8") as dfile:
			ddata = json.load(dfile)

		money = dbFunction.get_economy(interaction.user.id)["money"]
		weights = ddata["slot_weight"]

		if input_money <= 0:
			await interaction.edit_original_response(content="請投入金額(至少1塊錢)")
			return
		
		if money < input_money:
			await interaction.edit_original_response(content="你沒有這麼多錢唷～")
			return
		

		for i in range(1, 6):
			slot.clear()
			for j in range(1, 10):
				item = random.choices(ddata["slot"], weights=weights, k=1)[0]
				slot.append(item)

			embed = Slot.SlotInfo(slot, input_money, 0, money)

			await interaction.edit_original_response(embed=embed)
			await asyncio.sleep(0.5)

		result = Slot.check_result(self, slot, input_money)
		gained_money = result - input_money
		dbFunction.Slot_gain(interaction.user.id, gained_money)

		now_money = dbFunction.get_economy(interaction.user.id)["money"]
		embed = Slot.SlotInfo(slot, input_money, result, now_money)
		await interaction.edit_original_response(embed=embed)

class PP:
	class PPInfo:
		def __init__(self, slot, result):
			# 初始化Embed物件
			result = str(result)
			results = []
			for i in range(1, 4):
				if slot[f'select_{i}'] == -1:
					results.append("無")
				else:
					select_value = slot[f'select_{i}']
					results.append(slot[f'hole_{select_value}'])
				
			self.embed = discord.Embed(title="洞洞樂", description="", color=0x3d993a)
			self.embed.add_field(name=f"玩家：{slot['name']}\n投入金額：{slot['input_money']}\n獎賞：{results[0]}、{results[1]}、{results[2]}\n結果：{result}", value="", inline=False)

			# 動態設置每個格子的內容
			for i in range(1, 26, 5):
				holes = ""
				# 判斷每個格子是否被選擇
				for j in range(i, i + 5):
					if slot["chance"] == 0:
						holes += f"【{slot[f'hole_{j}']}】"  # 格子被選擇，顯示其內容
					else:
						holes += "【⬛】"  # 格子未被選擇，顯示黑方塊

				holes += "\n"
				self.embed.add_field(name=holes, value="", inline=False)


		def to_dict(self):
			return self.embed.to_dict()
		
	class PPButton(View):
		def __init__(self):
			super().__init__(timeout=None)

			async def choose_hole(interaction):
				await interaction.response.defer()	
				chance = dbFunction.PP_getslot(interaction.user.id)["chance"]
				dbFunction.PP_select(interaction.user.id, interaction.data["custom_id"], 3 - chance + 1)
				slot = dbFunction.PP_getslot(interaction.user.id)
				if slot["chance"] > 0:
					embed = PP.PPInfo(slot, 0)

					button = next(item for item in self.children if item.custom_id == str(interaction.data['custom_id']))
					button.disabled = True  # 禁用按鈕

					await interaction.edit_original_response(embed=embed, view=self)  # 更新視圖，這樣禁用的按鈕才會生效

				else:
					input_money = slot["input_money"]
					selection_1, selection_2, selection_3 = slot['select_1'], slot['select_2'], slot['select_3']
					selections = [str(slot[f"hole_{selection_1}"]), str(slot[f"hole_{selection_2}"]), str(slot[f"hole_{selection_3}"])]
					result = input_money
					for selection in selections:
						op, value = selection[:1], selection[1:]

						if selection == "| |":
							result = abs(result)
							continue

						if not value.isdigit():
							continue  # 防呆，跳過無效指令

						num = int(value)

						match op:
							case "+":
								result += num
							case "-":
								result -= num
							case "×":
								result *= num
							case "÷":
								if num != 0:
									result //= num
							case "^":
								result = round(pow(result, num))
							case "√":
								if result >= 0 or num % 2 == 1:
									result = round(pow(result, 1 / num))

					embed = PP.PPInfo(slot, result)
					dbFunction.PP_gain(interaction.user.id, result)

					await interaction.edit_original_response(embed=embed, view=None)


			for i in range(1,26):
				hole = Button(label=f"[{i}]", custom_id=str(i), style=discord.ButtonStyle.primary)
				self.add_item(hole)
				hole.callback = choose_hole


class Main(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
	

	@app_commands.command(description="骰一顆骰子")
	async def dice(self, interaction):
		dice = random.randint(1, 6)
		await interaction.response.send_message(f"你骰出了 {dice} 點")


	@app_commands.command(description="遊玩猜數字")
	async def gtn(self, interaction):
		reload_db()
		view = GTN.GTNButton(self.bot) 
		await interaction.response.send_message(f"選擇難度後輸入數字", view=view)

	@app_commands.command(description="遊玩井字遊戲")
	async def ttt(self, interaction):
		reload_db()
		dbFunction.TTT_init(interaction.user.id)
		data = dbFunction.TTT_getslot(interaction.user.id)
		
		embed = TTT.TTTInfo(data)
		view = TTT.TTTButton()

		await interaction.response.send_message(content="你花費了 50 塊錢來遊玩井字遊戲", embed=embed, view=view)


	@app_commands.command(description="遊玩吃角子老虎機")
	async def slot(self, interaction, 金錢:int):
		reload_db()
		await Slot.start_game(self, interaction, 金錢) # pyright: ignore[reportArgumentType]


	@app_commands.command(description="遊玩洞洞樂")
	async def pp(self, interaction:discord.Interaction, 金錢:int):
		reload_db()
		with open(dpath,"r",encoding="utf8") as dfile:
			ddata = json.load(dfile)

		money = dbFunction.get_economy(interaction.user.id)["money"]

		if 金錢 <= 0:
			await interaction.response.send_message("至少要投入 1 塊錢")
			return
		
		if 金錢 > money:
			await interaction.response.send_message("你沒有這麼多錢唷～")
			return 
		
		pp_slots = random.choices(ddata["pp_slots"], k=25)
		dbFunction.PP_start(interaction.user.id, 金錢)
		dbFunction.PP_init(interaction.user.id, 金錢, pp_slots)
		slot = dbFunction.PP_getslot(interaction.user.id)
		embed = PP.PPInfo(slot, 0)
		view= PP.PPButton()

		await interaction.response.send_message(embed=embed, view=view)
		
		

async def setup(bot):
	await bot.add_cog(Main(bot))