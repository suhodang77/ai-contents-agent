import os
import platform
import time
import pyautogui
import pyperclip
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def send_select_all_and_clear(element):
    """
    Selenium WebElement의 모든 텍스트를 선택하고 삭제합니다.

    Args:
        element: 텍스트를 지울 Selenium WebElement.
    """
    if platform.system() == "Darwin":
        element.send_keys(Keys.COMMAND, "a")
    else:
        element.send_keys(Keys.CONTROL, "a")

    element.send_keys(Keys.DELETE)


def element_click(driver, xpath, timeout=10):
    """
    지정된 XPath를 사용하여 웹 요소를 찾아 클릭합니다.

    요소가 클릭 가능해질 때까지 지정된 시간(timeout) 동안 기다립니다.

    Args:
        driver: Selenium WebDriver 인스턴스.
        xpath (str): 클릭할 요소의 XPath.
        timeout (int, optional): 요소를 기다릴 최대 시간(초). 기본값은 10.

    Returns:
        bool: 클릭에 성공하면 True, 그렇지 않으면 False.
    """
    sleep_time = 1
    try:
        time.sleep(sleep_time)
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        element.click()
        time.sleep(sleep_time)
        return True

    except Exception as e:
        print(f"요소 {xpath} 클릭 중 오류 발생: {e}")
        return False


def paste_text_to_element(driver, xpath, text_to_paste, timeout=10):
    """
    지정된 XPath를 사용하여 웹 요소에 텍스트를 붙여넣습니다.

    요소를 찾은 후, 기존 내용을 지우고 클립보드를 통해 새 텍스트를 붙여넣습니다.

    Args:
        driver: Selenium WebDriver 인스턴스.
        xpath (str): 텍스트를 붙여넣을 요소의 XPath.
        text_to_paste (str): 붙여넣을 텍스트.
        timeout (int, optional): 요소를 기다릴 최대 시간(초). 기본값은 10.

    Returns:
        bool: 텍스트 붙여넣기에 성공하면 True, 그렇지 않으면 False.
    """
    sleep_time = 1
    try:
        time.sleep(sleep_time)
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        send_select_all_and_clear(element)

        pyperclip.copy(text_to_paste)
        element.click()
        if platform.system() == "Darwin":
            element.send_keys(Keys.COMMAND, "v")
        else:
            element.send_keys(Keys.CONTROL, "v")

        time.sleep(sleep_time)

        print(f"요소 '{xpath}'에 텍스트 붙여넣기 성공")
        return True

    except TimeoutError:
        print(f"요소 '{xpath}' 로딩 시간 초과")
        return False
    except Exception as e:
        print(f"요소 '{xpath}'에 텍스트 붙여넣기 중 오류 발생: {e}")
        return False


def upload_file_to_element(
    driver, trigger_xpath, file_input_xpath, file_path, timeout=15
):
    """
    파일 업로드를 처리합니다. 필요한 경우 트리거 요소를 클릭한 후,
    지정된 파일 입력 요소(<input type="file">)를 사용하여 파일을 업로드합니다.

    Args:
        driver: Selenium WebDriver 인스턴스.
        trigger_xpath (str | None): 파일 입력을 표시하기 위해 클릭해야 할 요소의 XPath.
                                    없으면 None.
        file_input_xpath (str): 파일 경로를 받을 <input type="file"> 요소의 XPath.
        file_path (str): 업로드할 파일의 절대 또는 상대 경로.
        timeout (int, optional): 요소를 기다릴 최대 시간(초). 기본값은 15.

    Returns:
        bool: 파일 경로 전송에 성공하면 True, 그렇지 않으면 False.
            (실제 업로드 완료가 아닌 경로 전송 성공 여부)
    """
    try:
        abs_file_path = os.path.abspath(file_path)
        if not os.path.exists(abs_file_path):
            print(f"Error: File not found at {abs_file_path}")
            return False
        print(f"Attempting to upload file: {abs_file_path}")

        if trigger_xpath:
            print(f"Clicking trigger element: {trigger_xpath}")
            if not element_click(driver, trigger_xpath, timeout=timeout):
                print(
                    f"Warning: Failed to click trigger element {trigger_xpath}, attempting upload anyway."
                )
            time.sleep(1)

        print(f"Locating file input element: {file_input_xpath}")
        file_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, file_input_xpath))
        )
        print("File input element located. Sending file path...")
        file_input.send_keys(abs_file_path)
        print(f"File path '{abs_file_path}' sent to input element.")
        time.sleep(2)
        return True
    except TimeoutException:
        print(f"Error: File input element not found or timed out: {file_input_xpath}")
        return False
    except Exception as e:
        print(f"Error uploading file using input {file_input_xpath}: {e}")
        return False


