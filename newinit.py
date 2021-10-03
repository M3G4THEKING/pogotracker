import logging
from logging.handlers import TimedRotatingFileHandler
from telegram.ext import Updater
from telegram import Bot
from Database import createConnection
from JSONParser import loadJSON, loadDatabaseConfig
from CommandHandler import loadCommands, loadCallbackQueries

"""
RaidHelpBot
Modulo Principale
Qui carichiamo i JSON necessari e le risorse per i componenti principali (Bot, Database)
"""

logging.basicConfig(
	format = "[%(asctime)s - %(levelname)s] %(message)s",
	level = logging.INFO,
	datefmt = "%d/%m/%Y %H:%M:%S",
	handlers = [
		TimedRotatingFileHandler("logs/AdventureGame.log", when = "midnight", backupCount = 14)
	]
)

def main() -> None:
	createConnection(loadDatabaseConfig("Connect.json"))
	BotInfos = loadJSON("Bot.json")
	bot = Bot(token = BotInfos["Token"])
	updater = Updater(BotInfos["Token"])

	logging.info(bot.getMe())

	loadCommands(updater.dispatcher)
	loadCallbackQueries(updater.dispatcher)

	logging.getLogger('apscheduler').setLevel(logging.WARNING)

	updater.start_polling()

	updater.idle()

if __name__ == "__main__":
	main()