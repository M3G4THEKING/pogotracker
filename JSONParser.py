import json

def loadJSON(path: str):
	tmp = {}
	try:
		tmp = json.load(open(path, "r"))
	except:
		pass
	finally:
		return tmp

def loadDatabaseConfig(path: str):
	tmp = loadJSON(path)
	parsed = ''
	for val in tmp:
		parsed += f"{val}={tmp[val]} "
	return parsed.strip()

def getConfig():
	return loadJSON("Config.json")

def getPermessi():
	return loadJSON("Permessi.json")