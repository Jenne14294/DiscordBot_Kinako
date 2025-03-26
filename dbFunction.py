import json
import mysql.connector

try:
	conn = mysql.connector.connect(
		user = "root", 
		password = "", 
		host = "localhost", 
		port = 3306, 
		database = "discordbot"
	)
	
	cursor = conn.cursor(dictionary = True)

except mysql.connector.Error as e:
	print("DB無法連線")

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

def GTN_gain(id, money):
	sql = "update `economy` set `money` = `money` + %s where Id = %s"
	param = (money, id, )
	cursor.execute(sql, param)

	conn.commit()
	return