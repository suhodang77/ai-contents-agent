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
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    NoSuchWindowException,
    WebDriverException,
)


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


def chrome_focuse(driver, max_retries=3, delay_between_retries=0.5):
    """
    Windows와 macOS에서 Selenium으로 제어 중인 Chrome 브라우저 창에 포커스를 맞추고
    화면 맨 앞으로 가져옵니다.

    Args:
        driver: 활성 Selenium WebDriver 인스턴스.
        max_retries (int): 포커싱 재시도 횟수.
        delay_between_retries (float): 재시도 간 대기 시간 (초).

    Returns:
        bool: 포커싱 성공 시 True, 실패 시 False.
    """
    if not driver:
        print("오류: 유효한 WebDriver 인스턴스가 제공되지 않았습니다.")
        return False

    system_os = platform.system()
    print(f"운영체제: {system_os}. Chrome 창 포커싱 시작...")

    for attempt in range(max_retries):
        print(f"포커싱 시도 #{attempt + 1}/{max_retries}")
        try:
            # 1. Selenium으로 현재 창 핸들 가져오기 및 JavaScript 포커스 시도
            current_handle = driver.current_window_handle
            driver.switch_to.window(current_handle)
            driver.execute_script("window.focus();")
            print("Selenium JavaScript window.focus() 실행됨.")
            time.sleep(0.2)  # JavaScript 적용 대기

            # 2. PyAutoGUI로 OS 수준에서 창 활성화
            # Chrome 창의 제목을 기반으로 찾습니다.
            # 페이지 제목이 자주 바뀌므로, "Google Chrome" 또는 브라우저 자체 이름으로 찾는 것이 더 일반적일 수 있습니다.
            # driver.title을 사용하여 현재 페이지 제목을 포함하는 창을 우선적으로 찾습니다.

            expected_title_part = driver.title  # 현재 탭의 제목
            browser_keyword = "Chrome"  # 일반적인 Chrome 브라우저 식별자
            if (
                "msedge" in driver.capabilities.get("browserName", "").lower()
            ):  # Edge 브라우저인 경우
                browser_keyword = "Microsoft Edge"

            target_window = None
            all_windows = pyautogui.getAllWindows()

            # 우선 현재 Selenium이 제어하는 탭의 제목과 일치하는 창을 찾음
            if expected_title_part:
                for window in all_windows:
                    if (
                        expected_title_part in window.title
                        and browser_keyword in window.title
                    ):
                        target_window = window
                        break

            # 위에서 못 찾았거나, expected_title_part가 없다면 browser_keyword로만 다시 찾음
            if not target_window:
                for window in all_windows:
                    if browser_keyword in window.title:
                        # 여러 Chrome/Edge 창이 있을 경우, 어떤 것이 Selenium 창인지 특정하기 어려움
                        # 여기서는 첫 번째 발견된 창을 사용 (개선 여지 있음)
                        target_window = window
                        print(
                            f"페이지 제목으로 정확히 일치하는 창을 못찾아 '{browser_keyword}' 키워드로 창 '{window.title}' 선택됨."
                        )
                        break

            if target_window:
                print(f"PyAutoGUI: 창 '{target_window.title}' 활성화 시도...")

                # 창 활성화 시도
                if system_os == "Darwin":  # macOS
                    # activate()는 macOS에서 항상 창을 맨 앞으로 가져오지 않을 수 있음
                    # AppleScript를 사용하는 것이 더 안정적일 수 있으나, 여기서는 pyautogui로 최대한 시도
                    try:
                        target_window.activate()
                        time.sleep(delay_between_retries / 2)
                        if (
                            not target_window.isActive
                        ):  # activate 후에도 활성화 안됐으면
                            # macOS에서는 minimize/maximize 트릭이 일반적이지 않음
                            # pyautogui.click(target_window.left + 10, target_window.top + 10) # 창 내부 클릭 시도
                            print(
                                f"macOS: '{target_window.title}' activate 시도 후, 활성 상태: {target_window.isActive}"
                            )
                    except Exception as e_mac_activate:
                        print(f"macOS activate 중 오류: {e_mac_activate}")
                        # AppleScript 대안을 고려할 수 있음 (별도 함수로 구현)
                        # activate_chrome_via_applescript(browser_keyword)

                elif system_os == "Windows":
                    try:
                        target_window.activate()
                        time.sleep(delay_between_retries / 2)
                        if (
                            not target_window.isActive
                        ):  # activate() 후에도 활성화 안됐으면
                            print(
                                f"Windows: '{target_window.title}' activate 후 비활성. 최소화/최대화 트릭 시도."
                            )
                            target_window.minimize()
                            time.sleep(0.1)
                            target_window.maximize()  # 또는 target_window.restore()
                            time.sleep(0.1)
                            target_window.activate()
                    except Exception as e_win_activate:
                        print(f"Windows activate/트릭 중 오류: {e_win_activate}")
                else:  # Linux 등 기타 OS
                    target_window.activate()  # 기본 activate 시도
                    time.sleep(delay_between_retries / 2)

                # 최종 확인 및 Selenium 재포커스
                time.sleep(0.3)  # OS가 창을 앞으로 가져올 시간
                active_after_pyautogui = pyautogui.getActiveWindow()
                if (
                    active_after_pyautogui
                    and target_window.title == active_after_pyautogui.title
                ):
                    print(f"PyAutoGUI: 창 '{target_window.title}' 성공적으로 활성화됨.")
                    # Selenium 컨텍스트 재확인
                    driver.switch_to.window(current_handle)
                    driver.execute_script(
                        "window.focus();"
                    )  # 한 번 더 JavaScript 포커스
                    return True
                else:
                    print(
                        f"PyAutoGUI: 창 활성화 확인 실패. 현재 활성 창: {active_after_pyautogui.title if active_after_pyautogui else '없음'}"
                    )

            else:
                print(
                    f"PyAutoGUI: 제목에 '{expected_title_part}' 또는 '{browser_keyword}'을 포함하는 Chrome/Edge 창을 찾지 못했습니다."
                )

        except NoSuchWindowException:
            print("오류: Selenium이 제어하는 브라우저 창이 닫혔거나 유효하지 않습니다.")
            return False  # WebDriver가 유효하지 않으면 더 이상 진행 불가
        except WebDriverException as wde:
            print(f"WebDriver 오류 발생: {wde}")
            # WebDriver 연결이 끊겼을 수 있음
            return False
        except Exception as e:
            print(f"포커싱 시도 중 예기치 않은 오류 발생: {e}")

        if attempt < max_retries - 1:
            print(f"{delay_between_retries}초 후 재시도...")
            time.sleep(delay_between_retries)
        else:
            print("최대 재시도 횟수 도달. Chrome 창 포커싱 최종 실패.")
            return False
    return False


def slider_drag(driver, slider_xpath, thumb_xpath, target_value):
    if element_click(driver, slider_xpath):
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
