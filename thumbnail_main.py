import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException
import time
import random
import os
from dotenv import load_dotenv
import re
import webbrowser
import threading
import traceback

# .env 파일에서 환경 변수 로드
load_dotenv(override=True)

class ChatGPTAutomator:
    def __init__(self, headless=True):
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        if headless:
            options.add_argument("--headless=new")
        # 사용자 데이터 디렉토리 설정 (선택 사항: 이미 로그인된 프로필 사용하려면 주석 해제)
        # user_data_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome')  # macOS
        # options.add_argument(f"--user-data-dir={user_data_dir}")  
        # options.add_argument("--profile-directory=Default")  # 프로필명 (Default 또는 Profile 1, 2 등)
        self.driver = uc.Chrome(options=options, use_subprocess=True)
        self.wait = WebDriverWait(self.driver, 20)

    def wait_and_find_element(self, by, selector, timeout=10):
        """요소를 찾고 클릭 가능할 때까지 대기하는 함수"""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            self.wait.until(EC.element_to_be_clickable((by, selector)))
            return element
        except Exception as e:
            print(f"요소를 찾을 수 없거나 클릭할 수 없습니다 ({selector}): {str(e)}")
            return None

    def check_and_switch_to_frame(self):
        """iframe이 있는지 확인하고 있다면 전환하는 함수"""
        try:
            # iframe 존재 여부 확인 및 전환
            iframe = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            self.driver.switch_to.frame(iframe)
            print("iframe으로 전환했습니다.")
            return True
        except:
            print("iframe이 발견되지 않았습니다. 메인 프레임에서 계속합니다.")
            return False

    # --- iframe까지 모두 순회해서 input[type="email"]을 찾는 함수 ---
    def find_email_input_in_all_frames(self):
        # 메인 프레임부터 시작
        self.driver.switch_to.default_content()
        email_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="email"]')
        if email_fields:
            return email_fields[0]
        # 모든 iframe 순회
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                self.driver.switch_to.frame(iframe)
                email_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="email"]')
                if email_fields:
                    return email_fields[0]
                self.driver.switch_to.default_content()
            except Exception:
                self.driver.switch_to.default_content()
                continue
        self.driver.switch_to.default_content()
        return None

    # --- polling 방식으로 모든 프레임에서 이메일 입력 시도 ---
    def robust_email_input_polling_all_frames(self, email, max_wait=15):
        start = time.time()
        while time.time() - start < max_wait:
            email_field = self.find_email_input_in_all_frames()
            if email_field:
                try:
                    email_field.clear()
                except Exception:
                    pass
                try:
                    email_field.click()
                except Exception:
                    pass
                try:
                    email_field.send_keys(email)
                except Exception:
                    self.driver.execute_script("arguments[0].value = arguments[1];", email_field, email)
                val = self.driver.execute_script("return arguments[0].value;", email_field)
                if val == email:
                    print("이메일 입력 성공 (all frames)")
                    return True
            time.sleep(0.5)
        print("이메일 입력 실패 (all frames)")
        return False

    def click_google_next_button_with_delay(self, delay=3, max_wait=30):
        start = time.time()
        while time.time() - start < max_wait:
            if "accounts.google.com" in self.driver.current_url:
                print(f"구글 로그인 페이지 감지됨, {delay}초 대기 후 '다음' 버튼 클릭 시도")
                time.sleep(delay)
                try:
                    next_div = self.wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
                    try:
                        next_div.click()
                    except ElementClickInterceptedException:
                        print("div 클릭 실패, JS로 강제 클릭 시도")
                        self.driver.execute_script("arguments[0].click();", next_div)
                    print("구글 '다음' 버튼(div#identifierNext) 클릭 성공")
                    return True
                except Exception as e:
                    print(f"div#identifierNext 클릭 실패: {e}")
                    try:
                        next_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="LgbsSe"]')))
                        try:
                            next_btn.click()
                        except ElementClickInterceptedException:
                            print("버튼 클릭 실패, JS로 강제 클릭 시도")
                            self.driver.execute_script("arguments[0].click();", next_btn)
                        print("구글 '다음' 버튼(button[jsname]) 클릭 성공")
                        return True
                    except Exception as e2:
                        print(f"버튼 클릭도 실패: {e2}")
            time.sleep(0.5)
        print("구글 '다음' 버튼 클릭 실패")
        return False

    def input_google_password_if_needed(self, max_wait=30):
        password = os.getenv("PASSWORD")
        start = time.time()
        while time.time() - start < max_wait:
            try:
                pw_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
                if pw_input.is_displayed() and pw_input.is_enabled():
                    if password:
                        pw_input.clear()
                        pw_input.send_keys(password)
                        print("구글 비밀번호 자동 입력 완료 (name 무관)")
                    else:
                        print(".env에 PASSWORD 값이 없어 비밀번호 입력을 스킵합니다.")
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        print("비밀번호 입력창을 찾지 못했습니다.")
        return False

    def click_google_password_next_button(self, delay=1, max_wait=30):
        start = time.time()
        while time.time() - start < max_wait:
            if "accounts.google.com" in self.driver.current_url:
                print(f"구글 비밀번호 '다음' 버튼 클릭 시도")
                time.sleep(delay)
                try:
                    pw_next_div = self.wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
                    try:
                        pw_next_div.click()
                    except ElementClickInterceptedException:
                        print("비밀번호 div 클릭 실패, JS로 강제 클릭 시도")
                        self.driver.execute_script("arguments[0].click();", pw_next_div)
                    print("구글 비밀번호 '다음' 버튼(div#passwordNext) 클릭 성공")
                    return True
                except Exception as e:
                    print(f"div#passwordNext 클릭 실패: {e}")
                    try:
                        next_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="LgbsSe"]')))
                        try:
                            next_btn.click()
                        except ElementClickInterceptedException:
                            print("비밀번호 버튼 클릭 실패, JS로 강제 클릭 시도")
                            self.driver.execute_script("arguments[0].click();", next_btn)
                        print("구글 비밀번호 '다음' 버튼(button[jsname]) 클릭 성공")
                        return True
                    except Exception as e2:
                        print(f"비밀번호 버튼 클릭도 실패: {e2}")
            time.sleep(0.5)
        print("구글 비밀번호 '다음' 버튼 클릭 실패")
        return False

    def url_watcher(self, poll_interval=0.5):
        last_url = None
        while True:
            try:
                cur_url = self.driver.current_url
            except Exception:
                break  # 드라이버 종료 시
            if cur_url != last_url:
                print(f"[URL Watcher] URL 변경 감지: {cur_url}")
                last_url = cur_url
            time.sleep(poll_interval)

    def automate(self):
        try:
            self.driver.get("https://chatgpt.com/")
            print("ChatGPT 페이지를 열었습니다.")
            login_button = self.wait_and_find_element(By.CSS_SELECTOR, 'button.btn.relative.btn-primary.btn-large.w-full')
            if login_button:
                time.sleep(random.uniform(1, 2))
                login_button.click()
                print("첫 페이지 로그인 버튼 클릭 성공")
                print("로그인 페이지로 이동 대기 중...")
                self.wait.until(EC.url_contains("auth.openai.com/log-in"))
                print("로그인 페이지로 이동 완료")
                time.sleep(3)
                self.check_and_switch_to_frame()
                email = os.getenv("EMAIL")
                print(f"불러온 EMAIL 값: {email}")
                if email:
                    if self.robust_email_input_polling_all_frames(email):
                        print("robust_email_input_polling_all_frames 함수 정상 동작")
                        try:
                            continue_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type=\"submit\"]')))
                            continue_button.click()
                            print("계속 버튼 클릭 성공")
                        except Exception as e:
                            print(f"계속 버튼 클릭 실패: {e}")
                        max_wait = 60
                        start = time.time()
                        while time.time() - start < max_wait:
                            if "accounts.google.com" in self.driver.current_url:
                                self.click_google_next_button_with_delay(delay=3)
                                if self.input_google_password_if_needed():
                                    self.click_google_password_next_button()
                                break
                            time.sleep(0.5)
                    else:
                        print("robust_email_input_polling_all_frames 함수에서 이메일 입력에 실패했습니다.")
                else:
                    print("EMAIL 환경 변수를 찾을 수 없습니다.")
            else:
                print("첫 페이지 로그인 버튼을 찾을 수 없습니다.")
            main_url_detected = False
            poll_start = time.time()
            while time.time() - poll_start < 120:
                if self.driver.current_url.startswith("https://chatgpt.com"):
                    main_url_detected = True
                    break
                time.sleep(1)
            if main_url_detected:
                prompt = """
아래와 같은 조건으로 썸네일용 이미지를 생성하려고 합니다. 별도의 질문/답변 없이 바로 생성해주세요.

### **기본 정보**

- **대상**: {초등학교 5학년 또는 중학교 2학년}
- **차시**: {6차시}
- **강의명**: {인공지능이란 무엇일까?}
- **교수명**: {정병철 교수님}
- **난이도**: {1}
- **썸네일 비율**: 16:9
- **스타일**: 교육용 2D 심플 스타일, 밝고 친근한 색감
- **분위기**: 명랑하고 학습에 동기부여를 주는 분위기

---

### **텍스트 레이아웃 및 정확도 요구사항**

### **텍스트 구성**

텍스트는 다음과 같은 4개의 고정된 문구를 **줄 단위로 정확히 표시**해야 하며, 오타 없이 명확하게 인식 가능해야 합니다:

1. **X차시**
2. **강의명**
3. **교수명**
4. 오른쪽 상단의 작은 텍스트: **Lv{숫자}**
- **모든 텍스트는 정확히 해당 문자열로 출력되어야 하며**, '레벌', '레벨:', '차시:' 등으로 잘못 출력되면 안 됩니다.
- **텍스트는 가독성 높은 고딕체 또는 산세리프 스타일의 한국어 글꼴로 출력**되어야 하며, 외계어처럼 깨지거나 잘려보이지 않아야 합니다.
- **텍스트는 이미지 내에 벡터처럼 또렷하고 선명하게 렌더링**되어야 합니다.
- `{숫자}` 는 강의의 레벨 숫자가 들어올 것입니다.
- *"컴푸터적" ⇒ "컴퓨터적"**으로 오타 수정해서 생성해주셔야 합니다.

---

### **텍스트 위치 및 비율**

- 텍스트 블록은 왼쪽 정렬되며, **화면의 왼쪽 10~15% 안쪽 영역**에 배치
- 세로 위치는 **왼쪽 세로 중앙보다 약간 위쪽** (상단에서 20% 정도 아래 위치)
- 텍스트 간 줄 간격은 일정하게 유지되며, 겹치지 않음

**텍스트 크기 비율 예시:**

- **강의명**: 기준 크기 100% (가장 큼), 텍스트 두꺼운 두께
- **X차시, 교수명**: 약 60~70% 크기, 텍스트 얇은 두께
- **Lv{숫자}**: 가장 작고 고정 위치, 약 20% 크기, 박스 형태로 배경색 존재, 텍스트 얇은 두께

---

### **오른쪽 일러스트 요소 조건 (🆕 개선 핵심)**

- **오른쪽 일러스트는 반드시 썸네일 너비의 35% 이내 영역에만 배치**
- **오른쪽 이미지가 중앙이나 왼쪽으로 넘어오지 않도록 강력히 제한**
- **일러스트의 개수는 1개로 제한** (2개 이상 사용 금지)
- **Lv{숫자} 텍스트와 겹치지 않도록** 오른쪽 상단 여백 확보
- 주제에 맞는 심플한 요소 사용

---

### **배경 및 색상 조건**

- 배경은 강의명과 어울리는 **단색 배경**
- 텍스트 색상은 대비가 잘 되는 색

---

### **기타**

- 썸네일에 들어가는 이미지 요소는 중복이 되면 안됩니다. 들어가는 주제가 비슷하더라도 다르게 나와야 하며, 일러스트의 제스쳐 또한 매번 다르게 나와야 합니다.
    """
                prompt_html = ''.join(f'<p>{line}</p>' for line in prompt.strip().split('\n'))
                prompt_box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ProseMirror')))
                self.driver.execute_script("arguments[0].innerHTML = arguments[1];", prompt_box, prompt_html)
                prompt_box.click()
                send_btn = self.wait.until(EC.element_to_be_clickable((By.ID, 'composer-submit-button')))
                send_btn.click()
                print("프롬프트 자동 입력 및 전송 완료 (p태그+전송버튼)")
                print("썸네일 생성 중입니다. 잠시만 기다려주세요...")
                max_wait = 600
                interval = 2
                img_src = None
                start = time.time()
                while time.time() - start < max_wait:
                    try:
                        img = self.driver.find_element(By.CSS_SELECTOR, 'img[alt="생성된 이미지"]')
                        img_src = img.get_attribute('src')
                        if img_src:
                            print("이미지 URL:", img_src)
                            with open("generated_image_url.txt", "w") as f:
                                f.write(img_src)
                            # headless 환경에서는 webbrowser.open_new_tab이 무의미하므로, headless 아닐 때만 실행
                            if not self.driver.capabilities.get('goog:chromeOptions', {}).get('args', []) or not any('headless' in arg for arg in self.driver.capabilities.get('goog:chromeOptions', {}).get('args', [])):
                                webbrowser.open_new_tab(img_src)
                            print("이미지 새 탭으로 자동 오픈 완료 (사용자 브라우저)")
                            break
                    except Exception:
                        pass
                    time.sleep(interval)
                if not img_src:
                    print("이미지 자동 오픈 실패: 시간 내에 이미지를 찾지 못했습니다.")
            else:
                print("chatgpt.com 메인 페이지로 돌아오지 않았습니다.")
            url_thread = threading.Thread(target=self.url_watcher, daemon=True)
            url_thread.start()
            input("작업을 마친 후 Enter 키를 누르면 브라우저가 종료됩니다...")
        except Exception as e:
            print("자동화 도중 예외 발생:")
            print(traceback.format_exc())
        finally:
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                    print("브라우저를 종료했습니다.")
                except Exception:
                    pass

if __name__ == "__main__":
    automator = ChatGPTAutomator(headless=False)
    automator.automate()