import time
import platform
import os
import pyperclip
import subprocess
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_utils import element_click, paste_text_to_element


class GammaAutomator:
    def __init__(self):
        load_dotenv()

        # Chrome 브라우저 실행
        if platform.system() == "Darwin":  # macOS
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # 크롬 설치 경로
            user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        else:  # Windows
            chrome_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"  # 크롬 설치 경로
            user_data_dir = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
            
        # # Chrome 프로필 디렉토리 삭제
        # if os.path.exists(user_data_dir):
        #     try:
        #         shutil.rmtree(user_data_dir)
        #         print("Chrome 프로필 디렉토리가 삭제되었습니다.")
        #     except Exception as e:
        #         print(f"Chrome 프로필 디렉토리 삭제 중 오류 발생: {e}")

        # Chrome 브라우저 실행
        if os.path.exists(chrome_path):
            subprocess.Popen([chrome_path, "--remote-debugging-port=9222"])
            time.sleep(2)  # Chrome이 완전히 시작될 때까지 대기
        else:
            print("Chrome 브라우저를 찾을 수 없습니다. 수동으로 Chrome을 실행해주세요.")
            return

        # Chrome 옵션 설정
        _options = webdriver.ChromeOptions()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        download_dir = os.path.abspath(os.path.join(current_dir, "..", "data", "ppts"))
        
        # Chrome 옵션 설정
        _options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        _options.add_argument("--disable-blink-features=AutomationControlled")
        _options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        )
        _options.add_argument("--disable-extensions")
        _options.add_argument("--disable-popup-blocking")
        _options.add_argument("--disable-infobars")
        _options.add_argument("--disable-notifications")
        _options.add_argument("--disable-gpu")
        _options.add_argument("--no-sandbox")
        _options.add_argument("--disable-dev-shm-usage")
        _options.add_argument(f"--download.default_directory={download_dir}")
        _options.add_argument("--download.prompt_for_download=false")
        _options.add_argument("--download.directory_upgrade=true")
        _options.add_argument("--safebrowsing.enabled=false")

        # Chrome 드라이버 초기화
        self.driver = webdriver.Chrome(options=_options)

        # 쿠키 삭제
        self.driver.delete_all_cookies()
        
        # 로컬 스토리지 및 세션 스토리지 삭제
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

        self.driver.get("https://gamma.app/create/paste")

    def login(self):
        element_click(self.driver, '//*[@id="__next"]/div[2]/div[2]/div/div/div[3]/a[1]')
        print("=" * 50)
        print("Gamma.app 웹사이트가 열렸습니다.")
        print("수동으로 로그인을 진행해 주세요.")

        # 사용자 입력 대기
        user_input = ""
        while user_input.lower() != "start":
            user_input = input("로그인이 완료되었으면 'start'를 입력하세요: ")

            if user_input.lower() == "exit":
                self.driver.quit()
                return False

        print("자동화 프로세스를 시작합니다.")
        print("=" * 50)

        return True
    
    # def login(self):
    #     try:
    #         gamma_app_id = os.getenv("GAMMA_APP_ID")
    #         gamma_app_pw = os.getenv("GAMMA_APP_PW")

    #         if not gamma_app_id or not gamma_app_pw:
    #             print(
    #                 "Error: 환경변수에 GAMMA_APP_ID 또는 GAMMA_APP_PW가 설정되지 않았습니다."
    #             )
    #             return False

    #         if paste_text_to_element(self.driver, '//*[@id="email"]', gamma_app_id):

    #             if paste_text_to_element(self.driver, '//*[@id="password"]', gamma_app_pw):
    #                 print("비밀번호 입력 성공")

    #                 element_click(
    #                     self.driver, 
    #                     '//*[@id="__next"]/div[2]/div[2]/div[2]/div/div/div/form/div/div[4]/button'
    #                 )
    #             else:
    #                 print("Error: 비밀번호 입력 실패")
    #         else:
    #             print("Error: 이메일 입력 실패")

    #     except Exception as e:
    #         print(f"login 함수 에러 발생: {e}")
    #         return False  # 요소 로딩 실패 또는 기타 에러

    #     return True  # 로그인 시도 성공

    def automate_gamma_ppt_creation(self, paste_content):
        try:
            if self.paste_text_to_element(
                '//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div',
                paste_content,
            ):
                time.sleep(1)
            else:
                print("텍스트 붙여넣기 실패")
                return False

            # 페이지 이동
            if self.element_click(
                '//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div/div[3]/button'
            ):
                print("페이지 이동 성공")
                time.sleep(3)
            else:
                print("페이지 이동 실패")
                return False

            if self.element_click(
                '//*[@id="main"]/div/div[2]/div[4]/div/div[2]/div/div[2]/div/button'
            ):
                if self.element_click(
                    '//*[@id="main"]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[2]/div/div/button'
                ):
                    print("PPT 제작 시작")
                    return True
            else:
                print("PPT 제작 실패")
                return False

        except Exception as e:
            print(f"Gamma 자동화 중 오류 발생: {e}")
            return False

    def export_ppt(self):
        try:
            # 첫 번째 요소 클릭 - 내보내기 버튼
            if self.element_click(
                self.driver,
                "/html/body/div[1]/div/div/div/div/div[1]/div[2]/button"
            ):
                print("내보내기 버튼 클릭 성공")
                time.sleep(2)
            else:
                print("내보내기 버튼 클릭 실패")
                return False

            # 두 번째 요소 클릭 - PPT 옵션
            if self.element_click(self.driver, "/html/body/div[41]/div/div/div[1]/button[5]"):
                print("PPT 옵션 클릭 성공")
                time.sleep(2)
            else:
                print("PPT 옵션 클릭 실패")
                return False

            # 세 번째 요소 클릭 - 다운로드 버튼
            if self.element_click(
                self.driver,
                "/html/body/div[108]/div[3]/div/section/div/div[2]/div[2]/button[2]"
            ):
                print("다운로드 버튼 클릭 성공")
                print("PPT 내보내기 완료!")
                time.sleep(5)  # 다운로드 완료 대기
                return True
            else:
                print("다운로드 버튼 클릭 실패")
                return False

        except Exception as e:
            print(f"PPT 내보내기 중 오류 발생: {e}")
            return False


if __name__ == "__main__":
    automator = GammaAutomator()
    automator.login()
    
