import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
import random

LOGIN_URL = "https://gamma.app/signin"
EMAIL = "suhodang77@gmail.com"
PASSWORD = "Tnghekd123!@#"
MAX_RETRIES = 3

def human_like_typing(element, text):
    """사람처럼 천천히 타이핑하는 효과를 줍니다."""
    for char in text:
        element.send_keys(char)
        # 0.1~0.3초 사이의 랜덤한 시간 동안 대기
        time.sleep(random.uniform(0.1, 0.3))

def try_login(driver, wait):
    try:
        # 이메일 입력
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        email_input.clear()
        print("[INFO] 이메일 입력 중...")
        human_like_typing(email_input, EMAIL)
        print("[INFO] 이메일 입력 완료")
        
        # 비밀번호 입력
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        password_input.clear()
        print("[INFO] 비밀번호 입력 중...")
        human_like_typing(password_input, PASSWORD)
        print("[INFO] 비밀번호 입력 완료")
        
        # 잠시 대기 후 로그인 버튼 클릭
        time.sleep(1)
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        print("[INFO] 로그인 버튼 클릭 완료")
        
        # 로그인 완료 대기
        time.sleep(5)
        print(f"[INFO] 로그인 후 URL: {driver.current_url}")
        
        # 로그인 성공 여부 확인 (URL이 변경되었는지)
        if "signin" not in driver.current_url:
            print("[INFO] 로그인 성공!")
            return True
        else:
            print("[WARNING] 로그인 실패 - URL이 변경되지 않음")
            return False
            
    except TimeoutException:
        print("[WARNING] 로그인 요소를 찾을 수 없음")
        return False
    except Exception as e:
        print(f"[WARNING] 로그인 중 오류 발생: {str(e)}")
        return False

def main():
    print("Chrome 브라우저 실행 중...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    try:
        print("Chrome 드라이버 초기화 중...")
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        print("Chrome 드라이버 초기화 성공!")
        
        print(f"[INFO] {LOGIN_URL} 로 이동 시도...")
        driver.get(LOGIN_URL)
        print(f"[INFO] 현재 URL: {driver.current_url}")
        
        # 페이지가 제대로 로드되지 않을 수 있으므로 새로고침
        print("[INFO] 페이지 새로고침 중...")
        driver.refresh()
        print(f"[INFO] 새로고침 후 URL: {driver.current_url}")
        
        # 로그인 시도 (최대 3번)
        wait = WebDriverWait(driver, 10)
        login_success = False
        for attempt in range(MAX_RETRIES):
            print(f"[INFO] 로그인 시도 {attempt + 1}/{MAX_RETRIES}")
            if try_login(driver, wait):
                login_success = True
                break
            else:
                if attempt < MAX_RETRIES - 1:  # 마지막 시도가 아니면
                    print("[INFO] 페이지 새로고침 후 재시도...")
                    driver.refresh()
                    time.sleep(3)  # 새로고침 후 잠시 대기
                else:
                    print("[ERROR] 최대 시도 횟수 초과")
        
        if login_success:
            print("\n[INFO] 브라우저를 계속 유지합니다.")
            print("[INFO] 브라우저를 종료하려면 아무 키나 누르세요...")
            input()  # 사용자 입력 대기
        
    except WebDriverException as e:
        print(f"[ERROR] Chrome 드라이버 연결 실패: {str(e)}")
        return
    except Exception as e:
        print(f"[ERROR] 예상치 못한 오류 발생: {str(e)}")
        return
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
