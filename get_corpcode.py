from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import xml.etree.ElementTree as elemTree
import csv
import os
import setting

'''
기업 고유번호를 받아 csv로 저장하는 모듈
csv 순서는 "corp_code", "corp_name", "stock_code", "modify_date"
'''

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