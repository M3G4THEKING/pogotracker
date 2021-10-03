
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, Filters, InlineQueryHandler, MessageHandler

from InlineButton import InlineRaid
from Functions import codice_amico, getUser, info, livello, nickname, raid, start, team

def loadCallbackQueries(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(CallbackQueryHandler())

def loadCommands(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(CommandHandler("codice_amico", codice_amico))
	dispatcher.add_handler(CommandHandler("info", info))
	dispatcher.add_handler(CommandHandler("livello", livello))
	dispatcher.add_handler(CommandHandler("nickname", nickname))
	dispatcher.add_handler(CommandHandler("raid", raid))
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("team", team))

def loadInlineQueries(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(InlineQueryHandler(InlineRaid))

def loadMessageHandler(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(MessageHandler(Filters.all, getUser))