import os
import datetime

'''
기본적인 설정들을 입출력하는 모듈
'''



class Setting():
    def __init__(self):
        self.setting_path = "data/settings/"


    def set_api_key(self, api_key):
        """
        key를 받아 api.txt에 저장
        :return: none
        """
        # data/settings 폴더가 있는지 확인 -> 없으면 생성
        data_path = "data"
        if not self.check_api():
            try:
                os.mkdir(data_path)
                data_path = "data/settings"
                os.mkdir(data_path)
            except Exception as e:
                pass

            file_name = "api.txt"
            file_path = self.setting_path + file_name
            # api.txt파일이 있는지 확인
            # API_KEY = input("API KEY를 입력해주세요")
            API_KEY = api_key

            # API_KEY 저장
            file = open(file_path, 'w')
            file.write("API_KEY\n")
            file.write(API_KEY + "\n\n")
            file.close()


    def check_api(self):
        """
        api.txt가 존재하는지 확인
        :return: api존재 여부 (type: boolean)
        """
        condi = False
        # data/settings 폴더가 있는지 확인
        data_path = "data"
        if os.path.isdir(data_path):
            condi = True
        data_path = "data/settings"
        if os.path.isdir(data_path):
            condi = True


        file_name = "api.txt"
        file_path = self.setting_path + file_name
        # api.txt파일이 있는지 확인
        if os.path.isfile(file_path):
            condi = True
        else:
            condi = False

        return condi

    def get_api_key(self):
        """
        settings.txt에서 API_KEY를 읽어 반환
        :return: API_KEY
        """
        API_KEY = ""
        file_name = "api.txt"
        file_path = self.setting_path + file_name
        if os.path.isfile(file_path):
            file = open(file_path, 'r')
            file.readline()
            API_KEY = file.readline().strip()
            file.close()

        return API_KEY


    def set_range(self, bgn, end):
        """
        date_range.txt에 검색 기간 설정
        :param bgn: 검색 날짜 시작 (type: string)
        :param end: 검색 날짜 종료 (type: string)
        :return: none
        """
        now = datetime.datetime.now()
        formattedDate = now.strftime("%Y%m%d")

        file_name = "date_range.txt"
        file_path = self.setting_path + file_name

        file = open(file_path, 'w')
        # 입력이 있는지 확인
        # 없으면 당일 날짜 입력
        if bgn:
            file.write(bgn + "\n")
        else:
            file.write(formattedDate + "\n")
        if end:
            file.write(end + "\n")
        else:
            file.write(formattedDate + "\n")
        file.close()


    def get_range(self):
        """
        date_range.txt에서 시작/끝 날짜를 읽어서 리스트로 전달
        :return: 기간 리스트 (type: list[string])
        """
        file_name = "date_range.txt"
        file_path = self.setting_path + file_name

        result = list()
        if os.path.isfile(file_path):
            file = open(file_path, 'r')
            result.append(file.readline().strip())
            result.append(file.readline().strip())
            file.close()

        return result


    def check_range(self):
        """
        date_range.txt존재 유무 확인
        :return: true: 파일이 존재하면
        """
        condi = False

        file_name = "date_range.txt"
        file_path = self.setting_path + file_name
        # date_range.txt파일이 있는지 확인
        if os.path.isfile(file_path):
            condi = True

        return condi

    def set_corpname_corpcode(self, corpname, corpcode):
        """
        corpcode.txt에 기업 고유번호를 저장
        """
        file_name = "corpcode.txt"
        file_path = self.setting_path + file_name

        file = open(file_path, 'w')
        file.write("기업 고유번호\n")
        for i in range(len(corpcode)):
            file.write(corpname[i] + " ")
            file.write(corpcode[i] + "\n")
        file.write("\n")
        file.close()


    def get_corpname_corpcode(self):
        """
        corpcode.txt에 저장되어있는 기업 고유번호 반환
        :return: [corpcode, corpname]
        """
        file_name = "corpcode.txt"
        file_path = self.setting_path + file_name

        result = list()
        if os.path.isfile(file_path):
            file = open(file_path, 'r')
            file.readline()
            while True:
                temp = file.readline().strip().split()
                if not temp: break
                result.append(temp)
            file.close()
        return result


    def set_keyword(self):
        """
        keyword.txt에 키워드를 저장한다
        """
        file_name = "keyword.txt"
        file_path = self.setting_path + file_name

        # 키워드가 저장되어있는지 & 변경하고싶은지 확인
        if not self.check_keyword():
            while True:
                keyword = input("찾기 원하시는 키워드를 입력해주세요. (여러개의 경우 ,로 나누면 됩니다): ").strip().split(',')

                # 입력한 값이 맞는지 확인
                print("입력한 키워드")
                for i in keyword:
                    print("-" + i.strip())

                confirm = input("입력하신 키워드가 맞나요? Y/N: ")
                print("===========================================")
                if confirm.lower() == 'y':
                    file = open(file_path, 'w')
                    file.write("키워드\n")
                    for i in range(len(keyword)):
                        file.write(keyword[i].strip() + "\n")
                    file.write("\n")
                    file.close()
                    break
                else:
                    keyword.clear()

    def get_keyword(self):
        """
        keyword.txt에 저장되어있는 키워드 반환
        :return: keyword
        """
        file_name = "keyword.txt"
        file_path = self.setting_path + file_name

        result = list()
        if os.path.isfile(file_path):
            file = open(file_path, 'r')
            file.readline().strip()
            while True:
                temp = file.readline().strip().split()
                if not temp: break
                result += temp
            file.close()
        return result

    def check_keyword(self):
        """
        키워드가 이미 저장되어있는지 확인
        True = 저장되어있는 경우
        False = 저장 안 되어있는 경우
        :return: True/False
        """
        condi = False
        saved_keyword = self.get_keyword()
        if saved_keyword:
            print("저장되어있는 키워드 리스트")
            for keyword in saved_keyword:
                print(keyword)
            check = input("이미 저장되어있는 키워드가 있습니다. 이를 사용하시겠습니까? Y/N: ")
            print("===========================================")
            if check.lower() == 'y':
                condi = True
            else:
                condi = False

        return condi

    def set_search_time(self, search_time):
        """
        searchtime.txt에 키워드를 저장한다
        """
        file_name = "searchtime.txt"
        file_path = self.setting_path + file_name

        with open(file_path, 'w') as file:
            file.write(search_time)

    def get_search_time(self):
        """
        searchtime.txt에 저장되어있는 키워드 반환
        :return: searchtime
        """
        file_name = "searchtime.txt"
        file_path = self.setting_path + file_name

        search_time = ''
        with open(file_path, 'r') as file:
            search_time = file.readline().strip()

        return search_time

    def check_search_time(self):
        """
        searchtime.txt존재 유무 확인
        :return: true: 파일이 존재하면
        """
        condi = False

        file_name = "searchtime.txt"
        file_path = self.setting_path + file_name
        # searchtime.txt파일이 있는지 확인
        if os.path.isfile(file_path):
            condi = True

        return condi