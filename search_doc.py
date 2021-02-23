import os
from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup
import webbrowser
import datetime
import setting, corpcode
import requests

setting = setting.Setting()
corpcode = corpcode.Corpcode()


class SearchDoc():
    def search(self):
        """
        주어진 기업 리스트가 공시 서류안에 있는지 확인
        :return: 보고서 데이터
        """

        API_KEY = setting.get_api_key()
        corp_code = corpcode.load_corpcode()
        data = pd.DataFrame()
        for i in range(len(corp_code)):
            url = f"https://opendart.fss.or.kr/api/list.xml?crtfc_key={API_KEY}&corp_code={corp_code[i]}&bgn_de=20190110"
            resultXML = urlopen(url)
            result = resultXML.read()
            xmlsoup=BeautifulSoup(result,'html.parser')
            # xml에서 list태그 모두 찾기
            te = xmlsoup.findAll("list")
            for t in te:
                temp = pd.DataFrame(data={"corp_name": [t.corp_name.string],
                                          "corp_code": [t.corp_code.string],
                                          "report_nm": [t.report_nm.string],
                                          "rcept_no": [t.rcept_no.string],
                                          "rcept_dt": [t.rcept_dt],
                                          },
                                    columns=["corp_name", "corp_code", "report_nm", "rcept_no", "rcept_dt"],
                                    )
                data = pd.concat([data, temp])

        # data인덱싱 새로 해줌
        data = data.reset_index(drop=True)

        return data


    def __filter_keyword(self, data):
        """
        주어진 키워드로 보고서를 필터링
        :param data: search()합수의 보고서 데이터
        :return: 필터링된 보고서
        """
        # 키워드 지정
        setting.set_keyword()

        # 키워드 필터링
        keyword = setting.get_keyword()
        # or로 키워드 있는 공시 다 필터링 하는 것인데 이해 못했음
        filtered_data = data[data.report_nm.apply(lambda x: any(i in x for i in keyword))]
        filtered_data = filtered_data.reset_index(drop=True)

        return filtered_data


    def __create_downlink(self, data):
        """
        보고서를 받아 다운로드 링크 생성
        :param data: 보고서 데이터 (type: pandas Dataframe)
        :return: 다운로드 링크 리스트 (type: list[string])
        """
        # 보고서 리스트 다운로드 링크
        total_link = list()

        # 공시 다운화면 리스트
        downpage_url_list = self.__get_downpage(data)
        for downpage_url in downpage_url_list:
            response = requests.get(downpage_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # 개별 다운로드 링크
            down_url = list()
            for link in soup.findAll('a'):
                down_url.append("http://dart.fss.or.kr"+link.get('href'))
            # 마지막 쓸대없는 정보 제거
            down_url.pop()
            total_link.append(down_url[:])
            # 다음 루프때 사용할 수 있도록 제거
            down_url.clear()

        return total_link


    def __create_filename(self, data):
        """
        보고서 정보로 파일 이름 리스트 반환
        :param downpage_list: 다운페이지 링크 리스트 (type: list[string])
        :return: 파일 이름 리스트 (type: list[string])
        """
        total_filename_list = list()
        # 공시 다운화면 리스트
        downpage_url_list = self.__get_downpage(data)
        for downpage_url in downpage_url_list:
            response = requests.get(downpage_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # 하나의 다운화면 안에 있는 파일 리스트
            temp_list = list()
            for filename in soup.findAll('td'):
                # 각 파일 이름
                temp = filename.text.strip()
                # 파일 이름이 있을 경우에만 저장
                if temp:
                    temp_list.append(temp)
            total_filename_list.append(temp_list)

        return total_filename_list


    def __get_downpage(self, data):
        """
        보고서 정보 받아서 다운페이지 링크 리스트 반환
        :param data: 보고서 리스트 (type: panda dataframe)
        :return: 다운페이지 리스트 (type: list[string])
        """
        downpage_list = list()
        for i in range(len(data.index)):
            rcept_no = data['rcept_no'][i]
            # 공시 첫 화면
            main_url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+rcept_no
            response = requests.get(main_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # a 태그 안에 href attribute가 #download찾고 그거의 onclick attribute에서 slicing
            dcm = soup.find('a', {"href":"#download"})["onclick"][35:42]

            # 공시 다운 화면
            downpage_url = "http://dart.fss.or.kr/pdf/download/main.do?rcp_no="+rcept_no+"&dcm_no="+dcm
            downpage_list.append(downpage_url)
        return downpage_list


    def save_file(self,data):
        """
        보고서 리스트를 사용해 파일을 저장
        :param response: 보고서 리스트 (type: panda dataframe)
        """
        # 브라우저만 다운을 가능하게 하는 것 같아서 user-agent를 넣어줘야함
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.150 Safari/537.36'}
        filtered_data = self.__filter_keyword(data)
        filename_list = self.__create_filename(filtered_data)
        downlink_list = self.__create_downlink(filtered_data)

        for i in range(len(downlink_list)):
            for j in range(len(downlink_list[i])):
                file_name = filename_list[i][j]
                today_date = datetime.date.today().isoformat()
                file_path = f"data/save/"

                # 폴더가 없으면 생성
                if not os.path.isdir(file_path):
                    os.mkdir(file_path)

                file_path = f"data/save/{today_date}/"

                # 폴더가 없으면 생성
                if not os.path.isdir(file_path):
                    os.mkdir(file_path)

                temp = file_path + file_name
                with open(temp,'wb') as file:
                    response = requests.get(downlink_list[i][j], allow_redirects=True, headers=headers)
                    file.write(response.content)


    # 브라우저에서 열기
    # open_url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+data['rcept_no'][0]
    # webbrowser.open(open_url)

    # download_url = "dart.fss.or.kr/pdf/download/zip.do?rcpNo=" + data['rcept_no'][0] + "&"  dcm 번호를 긁어와야함
    # # http://henryquant.blogspot.com/2019/02/r-dart-api.html 참고

    # __get_filetype(__create_filename(__filter_keyword(search())))