def select_dropdown_option(
    driver, select_xpath, option_text=None, value=None, index=None, timeout=10
):
    """
    드롭다운(<select> 요소)에서 옵션을 선택합니다.

    옵션 텍스트, 값 또는 인덱스 중 하나를 기준으로 선택할 수 있습니다.

    Args:
        driver: Selenium WebDriver 인스턴스.
        select_xpath (str): <select> 요소의 XPath.
        option_text (str, optional): 선택할 옵션의 보이는 텍스트.
        value (str, optional): 선택할 옵션의 value 속성 값.
        index (int, optional): 선택할 옵션의 인덱스.
        timeout (int, optional): 요소를 기다릴 최대 시간(초). 기본값은 10.

    Returns:
        bool: 옵션 선택에 성공하면 True, 그렇지 않으면 False.
    """
    try:
        print(f"Attempting to select option in dropdown: {select_xpath}")
        select_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, select_xpath))
        )
        select = Select(select_element)

        selected = False
        if option_text is not None:
            print(f"Selecting by visible text: '{option_text}'")
            select.select_by_visible_text(option_text)
            selected = True
        elif value is not None:
            print(f"Selecting by value: '{value}'")
            select.select_by_value(value)
            selected = True
        elif index is not None:
            print(f"Selecting by index: {index}")
            select.select_by_index(index)
            selected = True
        else:
            print("Error: No selection criteria (text, value, or index) provided.")
            return False

        print("Dropdown option selected successfully.")
        time.sleep(1)
        return selected

    except TimeoutException:
        print(f"Error: Dropdown element not found or timed out: {select_xpath}")
        return False
    except NoSuchElementException:
        criteria_str = (
            f"text='{option_text}'"
            if option_text
            else f"value='{value}'"
            if value
            else f"index='{index}'"
        )
        print(
            f"Error: Option not found in dropdown {select_xpath} (Criteria: {criteria_str})"
        )
        try:
            options = [
                f"'{opt.text}' (value='{opt.get_attribute('value')}')"
                for opt in select.options
            ]
            print(f"Available options: {options}")
        except Exception as debug_e:
            print(f"Could not retrieve available options: {debug_e}")
        return False
    except Exception as e:
        print(f"Error selecting dropdown {select_xpath}: {e}")
        return False


def press_tab_multiple_times(count):
    """Press the Tab key multiple times using pyautogui."""
    print(f"Tab 키를 {count}번 누릅니다.")
    for _ in range(count):
        pyautogui.press("tab")
        time.sleep(random.randrange(1, 5) / 10)


def press_shift_tab_multiple_times(count):
    """Press the Shift + Tab key multiple times using pyautogui."""
    print(f"Shift + Tab 키를 {count}번 누릅니다.")
    for _ in range(count):
        try:
            pyautogui.keyDown("shift")
            pyautogui.press("tab")
            pyautogui.keyUp("shift")
            time.sleep(random.randrange(1, 5) / 10)

        except Exception as e:
            print(f"Shift+Tab 실행 중 오류 발생: {e}")
            pyautogui.keyUp("shift")


def press_enter():
    """Press the Enter key using pyautogui."""
    print("Enter 키를 누릅니다.")
    pyautogui.press("enter")


