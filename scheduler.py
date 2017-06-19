from apscheduler.schedulers.blocking import BlockingScheduler
from services import TvmazeService
import telegram
from telegram.bot import Bot
import config
import database

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=5)
def schedule_day():
    service = TvmazeService()
    series = service.schedule()
    bot = Bot(token=config.TOKEN)
    for serie in series:
        results = database.get_registers(serie['id'])
        for result in results:
            text = serie['name'] + 'HOY'
            bot.send_message(
                chat_id=result,
                text=text,
                parse_mode=telegram.ParseMode.HTML
            )

sched.start()
