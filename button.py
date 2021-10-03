import utility, functions, authorized
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def button(bot, update):
	print(update)
	#try:
	#	idu = update.callback_query.message.from_user.id
	query = update.callback_query
	#except:
	#	query = update.inline_query
	print(query)
	data = query.data.split()
	if data[0] == "raid":
		functions.raidbutton(bot, query)
		return		
