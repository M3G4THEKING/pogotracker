from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent

from Auth import permLevel
from Database import getRaid, isRaid
from Functions import testoRaid

from JSONParser import getConfig
from uuid import uuid4

def InlineRaid(update: Update):
	queryText = update.inline_query.query
	if len(queryText.split()) == 0:
		return
	if permLevel(update.inline_query.from_user.id) < 3:
		return
	if not queryText.split()[0].isdigit():
		return
	if not isRaid(int(queryText.split()[0])):
		return
	raid = getRaid(int(queryText.split()[0]))
	results, keyboard = [], []
	config = getConfig()
	keyboard.append([InlineKeyboardButton("Presente", callback_data = f"raid {raid.IDRaid} present"), InlineKeyboardButton("Invitami", callback_data = f"raid {raid.IDRaid} invited")])
	keyboard.append([InlineKeyboardButton("Remoto", callback_data = f"raid {raid.IDRaid} fly"), InlineKeyboardButton("Toglimi", callback_data = f"raid {raid.IDRaid} remove")] if config["fly"] else [InlineKeyboardButton("Toglimi", callback_data = f"raid {raid.IDRaid} remove")])
	keyboard.append([InlineKeyboardButton(config["team"]["giallo"], callback_data = f"raid {raid.IDRaid} team giallo"), InlineKeyboardButton(config["team"]["rosso"], callback_data = f"raid {raid.IDRaid} team rosso"), InlineKeyboardButton(config["team"]["blu"], callback_data = f"raid {raid.IDRaid} team blu")] if raid.ora_confermata else [InlineKeyboardButton("Pass Ex?", callback_data = f"raid {raid.IDRaid} passex"), InlineKeyboardButton("Cancella raid", callback_data = f"raid {raid.IDRaid} delete")])
	results.append(InlineQueryResultArticle(id = uuid4(), title = f"Invia: {raid.pokemon}", input_message_content = InputTextMessageContent(testoRaid(raid), parse_mode = "HTML"), reply_markup = InlineKeyboardMarkup(keyboard)))
	update.inline_query.answer(results, cache_time = 2)
