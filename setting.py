import os

'''
기본적인 설정들을 입출력하는 모듈
'''

setting_path = "data/settings/"


def set_api_key():
    """
    api_key를 입력받아 api.txt에 저장
    """
    # data/settings 폴더가 있는지 확인 -> 없으면 생성
    data_path = "data"
    if not os.path.isdir(data_path):
        os.mkdir(data_path)
    data_path = "data/settings"
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    file_name = "api.txt"
    file_path = setting_path + file_name
    # api.txt파일이 있는지 확인
    if not os.path.isfile(file_path):
        API_KEY = input("API KEY를 입력해주세요")

        # API_KEY 저장
        file = open(file_path, 'w')
        file.write("API_KEY\n")
        file.write(API_KEY + "\n\n")
        file.close()


def get_api_key():
    """
    settings.txt에서 API_KEY를 읽어 반환
    :return: API_KEY
    """
    API_KEY = ""
    file_name = "api.txt"
    file_path = setting_path + file_name
    if os.path.isfile(file_path):
        file = open(file_path, 'r')
        file.readline()
        API_KEY = file.readline().strip()
        file.close()

    return API_KEY


def set_corpcode(corpname, corpcode):
    """
    corpcode.txt에 기업 고유번호를 저장
    """
    file_name = "corpcode.txt"
    file_path = setting_path + file_name

    file = open(file_path, 'w')
    file.write("기업 고유번호\n")
    for i in range(len(corpcode)):
        file.write(corpname[i] + " ")
        file.write(corpcode[i] + "\n")
    file.write("\n")
    file.close()


def get_corpcode():
    """
    corpcode.txt에 저장되어있는 기업 고유번호 반환
    :return: [corpcode, corpname]
    """
    file_name = "corpcode.txt"
    file_path = setting_path + file_name

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


def set_keyword():
    """
    keyword.txt에 키워드를 저장한다
    """
    file_name = "keyword.txt"
    file_path = setting_path + file_name

    # 키워드가 저장되어있는지 & 변경하고싶은지 확인
    if not __check_keyword():
        while True:
            keyword = input("찾기 원하시는 키워드를 입력해주세요. (여러개의 경우 ,로 나누면 됩니다): ").strip().split(',')

            # 입력한 값이 맞는지 확인
            print("입력한 키워드")
            for i in keyword:
                print("-" + i.strip())
            print()

            confirm = input("입력하신 키워드가 맞나요? Y/N: ")
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

def get_keyword():
    """
    keyword.txt에 저장되어있는 키워드 반환
    :return: keyword
    """
    file_name = "keyword.txt"
    file_path = setting_path + file_name

    result = list()
    if os.path.isfile(file_path):
        file = open(file_path, 'r')
        file.readline()
        while True:
            temp = file.readline().strip().split()
            if not temp: break
            result += temp
        file.close()
    return result

def __check_keyword():
    """
    키워드가 이미 저장되어있는지 확인
    True = 저장되어있는 경우
    False = 저장 안 되어있는 경우
    :return: True/False
    """
    condi = False
    saved_keyword = get_keyword()
    if saved_keyword:
        for keyword in saved_keyword:
            print(keyword)
        check = input("이미 저장되어있는 키워드가 있습니다. 이를 사용하시겠습니까? Y/N: ")
        print()
        if check.lower() == 'y':
            condi = True
        else:
            condi = False

    return condi
