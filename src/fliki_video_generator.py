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

    def send_select_all_and_clear(self, element):
        if platform.system() == "Darwin":  # macOS
            element.send_keys(Keys.COMMAND, "a")
        else:  # Windows, Linux
            element.send_keys(Keys.CONTROL, "a")

        element.send_keys(Keys.DELETE)

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
            time.sleep(1)
            return True

        except Exception as e:
            print(f"요소 {xpath} 클릭 중 오류 발생: {e}")
            return False

    def paste_text_to_element(self, xpath, text_to_paste, timeout=10):
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

    def element_check(self, xpath):
        try:
            time.sleep(1)
            self.driver.find_element(By.XPATH, xpath)
            time.sleep(1)
            return False
        except Exception:
            return True

    def email_pass(self, id, prev_step_button):
        email_form_xpath = (
            "/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[1]/input"
        )
        next_button_xpath = (
            "/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/button[1]"
        )
        email_cancel_button_xpath = (
            "/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/button[2]"
        )

        if self.paste_text_to_element(
            email_form_xpath,
            id,
        ):
            while True:
                if self.element_click(next_button_xpath):
                    if self.element_check(next_button_xpath):
                        break
                    self.element_click(email_cancel_button_xpath)
                    self.element_click(prev_step_button)

        return next_button_xpath

    def password_pass(self, id, pw, prev_step_button):
        password_form_xpath = (
            "/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/input"
        )
        submit_button_xpath = (
            "/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[3]/button[1]"
        )
        password_cancel_button_xpath = (
            "/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[3]/button[2]"
        )

        while True:
            if self.paste_text_to_element(
                password_form_xpath,
                pw,
            ):
                if self.element_click(submit_button_xpath):
                    if self.element_check(submit_button_xpath):
                        break
                    self.element_click(password_cancel_button_xpath)
                    self.email_pass(id, prev_step_button)

    def login(self):
        try:
            fliki_id = os.getenv("FLIKI_ID")
            fliki_pw = os.getenv("FLIKI_PW")

            if not fliki_id or not fliki_pw:
                print("Error: 환경변수에 FLIKI_ID 또는 FLIKI_PW가 설정되지 않았습니다.")
                return False

            continue_email_button_xpath = (
                "/html/body/div/div[2]/div[2]/div/div[2]/button"
            )

            if self.element_click(continue_email_button_xpath):
                pass

            self.email_pass(fliki_id, continue_email_button_xpath)
            self.password_pass(fliki_id, fliki_pw, continue_email_button_xpath)

        except Exception as e:
            print(f"login 함수 에러 발생: {e}")
            return False

        return True  # 로그인 시도 성공


if __name__ == "__main__":
    fliki_generator = FlikiVideoGenerator()

    fliki_generator.login()
