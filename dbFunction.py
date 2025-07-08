import json
import mysql.connector
from dotenv import load_dotenv
import os

# 載入 .env 檔案中的變數
load_dotenv()

try:
	conn = mysql.connector.connect(
		user = os.getenv("DB_USER"),
		password = os.getenv("DB_PASSWORD"),
		host = os.getenv("DB_HOST"),
		port = int(os.getenv("DB_PORT")),
		database = os.getenv("DB_NAME")
	)
	
	cursor = conn.cursor(dictionary=True)

except mysql.connector.Error as e:
	print("DB無法連線：", e)

def register(user, data):
	sql = "INSERT INTO `economy`(`Id`, `name`, `money`, `bank`, `daily`) VALUES (%s, %s, %s,%s, %s)"
	param = (user.id, user.name, data["money"], data["bank"], data["daily"], )
	cursor.execute(sql, param)

	sql = "INSERT INTO `hl_battle`(`Id`, `name`) VALUES (%s, %s)"
	param = (user.id, user.name, )
	cursor.execute(sql, param)

	for key in data["enemies"]:
		for item in data["enemies"][key]:

			try:
				data["enemies"][key][item] = json.dumps(data["enemies"][key][item], ensure_ascii=False)
			except:
				pass

			sql = f"UPDATE `hl_battle` SET `{key}_{item}` = %s WHERE Id = %s"
			param = (data["enemies"][key][item], user.id, )
			cursor.execute(sql, param)
	

	sql = "INSERT INTO `hl_equipments`(`Id`, `name`) VALUES (%s, %s)"
	param = (user.id, user.name, )
	cursor.execute(sql, param)

	for key in data["equipments"]:
		print(key, data["equipments"][key])
		sql = f"UPDATE `hl_equipments` SET `{key}` = %s WHERE Id = %s"
		param = (data["equipments"][key], user.id, )
		cursor.execute(sql, param)
	

	sql = "INSERT INTO `hl_info`(`Id`, `name`, `skills`, `MQID`, `SQlist`, `DQlist`, `mapID`, `PVPchance`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
	param = (user.id, user.name, json.dumps(data["skills"]), data["Quests"]["MQID"], json.dumps(data["Quests"]["SQlist"]), json.dumps(data["Quests"]["DQlist"]), data["mapID"], data["PVPchance"], )
	cursor.execute(sql, param)

	sql = "INSERT INTO `hl_inventory`(`Id`, `name`, `items`, `armour`, `weapons`) VALUES (%s, %s, %s, %s, %s)"
	param = (user.id, user.name, json.dumps(data["items"]), json.dumps(data["armour"]), json.dumps(data["weapons"]), )
	cursor.execute(sql, param)

	conn.commit()
	return

def get_economy(id):
	sql = "SELECT * FROM `economy` WHERE Id = %s"
	param = (id, )
	cursor.execute(sql, param)
	return cursor.fetchone()

def claim_daily(id):
	sqls = [
		"UPDATE `economy` SET daily = 1 WHERE Id = %s",
		"UPDATE `economy` SET money = money + 100 WHERE Id = %s"
		]
	for sql in sqls:
		param = (id, )
		cursor.execute(sql, param, )

	conn.commit()
	return

def gift(selfID, otherID, money):
	sql = "UPDATE `economy` SET money = money - %s WHERE Id = %s"
	param = (money, selfID,)
	cursor.execute(sql, param)

	sql = "UPDATE `economy` SET money = money + %s WHERE Id = %s"
	param = (money, otherID,)
	cursor.execute(sql, param)
	
	conn.commit()
	return

def save_bank(ID, money):
	sql = "UPDATE `economy` SET money = money - %s WHERE Id = %s"
	param = (money, ID,)
	cursor.execute(sql, param)

	sql = "UPDATE `economy` SET bank = bank + %s WHERE Id = %s"
	param = (money, ID,)
	cursor.execute(sql, param)
	
	conn.commit()
	return

def claim_bank(ID, money):
	sql = "UPDATE `economy` SET money = money + %s WHERE Id = %s"
	param = (money, ID,)
	cursor.execute(sql, param)

	sql = "UPDATE `economy` SET bank = bank - %s WHERE Id = %s"
	param = (money, ID,)
	cursor.execute(sql, param)
	
	conn.commit()
	return


def daily_refresh():
	sqls = [
		"UPDATE `economy` SET `bank`= `bank` * 1.04 WHERE 1",
		"UPDATE `economy` SET `daily`= 0 WHERE 1"
		]
	
	for sql in sqls:
		cursor.execute(sql)

	conn.commit()
	return

def get_DQ():
	sql = "SELECT Id FROM `hl_daily_quests` WHERE 1;"

	cursor.execute(sql)
	return cursor.fetchall()

