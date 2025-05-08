import time
import platform
import os
import json
import shutil
import subprocess
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


def setup_selenium_driver(download_subdir: str, start_url: str):
    """
    Selenium WebDriver를 설정하고 Chrome 브라우저를 실행하는 공통 함수입니다.

    Args:
        download_subdir (str): 다운로드 파일을 저장할 하위 디렉토리 이름 (예: "videos", "pdfs").
        start_url (str): WebDriver가 처음 로드할 URL.

    Returns:
        webdriver.Chrome or None: 성공적으로 초기화된 WebDriver 인스턴스 또는 실패 시 None.
    """
    load_dotenv()

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir_relative = os.path.join(
        current_script_dir, "..", "data", "selenium-dev-profile"
    )
    selenium_user_data_dir = os.path.abspath(user_data_dir_relative)
    download_dir = os.path.abspath(
        os.path.join(current_script_dir, "..", "data", download_subdir)
    )

    preferences_path = os.path.join(selenium_user_data_dir, "Default", "Preferences")
    default_dir_path = os.path.join(selenium_user_data_dir, "Default")

    if not os.path.exists(default_dir_path):
        os.makedirs(default_dir_path)

    prefs_data = {}
    try:
        if os.path.exists(preferences_path):
            with open(preferences_path, "r", encoding="utf-8") as f:
                prefs_data = json.load(f)
        else:
            print(
                f"알림: Preferences 파일({preferences_path})이 존재하지 않아 새로 생성합니다."
            )

        if "download" not in prefs_data:
            prefs_data["download"] = {}
        prefs_data["download"]["default_directory"] = download_dir
        prefs_data["download"]["prompt_for_download"] = False
        prefs_data["download"]["directory_upgrade"] = True

        if "safebrowsing" not in prefs_data:
            prefs_data["safebrowsing"] = {}
        prefs_data["safebrowsing"]["enabled"] = False

        with open(preferences_path, "w", encoding="utf-8") as f:
            json.dump(prefs_data, f, indent=4)
        print(f"Preferences 파일 업데이트 완료: {preferences_path}")

    except json.JSONDecodeError:
        print(
            f"경고: Preferences 파일({preferences_path})이 유효한 JSON 형식이 아닙니다. 파일을 백업하고 새로 생성합니다."
        )
        try:
            shutil.move(preferences_path, preferences_path + ".bak")
            print(f"기존 Preferences 파일을 {preferences_path}.bak 으로 백업했습니다.")
            prefs_data = {
                "download": {
                    "default_directory": download_dir,
                    "prompt_for_download": False,
                    "directory_upgrade": True,
                },
                "safebrowsing": {"enabled": False},
            }
            with open(preferences_path, "w", encoding="utf-8") as f:
                json.dump(prefs_data, f, indent=4)
            print(f"새로운 Preferences 파일을 생성했습니다: {preferences_path}")
        except Exception as backup_err:
            print(
                f"Preferences 파일 처리 중 심각한 오류 발생 (백업/재생성 실패): {backup_err}"
            )
            return
    except Exception as e:
        print(f"Preferences 파일 처리 중 오류 발생: {e}")
        return
    if platform.system() == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else:
        chrome_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    if os.path.exists(chrome_path):
        subprocess.Popen(
            [
                chrome_path,
                "--remote-debugging-port=9222",
                f"--user-data-dir={selenium_user_data_dir}",
            ]
        )
        time.sleep(2)
    else:
        print("Chrome 브라우저를 찾을 수 없습니다. 수동으로 Chrome을 실행해주세요.")
        return

    _options = webdriver.ChromeOptions()

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

    driver = webdriver.Chrome(options=_options)

    driver.delete_all_cookies()

    # driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")

    driver.get(start_url)
    
    return driver
