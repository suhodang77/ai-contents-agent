import time
import platform
import os
import pyperclip
from dotenv import load_dotenv
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_utils import send_select_all_and_clear, element_click, paste_text_to_element


class FlikiVideoGenerator:
    def __init__(self):
        load_dotenv()

        self.driver = Driver(
            browser="chrome",  # 브라우저 종류 지정 (필수)
            uc=True,  # Undetected Chromedriver 모드 활성화
            headless=False,
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        )
        self.driver.delete_all_cookies()

        self.driver.get("https://app.fliki.ai/")

    def element_click(self, xpath, timeout=10):
        return element_click(self.driver, xpath, timeout)

    def paste_text_to_element(self, xpath, text_to_paste, timeout=10):
        return paste_text_to_element(self.driver, xpath, text_to_paste, timeout)

    def element_check(self, xpath):
        try:
            time.sleep(1)
            self.driver.find_element(By.XPATH, xpath)
            time.sleep(1)
            return False
        except Exception:
            return True

    def login(self):
        print("=" * 50)
        print("Fliki.ai 웹사이트가 열렸습니다.")
        print("수동으로 로그인을 진행해 주세요.")
        print("로그인이 완료되면 아래에 'start'를 입력하세요.")
        print("=" * 50)

        # 사용자 입력 대기
        user_input = ""
        while user_input.lower() != "start":
            user_input = input("로그인이 완료되었으면 'start'를 입력하세요: ")

            if user_input.lower() == "exit":
                self.driver.quit()
                return False

        print("자동화 프로세스를 시작합니다.")

        return True


if __name__ == "__main__":
    fliki_generator = FlikiVideoGenerator()

    fliki_generator.login()
