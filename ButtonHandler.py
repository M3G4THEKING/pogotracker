import logging
from telegram import Update
from telegram.ext import CallbackContext
from Functions import raidbutton

def ButtonHandler(update: Update, context: CallbackContext) -> None:
	Handlers = {
		"raid": raidbutton
	}
	Handler = Handlers.get(update.callback_query.data.split()[0])
	update.callback_query.answer('' if Handler else "Non conosco questo bottone!")
	if not Handler:
		logging.warn(f"Unknown button!")
	else:
		logging.info(f"{update.callback_query.from_user.id}: {update.callback_query.data}")
		Handler(update, context)

def annullaButton(update: Update, context: CallbackContext) -> None:
	update.callback_query.edit_message_text(f"{update.callback_query.message.text}\n\nOperazione annullata", parse_mode= "HTML", entities = update.callback_query.message.entities)