import platform
import time
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def send_select_all_and_clear(element):
    """
    요소의 모든 텍스트를 선택하고 삭제합니다.
    
    Args:
        element: Selenium WebElement
    """
    if platform.system() == "Darwin":  # macOS
        element.send_keys(Keys.COMMAND, "a")
    else:  # Windows, Linux
        element.send_keys(Keys.CONTROL, "a")

    element.send_keys(Keys.DELETE)


def element_click(driver, xpath, timeout=10):
    """
    XPath를 사용하여 요소가 로딩되었는지 확인하고, 요소를 클릭합니다.

    Args:
        driver: Selenium WebDriver 인스턴스
        xpath: 클릭할 요소의 XPath
        timeout: 대기 시간 (초), 기본값 10초
        
    Returns:
        bool: 클릭 성공 여부
    """
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


def paste_text_to_element(driver, xpath, text_to_paste, timeout=10):
    """
    XPath를 사용하여 요소가 로딩되었는지 확인하고,
    클립보드를 이용하여 텍스트를 붙여넣습니다.

    Args:
        driver: Selenium WebDriver 인스턴스
        xpath: 텍스트를 붙여넣을 요소의 XPath
        text_to_paste: 붙여넣을 텍스트 문자열
        timeout: 대기 시간 (초), 기본값 10초

    Returns:
        bool: 텍스트 붙여넣기 성공 여부
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        send_select_all_and_clear(element)

        pyperclip.copy(text_to_paste)  # 텍스트를 클립보드에 복사
        element.click()  # 요소에 focus
        if platform.system() == "Darwin":  # macOS
            element.send_keys(Keys.COMMAND, "v")
        else:  # Windows, Linux
            element.send_keys(Keys.CONTROL, "v")

        time.sleep(1)

        print(f"요소 '{xpath}'에 텍스트 붙여넣기 성공")
        return True

    except TimeoutError:
        print(f"요소 '{xpath}' 로딩 시간 초과")
        return False
    except Exception as e:
        print(f"요소 '{xpath}'에 텍스트 붙여넣기 중 오류 발생: {e}")
        return False 