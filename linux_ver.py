import os
import time
import setting, corpcode, search_doc
import datetime
import traceback
import requests
import sendmail
import zipfile

setting_cls = setting.Setting()
corpcode_cls = corpcode.Corpcode()
search_doc_cls = search_doc.SearchDoc()
file = open("data/settings/slack.txt")
myToken = file.readline().strip()
file = open("data/settings/gmail.txt", encoding="UTF-8")
email_sender_id = file.readline().strip()
email_sender_psw = file.readline().strip()
email_receiver_name = file.readline().strip()
email_receiver_id = file.readline().strip()


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )


def send_mail():
    # 이메일 보내기
    # SMTP 서버 정보
    smtp_address = ('smtp.gmail.com', 587)  # SMTP 서버 호스트, 포트

    # SMTP 계정 정보
    username = email_sender_id  # Gmail 계정
    password = email_sender_psw  # Gmail 앱 비밀번호

    # 메일 송/수신자 정보
    from_addr = ('전자공시 다운로더', email_sender_id)  # 보내는 사람 주소. (이름, 이메일)
    to_addrs = [  # 받는 사람 주소. (이름, 이메일)
        (email_receiver_name, email_receiver_id)
    ]

    # 메일 제목
    subject = '전자공시 파일입니다'

    # 메일 내용
    body = '''
                전자공시 파일입니다 \n
                감사합니다
                '''

    # 첨부파일
    cur_date = datetime.date.today()
    path_dir = os.path.join(os.getcwd(), 'data', 'save', str(cur_date)+".zip")  # 저장된 파일 위치
    attachments = [path_dir]  # 저장된 파일 리스트에 저장

    mail = sendmail.Mail(smtp_address, from_addr, to_addrs, debug=False)
    mail.setAuth(username, password)
    mail.setMail(subject, body, 'html', attachments=attachments)
    mail.send()

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))
while True:
    try:
        post_message(myToken, "#dart-alarm", '다운 시작')
        counter = True  # 하루 카운터
        now = datetime.datetime.now()
        set_time = setting_cls.get_search_time().replace(':', '')
        if len(set_time) == 3:  # 만약 불러온 값이 10시 이전이라 3자리면 0을 더해줌
            set_time = '0' + set_time

        set_time = datetime.datetime.strptime(now.strftime('%d/%m/%y') + ' ' + set_time, "%d/%m/%y %H%M")
        if counter and set_time < now:
            corpcode_cls.download_corpcode()
            search_doc_cls.save_file(search_doc_cls.add_data())

            # 저장된 파일 앞축
            cur_date = datetime.date.today()
            path_dir = os.path.join(os.getcwd(), 'data', 'save', str(cur_date))
            zipf = zipfile.ZipFile(f'{path_dir}.zip', 'w', zipfile.ZIP_DEFLATED)
            zipdir(path_dir, zipf)
            zipf.close()

            send_mail()
            post_message(myToken, "#dart-alarm", '전송 성공')

            counter = False
            time.sleep(82800)  # 23시간 쉬기

    except:
        if not os.path.isdir("log"):
            os.mkdir("log")
        today_date = datetime.date.today().isoformat()
        today_time = datetime.datetime.now().strftime("%H%M")
        with open(f"log/front_{today_date}_{today_time}.txt", 'w') as file:
            file.write(traceback.format_exc())
        post_message(myToken, "#dart-alarm", traceback.format_exc())
        time.sleep(3600)
