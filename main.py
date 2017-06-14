# -*- coding: utf-8 -*-
import os
import requests
import re
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


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
    update.message.reply_text('Hi! This bot')


def help(bot, update):
    update.message.reply_text('Help')


def echo(bot, update):
    service = TvmazeService()
    text = ''
    serie = service.next_episode(update.message.text)
    if serie:
        text += "<b> %s </b>" % serie['name']
        text += "Status: %s \n \n" % serie['status']
        next_episode = serie.get('next', None)
        previous_episode = serie.get('previous', None)
        if previous_episode:
            text += "The last episode: <b>%sx%s %s</b> \n" % (previous_episode['season'], previous_episode['number'], previous_episode['name'])
            text += "Date: <b>%s %s</b> \n" % (str(previous_episode['airdate']), str(previous_episode['airtime']))
            if previous_episode['summary']:
                summary = remove_tag(previous_episode['summary'])
                text += summary
            text += '\n \n'
        if next_episode:
            text += "The next episode: <b>%sx%s %s</b> \n" % (next_episode['season'], next_episode['number'], next_episode['name'])
            text += "Date: <b>%s %s</b> \n" % (str(next_episode['airdate']), str(next_episode['airtime']))
            if next_episode['summary']:
                summary = remove_tag(next_episode['summary'])
                text += summary
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
    # Get the dispatcher to register handlers
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

if __name__ == '__main__':
    main()