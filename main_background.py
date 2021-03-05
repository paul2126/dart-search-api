from traceback import format_exc
from schedule import Scheduler
import setting, search_doc, corpcode
import datetime
import os
import time
import logging

'''
실행파일
'''
setting_cls = setting.Setting()
corpcode_cls = corpcode.Corpcode()
search_doc_cls = search_doc.SearchDoc()


def run():
    print("", end="") #exe파일에서 print가 없으면 시작을 안하는 경우 때문에 넣음
    corpcode_cls.download_corpcode()
    search_doc_cls.save_file(search_doc_cls.add_data())


logger = logging.getLogger('schedule')


# 에러뜨면 로깅하고 스케쥴대로 진행할 수 있게 함
class SafeScheduler(Scheduler):
    """
    An implementation of Scheduler that catches jobs that fail, logs their
    exception tracebacks as errors, optionally reschedules the jobs for their
    next run time, and keeps going.
    Use this to run jobs that may or may not crash without worrying about
    whether other jobs will run or if they'll crash the entire script.
    """

    def __init__(self, reschedule_on_failure=True):
        """
        If reschedule_on_failure is True, jobs will be rescheduled for their
        next run as if they had completed successfully. If False, they'll run
        on the next run_pending() tick.
        """
        self.reschedule_on_failure = reschedule_on_failure
        super().__init__()

    def _run_job(self, job):
        try:
            super()._run_job(job)
        except Exception:
            logger.error(format_exc())
            if not os.path.isdir("log"):
                os.mkdir("log")
            today_date = datetime.date.today().isoformat()
            with open(f"log/back_{today_date}.txt", 'w') as file:
                file.write(format_exc())
            job.last_run = datetime.datetime.now()
            job._schedule_next_run()


# 수정한 스케줄러 적용하기
scheduler = SafeScheduler()
# 지정한 시간 가져오기
search_time = setting_cls.get_search_time()
scheduler.every().day.at(search_time).do(run)
# scheduler.every(5).seconds.do(run)


while True:
    scheduler.run_pending()
    time.sleep(1)