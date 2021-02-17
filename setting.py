import os

'''
기본적인 설정들을 입출력하는 모듈
'''

def set_api_key():
    """
    api_key를 입력받아 settings.txt에 저장
    """
    # data 폴더가 있는지 확인 -> 없으면 생성
    data_path = "data"
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    # settings.txt파일이 있는지 확인
    file_path = "data/settings.txt"
    if not os.path.isfile(file_path):
        API_KEY = input("API KEY를 입력해주세요")

        # API_KEY 저장
        file = open(file_path, "w")
        file.write("API_KEY\n")
        file.write(API_KEY)
        file.close()


def get_api_key():
    """
    settings.txt에서 API_KEY를 읽어 반환
    :return: API_KEY
    """
    file_path = "data/settings.txt"
    API_KEY = ""
    if os.path.isfile(file_path):
        file = open(file_path, "r")
        file.readline()
        API_KEY = file.readline()

    return API_KEY
