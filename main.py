import corpcode, setting, search_doc
import schedule
import time

'''
실행파일
'''
setting_cls = setting.Setting()
corpcode_cls = corpcode.Corpcode()
search_doc_cls = search_doc.SearchDoc()

def run():
    setting_cls.set_api_key()
    print('got key')
    corpcode_cls.download_corpcode()
    print('download complete')
    search_doc_cls.save_file(search_doc_cls.search())


while True:
    schedule.run_pending()
    time.sleep(1)
