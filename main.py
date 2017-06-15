# -*- coding: utf-8 -*-
import os
import requests
import re
import telegram
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from botanio import botan
import logging
import goslate
import json
import urllib2
from pytz import timezone
from dateutil import parser

with open('language/translations.json') as json_data:
    translations = json.load(json_data)

gs = goslate.Goslate()
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
BOTAN_TOKEN = os.environ.get('BOTAN_TOKEN')


class TvmazeService(object):

    def __init__(self):
        self.base_url = 'http://api.tvmaze.com/'
        self.url_search = self.base_url + 'singlesearch/shows'
        self.url_serie = self.base_url + 'shows/'

    def _search(self, q):
        json = None
        url = self.url_search + '?q=' + q
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
        return json

    def _next_episode(self, id):
        url = self.url_serie + str(id) + '?embed[]=nextepisode&embed[]=previousepisode'
        nextepisode = None
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            nextepisode = json
            embedded = json.get('_embedded', None)
            if embedded.get('nextepisode'):
                nextepisode.update({'next': embedded['nextepisode']})
            else:
                nextepisode.update({'error': 'We do not have episode information right now.'})
            nextepisode.update({'previous': embedded['previousepisode']})
        return nextepisode

    def next_episode(self, q):
        next_episode = self._search(q)
        if next_episode:
            next_episode = self._next_episode(next_episode['id'])
        return next_episode


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
                    summary = gs.translate(summary, lang)
                except urllib2.HTTPError:
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
    botan.track(BOTAN_TOKEN, uid, message_dict, event_name)
    lang = update.message.from_user.language_code[:2]
    lang = 'en' if lang != 'es' else lang
    service = TvmazeService()
    text = ''
    serie = service.next_episode(update.message.text)
    if serie:
        if lang == 'es':
            serie['status'] = translations[serie['status']][lang]
        text += translations['title'][lang].format(name=serie['name'], status=serie['status'])
        next_episode = serie.get('next', None)
        previous_episode = serie.get('previous', None)
        text = print_episode(text, previous_episode, lang, 'last_episode')
        text = print_episode(text, next_episode, lang, 'next_episode')
    else:
        text += "Not found."
    bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        parse_mode=telegram.ParseMode.HTML
    )


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    TOKEN = os.environ.get('TOKEN')
    PORT = int(os.environ.get('PORT', '5000'))
    # Create the Updater and pass it your bot's token.

    updater = Updater(TOKEN)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://nextepisodebot.herokuapp.com/" + TOKEN)
    # # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

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


def remove_tag(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)


def convert_to_timezone(date_time):
    return date_time.astimezone(timezone('Europe/Madrid'))


def convert_to_datetime(date):
    return parser.parse(date)

if __name__ == '__main__':
    main()
