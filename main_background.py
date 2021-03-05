import setting, search_doc, corpcode
import schedule
import datetime
import functools
import os
import time

'''
실행파일
'''
setting_cls = setting.Setting()
corpcode_cls = corpcode.Corpcode()
search_doc_cls = search_doc.SearchDoc()

# 스캐줄러 돌릴때 에러 처리위해
def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if not os.path.isdir("log"):
                    os.mkdir("log")
                today_date = datetime.date.today().isoformat()
                with open(f"log/{today_date}.txt", 'w') as file:
                    file.write(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=True)
def run():
    corpcode_cls.download_corpcode()
    search_doc_cls.save_file(search_doc_cls.add_data())

# 지정한 시간 가져오기
search_time = setting_cls.get_search_time()
schedule.every().day.at(search_time).do(run)

while True:
    schedule.run_pending()
    time.sleep(1)


