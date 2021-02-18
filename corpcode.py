from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import xml.etree.ElementTree as elemTree
import csv
import os
import setting

'''
기업 고유번호 관련 모듈
'''


def download_corpcode():
    """
    기업 고유번호를 다운받아 csv로 저장하는 모듈
    csv 순서는 "corp_code", "corp_name", "stock_code", "modify_date"
    """

    API_key = setting.get_api_key()
    url = "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=" + API_key
    resp = urlopen(url)

    # 수신된 resp의 bytes를 Buffer에 쌓고 zip file을 로드한다
    with ZipFile(BytesIO(resp.read())) as zf:
        # namelist는 해당 파일 이름
        file_list = zf.namelist()
        while len(file_list) > 0:
            file_name = file_list.pop()
            # decode는 binary를 unicode로
            corpCode = zf.open(file_name).read().decode()

    # data 폴더가 있는지 확인 -> 없으면 생성
    data_path = "data"
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    # 저장할 csv파일을 만든다
    file = open("data\corpcode.csv", mode="w", newline="")
    writer = csv.writer(file)
    writer.writerow(["corp_code", "corp_name", "stock_code", "modify_date"])

    tree = elemTree.fromstring(corpCode)

    # 정보 저장하기
    for stock in tree.iter('list'):
        stock_dic = {
            "corp_code": stock.findtext("corp_code"),
            "corp_name": stock.findtext("corp_name"),
            "stock_code": stock.findtext("stock_code"),
            "modify_date": stock.findtext("modify_date"),
        }
        writer.writerow(stock_dic.values())

def load_corpcode():
    """
    기업이름을 받아 corpecode.txt와 비교한 후 매치를 반환
    :return: corpcode
    """
    corp_general_info = list()
    corpcode = list()
    corpname = list()

    if not __check_corpcode():  # 이미 저장된 값이 있는지 확인
        while True:
            # 기업 이름 입력
            corp_names = input('찾고자 하는 기업 이름을 적어주세요. (여러개의 경우 ,로 나누면 됩니다): ').split(',')
            for i in range(len(corp_names)):
                corp_names[i] = corp_names[i].strip()

            # 기업 고유번호 읽어와서 corp에 저장
            file_path = "data/corpcode.csv"
            if os.path.isfile(file_path):
                with open(file_path) as file:
                    for file_data in file.readlines():
                        corp_general_info.append(file_data.split(","))

            # 입력받은 기업 이름과 비교해 기업 고유번호 저장
            for name in corp_names:
                for data in corp_general_info:
                    if data[1] == name:
                        corpcode.append(data[0])
                        corpname.append(data[1])
                    # 앞 부분만 입력해서 나머지 부분을 채우는 것은 나중에 추가해야할듯
                    # elif data[1].startswith(name):
                    #     corpcode.append(data[0])
                    #     corpname.append(data[1])
                        break

            # 찾은 기업이 맞는지 확인
            print("찾은 기업 리스트")
            for data in corpname:
                print("- " + data)
            print()

            confirm = input("찾은 기업들이 맞나요? Y/N: ")
            if confirm.lower() == 'y':
                save_info = input("지금 리스트를 기본으로 설정하시겠습니까? (추후에 변경 가능합니다) Y/N: ")
                if save_info.lower() == 'y':
                    setting.set_corpcode(corpname, corpcode)
                break
            else:
                corpcode.clear()
                corpname.clear()
    else:
        temp = setting.get_corpcode()
        for i in range(len(temp)):
            corpcode.append(temp[i][1])
    return corpcode


def __check_corpcode():
    """
    corpcode.txt에 이미 저장되어있는 기업리스트가 있는지 확인
    True = 기업리스트가 저장되어있음
    False = 기업리스트가 없음
    :return: True/False
    """

    # 저장되어있는 기업 리스트가 있는지 확인
    saved_corp = setting.get_corpcode()
    condi = False
    if saved_corp:
        for i in range(len(saved_corp)):
            print(saved_corp[i][0], end=" ")
            print(saved_corp[i][1])
        check = input("이미 저장되어있는 기업들이 있습니다. 이를 사용하시겠습니까? Y/N: ")
        print()
        if check.lower() == 'y':
            condi = True
        else:
            condi = False

    return condi

