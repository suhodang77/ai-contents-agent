import time
import platform
import os
import pyperclip
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GammaAutomator:
    def __init__(self):
        load_dotenv()

        _options = webdriver.ChromeOptions()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        download_dir = os.path.abspath(os.path.join(current_dir, "..", "data", "ppts"))
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
        }  # 다운로드 경로 설정
        _options.add_experimental_option("prefs", prefs)  # ppt 다운로드 경로 설정
        _options.add_argument("disable-blink-features=AutomationControlled")
        _options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        )

        _options.add_experimental_option("excludeSwitches", ["enable-automation"])
        _options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=_options)

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.driver.delete_all_cookies()

        self.driver.get("https://gamma.app/create/paste")

    def send_select_all_and_clear(self, element):
        if platform.system() == "Darwin":  # macOS
            element.send_keys(Keys.COMMAND, "a")
        else:  # Windows, Linux
            element.send_keys(Keys.CONTROL, "a")

        element.send_keys(Keys.DELETE)

    def login(self):
        try:
            gamma_app_id = os.getenv("GAMMA_APP_ID")
            gamma_app_pw = os.getenv("GAMMA_APP_PW")

            if not gamma_app_id or not gamma_app_pw:
                print(
                    "Error: 환경변수에 GAMMA_APP_ID 또는 GAMMA_APP_PW가 설정되지 않았습니다."
                )
                return False

            if self.paste_text_to_element('//*[@id="email"]', gamma_app_id):
                time.sleep(1)

                if self.paste_text_to_element('//*[@id="password"]', gamma_app_pw):
                    print("비밀번호 입력 성공")
                    time.sleep(1)

                    self.element_click(
                        '//*[@id="__next"]/div[2]/div[2]/div[2]/div/div/div/form/div/div[4]/button'
                    )
                else:
                    print("Error: 비밀번호 입력 실패")
            else:
                print("Error: 이메일 입력 실패")

        except Exception as e:
            print(f"login 함수 에러 발생: {e}")
            return False  # 요소 로딩 실패 또는 기타 에러

        return True  # 로그인 시도 성공

    def check_login_failure(self):
        driver = self.driver
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[id^='field-'][id*='feedback']")
                )
            )
            return True  # 로그인 실패
        except:  # noqa: E722
            return False  # 로그인 성공

    def paste_text_to_element(
        self, xpath, text_to_paste, timeout=10
    ):  # driver 매개변수 제거
        """
        CSS 선택자를 사용하여 요소가 로딩되었는지 확인하고,
        클립보드를 이용하여 텍스트를 붙여넣습니다.

        Args:
            xpath: 텍스트를 붙여넣을 요소의 CSS 선택자
            text_to_paste: 붙여넣을 텍스트 문자열
            timeout: 대기 시간 (초), 기본값 10초

        Returns:
            True: 요소 로딩 및 텍스트 붙여넣기 성공
            False: 요소 로딩 실패 또는 텍스트 붙여넣기 실패
        """
        driver = self.driver
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            self.send_select_all_and_clear(element)

            pyperclip.copy(text_to_paste)  # 텍스트를 클립보드에 복사
            element.click()  # 요소에 focus
            if platform.system() == "Darwin":  # macOS
                element.send_keys(Keys.COMMAND, "v")
            else:  # Windows, Linux
                element.send_keys(Keys.CONTROL, "v")

            print(f"요소 '{xpath}'에 텍스트 붙여넣기 성공")
            return True

        except TimeoutError:
            print(f"요소 '{xpath}' 로딩 시간 초과")
            return False
        except Exception as e:
            print(f"요소 '{xpath}'에 텍스트 붙여넣기 중 오류 발생: {e}")
            return False

    def element_click(self, xpath, timeout=10):
        """
        CSS 선택자를 사용하여 요소가 로딩되었는지 확인하고, 요소를 클릭합니다.

        Args:
            xpath: 텍스트를 붙여넣을 요소의 XPATH
            timeout: 대기 시간 (초), 기본값 10초
        """
        driver = self.driver
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            element.click()
            return True

        except Exception as e:
            print(f"요소 {xpath} 클릭 중 오류 발생: {e}")
            return False

    def automate_gamma_ppt_creation(self, paste_content):
        try:
            while True:
                if not self.login():
                    print(
                        "로그인에 실패했습니다. .env 파일 설정을 확인하거나, 네트워크 환경을 점검해주세요."
                    )
                    return False
                elif self.check_login_failure():
                    print("로그인 실패. 다시 시도합니다.")
                    time.sleep(2)
                else:
                    print("로그인 성공!")
                    break

            time.sleep(3)

            # .tiptap 요소에 텍스트 붙여넣기
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
                "/html/body/div[1]/div/div/div/div/div[1]/div[2]/button"
            ):
                print("내보내기 버튼 클릭 성공")
                time.sleep(2)
            else:
                print("내보내기 버튼 클릭 실패")
                return False

            # 두 번째 요소 클릭 - PPT 옵션
            if self.element_click("/html/body/div[41]/div/div/div[1]/button[5]"):
                print("PPT 옵션 클릭 성공")
                time.sleep(2)
            else:
                print("PPT 옵션 클릭 실패")
                return False

            # 세 번째 요소 클릭 - 다운로드 버튼
            if self.element_click(
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

    # 기존 URL 대신 테스트할 URL로 변경
    automator.driver.get("https://gamma.app/docs/-v5d5rqhky711zrs?mode=doc")

    print("브라우저가 지정된 URL로 이동했습니다.")
    print("로그인이 필요하면 먼저 로그인을 수동으로 진행해주세요.")
    print("준비가 완료되면 'start'를 입력하여 export_ppt 함수를 실행하세요.")

    # 사용자 입력 대기
    while True:
        user_input = input("명령을 입력하세요 (start/quit): ").strip().lower()

        if user_input == "start":
            print("PPT 내보내기를 시작합니다...")
            result = automator.export_ppt()

            if result:
                print("PPT 내보내기가 성공적으로 완료되었습니다.")
            else:
                print("PPT 내보내기 중 문제가 발생했습니다.")

        elif user_input == "quit":
            print("프로그램을 종료합니다.")
            automator.driver.quit()
            break

        else:
            print("유효한 명령이 아닙니다. 'start' 또는 'quit'을 입력해주세요.")
