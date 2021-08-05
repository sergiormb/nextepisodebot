# -*- coding: utf-8 -*-
import telegram
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from botanio import botan
import logging
import json
import urllib

import config
import database
from services import TvmazeService
from utils import remove_tag, convert_to_timezone, convert_to_datetime
import sys

reload(sys)
sys.setdefaultencoding('utf8')

with open('language/translations.json') as json_data:
    translations = json.load(json_data)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    lang = update.message.from_user.language_code[:2]
    lang = 'en' if lang != 'es' else lang
    text = translations['start'][lang]
    update.message.reply_text(text)


def help(bot, update):
    lang = update.message.from_user.language_code[:2]
    lang = 'en' if lang != 'es' else lang
    text = translations['help'][lang]
    update.message.reply_text(text)


def print_episode(text, episode, lang, type_episode):
    if episode:
        date = convert_to_datetime(episode['airstamp'])
        episode['airtime'] = date.strftime("%H:%M")
        if lang == 'es':
            date = convert_to_timezone(date)
            episode['airdate'] = date.strftime("%d-%m-%Y")
            episode['airtime'] = date.strftime("%H:%M")
        text += translations[type_episode][lang].format(**episode)
        if episode['summary']:
            summary = remove_tag(episode['summary'])
            if lang != 'en':
                try:
                    summary = config.gs.translate(summary, lang)
                except urllib.exceptions.HTTPError:
                    pass
            text += summary
        if type_episode == 'next_episode':
            date_str = episode['airdate'] + ' ' + episode['airtime']
            date_time = datetime.datetime.strptime(date_str, "%d-%m-%Y %H:%M")
            delta = date_time - datetime.datetime.now()
            if delta.days:
                text += translations['left'][lang].format(days=delta.days)
        text += '\n \n'
    return text


def echo(bot, update):
    uid = update.message.from_user
    message_dict = update.message.to_dict()
    event_name = update.message.text
    botan.track(config.BOTAN_TOKEN, uid, message_dict, event_name)
    lang = update.message.from_user.language_code[:2]
    lang = 'en' if lang != 'es' else lang
    service = TvmazeService()
    text = ''
    serie = service.next_episode(update.message.text)
    serie_active = False
    reply_markup = None
    if serie:
        serie_active = True if serie['status'] != 'Ended' else False
        if lang == 'es':
            serie['status'] = translations[serie['status']][lang]
        text += translations['title'][lang].format(name=serie['name'], status=serie['status'])
        next_episode = serie.get('next', None)
        previous_episode = serie.get('previous', None)
        text = print_episode(text, previous_episode, lang, 'last_episode')
        if next_episode:
            text = print_episode(text, next_episode, lang, 'next_episode')
        else:
            if serie_active:
                text += translations['serie_active'][lang]
    else:
        text += "Not found."
    if serie_active:
        search = database.search(update.message.from_user.id, serie['id'])
        if not search:
            button_list = [[
                telegram.InlineKeyboardButton(text=translations['subscribe'][lang], callback_data=str(serie['id'])),
            ]]
        else:
            button_list = [[
                telegram.InlineKeyboardButton(text=translations['unsubscribe'][lang], callback_data=str('baja' + str(serie['id']))),
            ]]
        reply_markup = telegram.InlineKeyboardMarkup(button_list)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=telegram.ParseMode.HTML
    )


def subscriptions(bot, update):
    lang = update.message.from_user.language_code[:2]
    lang = 'en' if lang != 'es' else lang
    uid = update.message.from_user
    subscriptions = database.get_subscriptions(uid.id)
    if not subscriptions:
        text = translations['not_subscriptions'][lang]
    else:
        text = translations['subscriptions'][lang]
        for subscription in subscriptions:
            text += "- %s\n" % str(subscription)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        parse_mode=telegram.ParseMode.HTML
    )


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def new_subscription(bot, update):
    lang = update.callback_query.from_user.language_code[:2]
    lang = 'en' if lang != 'es' else lang
    service = TvmazeService()
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    serie_id = query['data']
    if 'baja' in serie_id:
        serie_baja = serie_id.split('baja')
        serie_id = int(serie_baja[1])
        search = database.search(user_id, serie_id)
        if search:
            remove = database.remove_register(user_id, serie_id)
            if remove:
                text = translations['remove_subscription'][lang]
            else:
                text = 'ERROR'
    else:
        serie_id = int(serie_id)
        serie = service._next_episode(serie_id)
        serie_name = serie['name']
        search = database.search(user_id, serie_id)
        if not search:
            register = database.insert_register(user_id, serie_id, update.effective_chat.id, serie_name)
            if register:
                text = translations['new_subscription'][lang].format(serie=serie_name)
            else:
                text = 'ERROR'
        else:
            text = translations['already_subscribed'][lang]
    bot.answerCallbackQuery(query.id, text=text)


def main():
    # Create the Updater and pass it your bot's token.
    database.create_tables()
    updater = Updater(config.TOKEN)
    if config.PORT:
        updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)
        updater.bot.set_webhook("https://nextepisodebot.herokuapp.com/" + config.TOKEN)
    # # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CallbackQueryHandler(new_subscription))
    dp.add_handler(CommandHandler("subscriptions", subscriptions))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
