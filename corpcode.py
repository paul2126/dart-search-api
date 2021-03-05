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
setting = setting.Setting()


class Corpcode:
    def download_corpcode(self):
        """
        기업 고유번호를 다운받아 csv로 저장하는 모듈
        csv 순서는 "corp_code", "corp_name", "stock_code", "modify_date"
        """
        print("", end="") #exe파일에서 print가 없으면 시작을 안하는 경우 때문에 넣음
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

        file.close()

    def load_corpcode(self):
        """
        corpecode.txt에서 기업 코드 반환
        :return: corpcode
        """
        corpcode = list()
        temp = setting.get_corpname_corpcode()
        for i in range(len(temp)):
            corpcode.append(temp[i][1])
        return corpcode

    def compare_corpcsv(self, corp_list):
        corp_general_info = list()
        corpcode = list()
        corpname = list()
        # 기업 고유번호 읽어와서 corp에 저장
        file_path = "data/corpcode.csv"
        if os.path.isfile(file_path):
            with open(file_path) as file:
                for file_data in file.readlines():
                    corp_general_info.append(file_data.split(","))

        # 입력받은 기업 이름과 비교해 기업 고유번호 저장
        for name in corp_list:
            for data in corp_general_info:
                if data[1] == name:
                    corpcode.append(data[0])
                    corpname.append(data[1])
                    # 앞 부분만 입력해서 나머지 부분을 채우는 것은 나중에 추가해야할듯
                    # elif data[1].startswith(name):
                    #     corpcode.append(data[0])
                    #     corpname.append(data[1])
                    break

        return corpname, corpcode

    def csv_to_list(self):
        """
        csv 파일을 list로 변환
        :return: corp list (type: list[string])
        """
        corp_name_list = list()

        # 기업 고유번호 읽어와서 기업이름을 리스트로
        file_path = "data/corpcode.csv"
        if os.path.isfile(file_path):
            with open(file_path) as file:
                file.readline()
                for file_data in file.readlines():
                    corp_name_list.append(file_data.split(",")[1])

        return corp_name_list

    def check_corpcode(self): ## 설명 수정
        """
        corpcode.txt에 이미 저장되어있는 기업리스트가 있는지 확인
        True = 기업리스트가 저장되어있음
        False = 기업리스트가 없음
        :return: True/False
        """

        # 저장되어있는 기업 리스트가 있는지 확인
        saved_corp = setting.get_corpname_corpcode()
        condi = False
        if saved_corp:
            condi = True
        else:
            condi = False

        return condi
