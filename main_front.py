import psutil  # 실행중인 프로세스 및 시스템 활용 라이브러리
import os
import time
import setting, corpcode, search_doc
import datetime
import traceback

setting_cls = setting.Setting()
corpcode_cls = corpcode.Corpcode()
search_doc_cls = search_doc.SearchDoc()


def kill_process():
    for proc in psutil.process_iter():
        try:
            # 프로세스 이름, PID값 가져오기
            processName = proc.name()
            processID = proc.pid
            # print(processName, ' - ', processID)

            if processName == "main_background.exe":
                parent_pid = processID  # PID
                parent = psutil.Process(parent_pid)  # PID 찾기
                for child in parent.children(recursive=True):  # 자식-부모 종료
                    child.kill()
                parent.kill()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):  # 예외처리
            pass
        # 출처: https: // c0mb.tistory.com / 115[뚠뚠]


def run_process():
    os.startfile('main_background.exe')


def run():
    # api_key 존재 유무 확인
    api_key = ""
    if not setting_cls.check_api():
        while True:
            api_key = input("API KEY를 입력해주세요: ")
            if show_input(api_key):
                setting_cls.set_api_key(api_key)
                break

    # 아래에서 사용할 기업고유번호 다운
    corpcode_cls.download_corpcode()

    # 기간 설정
    bgn, end = "", ""
    while True:
        bgn = input("검색 시작 기간을 입력해주세요. 입력이 없을 경우 당일로 지정합니다 (YYYYMMDD형식) ")
        if show_input(bgn):
            break
    while True:
        end = input("검색 종료 기간을 입력해주세요. 입력이 없을 경우 당일로 지정합니다(YYYYMMDD형식) ")
        if show_input(end):
            setting_cls.set_range(bgn, end)
            break

    # 기업 이름 설정
    saved_corp = setting_cls.get_corpname_corpcode()
    if corpcode_cls.check_corpcode():
        print("저장되어있는 기업 리스트")
        for i in range(len(saved_corp)):
            print(saved_corp[i][0], end=" ")
            print(saved_corp[i][1])
        condi = input("이미 저장되어있는 기업들이 있습니다. 이를 사용하시겠습니까? Y/N: ")
        print("===========================================")
        if condi.lower() == 'y':
            pass
        else:
            recieve_corpname()
    else:
        recieve_corpname()

    # 키워드 설정
    setting_cls.set_keyword()

    # 검색시간 설정
    while True:
        if setting_cls.check_search_time():
            original_search_time = setting_cls.get_search_time()
            print("저장되어있는 검색 시간이 있습니다")
            print(original_search_time)
            condi = input("이미 지정된 시간이 있습니다. 바꾸시겠습니까? Y/N: ")
            print("===========================================")
            if condi.lower() == 'y':
                search_time = input("원하시는 시간을 입력해주세요. (예: 13:03) ")
                if show_input(search_time):
                    setting_cls.set_search_time(search_time)
                    break
            else:
                break
        else:
            search_time = input("원하시는 시간을 입력해주세요. (예: 13:03) ")
            if show_input(search_time):
                setting_cls.set_search_time(search_time)
                break

    print("설정이 완료되었습니다")
    print("3초 후 자동으로 창이 닫힙니다")
    time.sleep(3)



def recieve_corpname():
    while True:
        # 기업 이름 입력
        corp_list = input('찾고자 하는 기업 이름을 적어주세요. (여러개의 경우 ,로 나누면 됩니다): ').split(',')
        for i in range(len(corp_list)):
            corp_list[i] = corp_list[i].strip()
        corpname, corpcode = corpcode_cls.compare_corpcsv(corp_list)

        # 입력 확인
        print("찾은 기업 리스트")
        for name in corpname:
            print("- " + name)

        confirm = input("찾은 기업들이 맞나요? Y/N: ")
        if confirm.lower() == 'y':
            save_info = input("지금 리스트를 기본으로 설정하시겠습니까? (추후에 변경 가능합니다) Y/N: ")
            print("===========================================")
            if save_info.lower() == 'y':
                setting_cls.set_corpname_corpcode(corpname, corpcode)
            break
        else:
            corpcode.clear()
            corpname.clear()
            print("===========================================")

def show_input(data):  # 이거 각 setting으로 옮겨주기
    """
    입력값이 올바른지 확인
    :param data: 어떤 데이터든 가능
    :return: 맞으면 True / 틀리면 False (type: boolean)
    """
    print(data)
    confirm = input("입력을 재대로 하셨나요? Y/N: ")
    print("===========================================")
    if confirm.lower() == 'y':
        return True
    else:
        return False

try:
    kill_process()
    run()
    run_process()
except:
    if not os.path.isdir("log"):
        os.mkdir("log")
    today_date = datetime.date.today().isoformat()
    with open(f"log/{today_date}.txt", 'w') as file:
        file.write(traceback.format_exc())