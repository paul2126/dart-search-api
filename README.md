# dart-search-api
한국 금융감독원에서 운영하는 다트(Dart) 시스템 api 사용하는 프로그램으로 지정한 시간에 입력된 키워들을 가진 기업 공시들을 저장합니다

# 1. 실행방법
## 1.1. 직접 실행할 경우 
* 파이썬 파일을 직접 실행할 경우 main_front.py파일 run_process함수에서 main_background.exe를 .py로 변경해야한다

## 1.2. exe파일로 변환해 실행할 경우
* pyinstaller를 사용하여 main_background.py와 main_front.py를 변환한다
	* main_background의 경우 --noconsole옵션을 넣어놓는 것이 편하다
* 만약 에러가 난다면 직접 python.exe와 pyinstaller-script.py 경로를 지정해 실행한다
* main_front.exe를 실행하여 설정을 한다
* 설정이 완료되었다는 메세지와 창이 닫히면 main_background.exe가 백그라운드에서 돌기 시작한다
	* 지정한 기업/키워드/기간에 따라서 다운받는데 걸리는 시간이 변할 수 있다 
	* 80개 이하는 2분 내 - 그 후 80개씩 1분 정도가 늘어난다
* 만약 설정을 바꾸고 싶다면 다시 main_front.exe를 실행하여 재설정을 진행한다

# 2. 프로그램 설명
* main_front 파일을 통해 모든 설정을 변경할 수 있다
	* API_KEY (맨 처음 프로그램을 실행시켰을 때만)
	* 기업
	* 공시 키워드
	* 검색 기간
	* 다운받을 시간

* main_background 파일을 통해 공시 자료를 검색하고 다운 받을 수 있다