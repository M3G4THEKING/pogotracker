from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler

def loadCommands(dispatcher: Dispatcher) -> None:
	return
	#dispatcher.add_handler(CommandHandler("start", start))

def loadCallbackQueries(dispatcher: Dispatcher) -> None:
	dispatcher.add_handler(CallbackQueryHandler())