def chrome_focuse(driver):
    main_window_handle = driver.current_window_handle

    # Chrome 창으로 포커스 맞추기
    try:
        print("Chrome 창으로 포커스 시도 (JavaScript)...")
        driver.switch_to.window(
            main_window_handle
        )  # Selenium에게 해당 창을 다시 인지시킴
        driver.execute_script("window.focus();")  # JavaScript로 브라우저 창 포커스
        # 추가적으로 창을 앞으로 가져오는 JavaScript (항상 작동하지 않을 수 있음)
        # driver.execute_script("window.open('','_self').close(); window.focus();") # 약간의 트릭
        print("포커스 시도 완료.")
        time.sleep(1)  # 포커스가 실제로 적용될 시간
    except Exception as e:
        print(f"JavaScript로 포커스 맞추기 실패: {e}")

def slider_drag(driver, slider_xpath, thumb_xpath, target_value):
    if element_click(
        driver, slider_xpath
    ):
        print("트랙 클릭 성공 또는 시도됨.")
        time.sleep(0.5)

        try:
            wait = WebDriverWait(driver, 10)
            thumb_element = wait.until(
                EC.presence_of_element_located((By.XPATH, thumb_xpath))
            )
            track_element = wait.until(
                EC.presence_of_element_located((By.XPATH, slider_xpath))
            )
            print("슬라이더 핸들 및 트랙 요소 찾음.")

            current_value = float(thumb_element.get_attribute("aria-valuenow"))
            min_value = float(thumb_element.get_attribute("aria-valuemin"))
            max_value = float(thumb_element.get_attribute("aria-valuemax"))
            print(f"현재 값: {current_value}, 최소값: {min_value}, 최대값: {max_value}")

            if not (min_value <= target_value <= max_value):
                print(
                    f"경고: 목표 값 {target_value}이 유효 범위 [{min_value}-{max_value}]를 벗어납니다. 값을 조정합니다."
                )
                target_value = max(min_value, min(target_value, max_value))
                print(f"조정된 목표 값: {target_value}")

            track_width = track_element.size["width"]
            if track_width == 0:
                print(
                    "오류: 슬라이더 트랙의 너비가 0입니다. 요소를 잘못 찾았거나 숨겨져 있을 수 있습니다."
                )

            value_range = max_value - min_value
            if value_range == 0:
                print("경고: 슬라이더의 최소값과 최대값이 동일합니다.")
                offset_percentage = 0
            else:
                offset_percentage = (target_value - min_value) / value_range

            current_offset_percentage = (
                (current_value - min_value) / value_range if value_range != 0 else 0
            )
            current_x_pixels = current_offset_percentage * track_width

            target_x_pixels = offset_percentage * track_width
            x_offset = target_x_pixels - current_x_pixels

            print(f"트랙 너비: {track_width}px")
            print(f"목표 값 비율: {offset_percentage:.2f}")
            print(f"현재 핸들 X 위치 (추정): {current_x_pixels:.2f}px")
            print(f"목표 핸들 X 위치 (추정): {target_x_pixels:.2f}px")
            print(f"이동할 X 오프셋: {x_offset:.2f}px")

            actions = ActionChains(driver)
            actions.click_and_hold(thumb_element).move_by_offset(
                int(round(x_offset)), 0
            ).release().perform()

            print(f"슬라이더 값을 {target_value}(으)로 설정 시도 완료.")
            time.sleep(1)

            updated_value = float(thumb_element.get_attribute("aria-valuenow"))
            print(f"변경 후 실제 값 (aria-valuenow): {updated_value}")
            if abs(updated_value - target_value) < 0.5:
                print("슬라이더 값 설정 성공적으로 확인됨.")
            else:
                print(
                    f"경고: 슬라이더 값이 정확히 설정되지 않았을 수 있습니다. (목표: {target_value}, 실제: {updated_value})"
                )

        except Exception as e:
            print(f"슬라이더 조작 중 오류 발생: {e}")