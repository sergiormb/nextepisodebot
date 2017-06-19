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


@sched.scheduled_job('interval', minutes=5)
def schedule_day():
    service = TvmazeService()
    series = service.schedule()
    bot = Bot(token=config.TOKEN)
    for serie in series:
        if isinstance(serie, dict):
            if serie.get('id', None):
                results = database.get_registers(serie['id'])
                for result in results:
                    text = '<b> HOY: </b>'
                    text = print_episode(text, serie, 'es', 'next_episode')
                    bot.send_message(
                        chat_id=result,
                        text=text,
                        parse_mode=telegram.ParseMode.HTML
                    )
                    if serie.get('image', None):
                        bot.send_photo(chat_id=result, photo=serie['image'])

sched.start()
