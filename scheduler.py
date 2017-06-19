from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every minute.')


@sched.scheduled_job('cron', day=14, hour=15, minute=37)
def scheduled_job():
    print('This job is run on day 14 at minute 37, 3pm.')


sched.start()
