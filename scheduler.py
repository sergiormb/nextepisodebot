from apscheduler.schedulers.blocking import BlockingScheduler
from services import TvmazeService
import telegram
from telegram.bot import Bot
from main import print_episode
import config
import database
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=12)
def schedule_day():
    service = TvmazeService()
    episodes = service.schedule()
    bot = Bot(token=config.TOKEN)
    for episode in episodes:
        if isinstance(episode, dict):
            if episode.get('show', None):
                show = episode['show']
                results = database.get_registers(show['id'])
                for result in results:
                    text = '<b> HOY: %s</b>\n' % show['name']
                    network = show.get('network', None)
                    if network:
                        text += '%s - %s' % (network['name'], network['country']['name'])
                    text = print_episode(text, episode, 'es', 'next_episode')
                    bot.send_message(
                        chat_id=result,
                        text=text,
                        parse_mode=telegram.ParseMode.HTML
                    )
                    if episode.get('image', None):
                        bot.send_photo(chat_id=result, photo=episode['image'])

if __name__ == '__main__':
    schedule_day()

sched.start()
