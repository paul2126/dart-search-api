import os
from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup
import webbrowser
import time
import datetime
import setting, corpcode
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# timeout 적용시키는 코드
DEFAULT_TIMEOUT = 10  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)

# 재시도 할 수 있게 하는 코드
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

class SearchDoc():
    def __init__(self):
        self.setting_cls = setting.Setting()
        self.corpcode_cls = corpcode.Corpcode()
        self.API_KEY = self.setting_cls.get_api_key()
        self.corp_code = self.corpcode_cls.load_corpcode()
        self.data = pd.DataFrame()
        self.date_range = self.setting_cls.get_range()

        # 분당 100회 미만을 유지하기 위한 카운터
        # corpcode.py에서 이미 한번 요청을 해서 1부터 시작
        self.cnt_download = 1

    def add_data(self):
        """
        각 기업의 보고서들을 합침
        :return: 보고서 데이터 (type: pandas dataframe)
        """
        # 주어진 기업 수 만큼 반복
        for i in range(len(self.corp_code)):
            page_cnt = self.get_page_cnt(i)
            if page_cnt > 1:
                for j in range(1, page_cnt + 1):
                    temp_data = self.search(j, i)
                    self.data = pd.concat([self.data, temp_data])
            else:
                self.data = pd.concat([self.data, self.search(1, i)])

        # data인덱싱 새로 해줌
        self.data = self.data.reset_index(drop=True)
        print(self.data)
        return self.data

    def get_page_cnt(self, corp_code_n):
        """
        기업 번호를 받아 총 몇 페이지 있는지 반환
        :param corp_code_n: 기업번호 (type: int)
        :return: 페이지 수 (type: int)
        """
        url = f"https://opendart.fss.or.kr/api/list.xml?crtfc_key={self.API_KEY}&corp_code={self.corp_code[corp_code_n]}" \
              f"&bgn_de={self.date_range[0]}&end_de={self.date_range[1]}&page_count=100"
        self.check_request_n()  # 요청 횟수 확인
        print('get_page_cnt')
        resultXML = urlopen(url)
        result = resultXML.read()
        xmlsoup = BeautifulSoup(result, 'html.parser')
        # xml에서 total_count 태그 모두 찾기
        page_cnt = xmlsoup.find("total_page").string

        return int(page_cnt)

    def search(self, page_cnt, corp_code_n):
        """
        기업 번호와 해당 페이지 번호를 가져와 문서 크롤링
        :param page_cnt: 해당 페이지 번호 (type: int)
        :param corp_code_n: 기업 번호 (type: int)
        :return: 보고서 리스트 (type: pandas dataframe)
        """
        data = pd.DataFrame()

        url = f"https://opendart.fss.or.kr/api/list.xml?crtfc_key={self.API_KEY}&corp_code={self.corp_code[corp_code_n]}" \
              f"&bgn_de={self.date_range[0]}&end_de={self.date_range[1]}&page_count=100&page_no={page_cnt}"
        self.check_request_n()  # 요청 횟수 확인
        print('search')
        resultXML = urlopen(url)
        result = resultXML.read()
        xmlsoup = BeautifulSoup(result, 'html.parser')

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
            data = pd.concat([temp, data])

        return data

    def __filter_keyword(self, data):
        """
        주어진 키워드로 보고서를 필터링
        :param data: 보고서 데이터 (type: pandas dataframe)
        :return: 필터링된 보고서 (type: pandas dataframe)
        """
        # # 키워드 지정
        # self.setting_cls.set_keyword()

        # 키워드 필터링
        keyword = self.setting_cls.get_keyword()
        if keyword:  # 키워드가 공백인지 확인
            # or로 키워드 있는 공시 다 필터링 하는 것인데 이해 못했음
            filtered_data = data[data.report_nm.apply(lambda x: any(i in x for i in keyword))]
            filtered_data = filtered_data.reset_index(drop=True)

            return filtered_data
        else:
            return data
    def __create_downlink(self, downpage_info_list):
        """
        다운 페이지 정보를 받아 다운로드 링크 생성
        :param downpage_info_list: 다운 페이지 정보 리스트 (type: list[string])
        :return: 다운로드 링크 리스트 (type: list[string])
        """
        # 보고서 리스트 다운로드 링크
        total_link = list()

        # 공시 다운화면 리스트
        for downpage in downpage_info_list:
            # 개별 다운로드 링크
            down_url = list()
            for link in downpage.findAll('a'):
                down_url.append("http://dart.fss.or.kr"+link.get('href'))
            # 마지막 쓸대없는 정보 제거
            down_url.pop()
            total_link.append(down_url[:])
            # 다음 루프때 사용할 수 있도록 제거
            down_url.clear()

        return total_link


    def __create_filename(self, downpage_info_list):
        """
        보고서 정보로 파일 이름 리스트 반환
        :param downpage_info_list: 다운 페이지 정보 리스트 (type: list[string])
        :return: 파일 이름 리스트 (type: list[string])
        """
        total_filename_list = list()
        # 공시 다운화면 리스트
        for downpage in downpage_info_list:

            # 하나의 다운화면 안에 있는 파일 리스트
            temp_list = list()
            for filename in downpage.findAll('td'):
                # 각 파일 이름
                temp = filename.text.strip()
                # 파일 이름이 있을 경우에만 저장
                if temp:
                    temp_list.append(temp)
            total_filename_list.append(temp_list)

        return total_filename_list

    def save_downpage_info(self, downpage_url_list):
        """
        다운페이지 url을 받아서 페이지 정보를 저장
        :param downpage_url_list: 다운페이지 url리스트 (type: list[string])
        :return: 다운페이지 정보 리스트 (type: list[string])
        """
        # 다운로드 페이지 정보를 담은 리스트
        downpage_info_list = list()

        for downpage_url in downpage_url_list:
            self.check_request_n()  # 요청 횟수 확인
            print('save_donwpage_info')
            # response = requests.get(downpage_url)
            response = http.get(downpage_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            downpage_info_list.append(soup)

        return downpage_info_list

    def __get_downpage(self, data):
        """
        보고서 정보 받아서 다운페이지 링크 리스트 반환
        :param data: 보고서 리스트 (type: panda dataframe)
        :return: 다운페이지 리스트 (type: list[string])
        """
        downpage_url_list = list()
        for i in range(len(data.index)):
            rcept_no = data['rcept_no'][i]
            # 공시 첫 화면
            main_url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+rcept_no
            self.check_request_n()  # 요청 횟수 확인
            print('get_downpage')
            # response = requests.get(main_url)
            response = http.get(main_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # a 태그 안에 href attribute가 #download찾고 그거의 onclick attribute에서 slicing
            dcm = soup.find('a', {"href":"#download"})["onclick"][35:42]

            # 공시 다운 화면
            downpage_url = "http://dart.fss.or.kr/pdf/download/main.do?rcp_no="+rcept_no+"&dcm_no="+dcm
            downpage_url_list.append(downpage_url)
        return downpage_url_list


    def save_file(self,data):
        """
        보고서 리스트를 사용해 파일을 저장
        :param data: 보고서 (type: panda dataframe)
        """
        # 브라우저만 다운을 가능하게 하는 것 같아서 user-agent를 넣어줘야함
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.150 Safari/537.36'}
        filtered_data = self.__filter_keyword(data)
        downpage_url_list = self.__get_downpage(filtered_data)
        downpage_info_list = self.save_downpage_info(downpage_url_list)

        filename_list = self.__create_filename(downpage_info_list)
        downlink_list = self.__create_downlink(downpage_info_list)

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
                    self.check_request_n()  # 요청 횟수 확인
                    # response = requests.get(downlink_list[i][j], allow_redirects=True, headers=headers)
                    response = http.get(downlink_list[i][j], allow_redirects=True, headers=headers)
                    file.write(response.content)


    def check_request_n(self):
        if self.cnt_download == 85:
            self.cnt_download = 1
            time.sleep(65)
        else:
            self.cnt_download += 1
        print(self.cnt_download)

    # 브라우저에서 열기
    # open_url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+data['rcept_no'][0]
    # webbrowser.open(open_url)

    # download_url = "dart.fss.or.kr/pdf/download/zip.do?rcpNo=" + data['rcept_no'][0] + "&"  dcm 번호를 긁어와야함
    # # http://henryquant.blogspot.com/2019/02/r-dart-api.html 참고

    # __get_filetype(__create_filename(__filter_keyword(search())))