def DQ_refresh(quests, id):
	quest = json.dumps(quests)

	sql = "UPDATE `hl_info` SET `DQlist`= %s,`PVPchance`= 5 WHERE Id = %s"
	param = (quest, id,)
	cursor.execute(sql, param)
	
	conn.commit()
	return

def GTN_set(id, data):
	number = data[0]
	top = data[1]
	chance = data[2]
	multiply = data[3]

	sql = "UPDATE `gtngame` SET `chance`= %s, `multiply`= %s, `GuessTop` = %s, `GuessBottom` = 0, `GuessNumber`= %s WHERE Id = %s"
	param = (chance, multiply, top, number, id,)
	cursor.execute(sql, param)

	conn.commit()
	return

def GTN_get(id):
	sql = "SELECT * FROM `gtngame` WHERE Id = %s;"
	param = (id, )

	cursor.execute(sql, param)
	return cursor.fetchone()

def GTN_greater(id, number):
	sql = "UPDATE `gtngame` SET `chance`= `chance` - 1, `GuessTop` = %s WHERE Id = %s"
	param = (number, id, )
	cursor.execute(sql, param)

	conn.commit()
	return

def GTN_less(id, number):
	sql = "UPDATE `gtngame` SET `chance`= `chance` - 1, `GuessBottom` = %s WHERE Id = %s"
	param = (number, id, )
	cursor.execute(sql, param)

	conn.commit()
	return

def GTN_gain(id, money):
	sql = "update `economy` set `money` = `money` + %s where Id = %s"
	param = (money, id, )
	cursor.execute(sql, param)

	conn.commit()
	return

def TTT_init(id):
	for i in range(1, 10):
		sql = f"UPDATE `tttgame` SET `slot_{i}`= %s WHERE Id = %s"
		param = ("⬛", id,)
		cursor.execute(sql, param)

	sql = "UPDATE `tttgame` SET `Round`= 4 WHERE Id = %s"
	param = (id,)
	cursor.execute(sql, param)

	conn.commit()
	return

def TTT_getslot(id):
	sql = "SELECT `slot_1`, `slot_2`, `slot_3`, `slot_4`, `slot_5`, `slot_6`, `slot_7`, `slot_8`, `slot_9` FROM `tttgame` WHERE Id = %s;"
	param = (id, )

	cursor.execute(sql, param)
	return cursor.fetchone()

def TTT_getRound(id):
	sql = "SELECT `Round` FROM `tttgame` WHERE Id = %s;"
	param = (id, )

	cursor.execute(sql, param)
	return cursor.fetchone()

def TTT_select(id, num_p, num_c):
	sql = f"UPDATE `tttgame` SET `slot_{num_p}` = '⭕' WHERE Id = %s"
	param = (id,)
	cursor.execute(sql, param)

	sql = f"UPDATE `tttgame` SET `slot_{num_c}` = '❌' WHERE Id = %s"
	param = (id,)
	cursor.execute(sql, param)

	sql = f"UPDATE `tttgame` SET `Round` = `Round` - 1 WHERE Id = %s"
	param = (id,)
	cursor.execute(sql, param)

	conn.commit()
	return

def TTT_gain(id):
	sql = "update `economy` set `money` = `money` + 100 where Id = %s"
	param = (id, )
	cursor.execute(sql, param)

	conn.commit()
	return

def Slot_gain(id, money):
	sql = "update `economy` set `money` = `money` + %s where Id = %s"
	param = (money, id, )
	cursor.execute(sql, param)

	conn.commit()
	return

def PP_start(id, money):
	sql = "update `economy` set `money` = `money` - %s where Id = %s"
	param = (money, id, )
	cursor.execute(sql, param)

	conn.commit()
	return

def PP_init(id, money, pp_slots):
	sql = "UPDATE `ppgame` SET `chance`= 3,`input_money`= %s,`select_1`= -1,`select_2`= -1,`select_3`= -1 WHERE Id = %s"
	param = (money, id, )
	cursor.execute(sql, param)

	for i in range(1, 26):
		sql = f"UPDATE `ppgame` SET `hole_{i}`= %s WHERE Id = %s"
		param = (pp_slots[i - 1], id)
		cursor.execute(sql, param)

	conn.commit()
	return

def PP_getslot(id):
	sql = "SELECT * FROM `ppgame` WHERE Id = %s;"
	param = (id, )

	cursor.execute(sql, param)
	return cursor.fetchone()

def PP_select(id, hole, time):
	sql = f"UPDATE `ppgame` SET `select_{time}`= %s, `chance` = `chance` - 1 WHERE Id = %s"
	param = (hole, id,)
	cursor.execute(sql, param)

	conn.commit()
	return

def PP_gain(id, money):
	sql = "update `economy` set `money` = `money` + %s where Id = %s"
	param = (money, id, )
	cursor.execute(sql, param)

	conn.commit()
	return
