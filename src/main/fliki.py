import os
import time
import random
import platform
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class FlikiLogin:
    def __init__(self):
        # 환경 변수 로드
        load_dotenv()

        # Chrome 옵션 설정
        _options = webdriver.ChromeOptions()
        _options.add_argument("--disable-blink-features=AutomationControlled")
        _options.add_experimental_option("excludeSwitches", ["enable-automation"])
        _options.add_experimental_option("useAutomationExtension", False)

        # User-Agent 변경 (사람처럼 보이도록)
        _options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.165 Safari/537.36")

        self.driver = webdriver.Chrome(options=_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.delete_all_cookies()

        # Fliki 로그인 페이지로 이동
        self.driver.get("https://app.fliki.ai/welcome?login=")

    def send_select_all_and_clear(self, element):
        """ 입력 필드 전체 선택 후 삭제 """
        if platform.system() == "Darwin":  # macOS
            element.send_keys(Keys.COMMAND, "a")
        else:  # Windows, Linux
            element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)

    def type_text_slowly(self, element, text, min_delay=0.1, max_delay=0.3):
        """ 사람처럼 랜덤한 속도로 한 글자씩 입력 """
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))  # 랜덤 입력

    def enter_text(self, xpath, text, timeout=10):
        """ 특정 입력 필드에 랜덤 속도로 한 글자씩 입력 """
        driver = self.driver
        try:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.send_select_all_and_clear(element)
            self.type_text_slowly(element, text)
            return True
        except Exception as e:
            print(f"❌ 요소 '{xpath}' 입력 중 오류 발생: {e}")
            return False

    def element_click(self, xpath, timeout=10):
        """ 지정된 XPATH의 버튼을 클릭 """
        driver = self.driver
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            return True
        except Exception as e:
            print(f"❌ 버튼 '{xpath}' 클릭 중 오류 발생: {e}")
            return False

    def login(self):
        try:
            email = os.getenv("GOOGLE_EMAIL")
            password = os.getenv("GOOGLE_PASSWORD")

            if not email or not password:
                print("❌ Error: 환경 변수에 GOOGLE_EMAIL 또는 GOOGLE_PASSWORD가 설정되지 않았습니다.")
                return False

            # 로그인 버튼 클릭
            if self.element_click("/html/body/div/div[2]/div[2]/div/div[2]/button"):
                time.sleep(3)

                # 이메일 입력
                if self.enter_text("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[1]/input", email):
                    time.sleep(3)

                    # 'Cancel'과 '로그인' 버튼 -> 'Next' 버튼 랜덤 반복 (5~7회)
                    repeat_count = random.randint(5, 7)
                    for i in range(repeat_count):
                        print(f"🔄 Cancel 버튼 클릭 & 로그인 버튼 재클릭 ({i + 1}/{repeat_count})")

                        # 'Cancel' 버튼 클릭
                        if not self.element_click(
                                "/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/button[2]/span/span"):
                            print("❌ 'Cancel' 버튼 클릭 실패")
                            return False

                        time.sleep(random.uniform(5, 15))  # 랜덤 딜레이

                        # 로그인 버튼 다시 클릭
                        if not self.element_click("/html/body/div/div[2]/div[2]/div/div[2]/button"):
                            print("❌ 로그인 버튼 재클릭 실패")
                            return False

                        time.sleep(random.uniform(5, 15))  # 랜덤 딜레이

                        # 'Next' 버튼 클릭 후 딜레이 2초
                        if self.element_click("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/button[1]"):
                            time.sleep(2)

                        # 비밀번호 필드가 나타나면 반복 종료
                        if self.is_element_present("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/input"):
                            print("✅ 비밀번호 필드 감지, 우회 성공")
                            break

                    # 비밀번호 입력
                    if self.enter_text("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/input", password):
                        time.sleep(3)

                        # 'Submit' 버튼 클릭
                        if self.element_click("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[3]/button[1]"):
                            print("✅ 로그인 시도 중")
                            time.sleep(10)

                            # CAPTCHA 경고 처리 반복문
                            while self.driver.current_url != "https://app.fliki.ai/":
                                print("🔄 CAPTCHA 경고 처리 중")
                                # CAPTCHA 경고 버튼 클릭
                                if not self.element_click("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[3]/button[2]"):
                                    print("❌ CAPTCHA 경고 버튼 클릭 실패")
                                    return False

                                time.sleep(2)

                                # 'Next' 버튼 클릭
                                if not self.element_click("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/button[1]"):
                                    print("❌ 'Next' 버튼 클릭 실패")
                                    return False

                                time.sleep(2)

                                # 비밀번호 재입력
                                if not self.enter_text("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[2]/input", password):
                                    print("❌ 비밀번호 재입력 실패")
                                    return False

                                time.sleep(3)

                                # 'Submit' 버튼 클릭
                                if not self.element_click("/html/body/div/div[2]/div[2]/div/div[2]/div/form/div[3]/button[1]"):
                                    print("❌ 'Submit' 버튼 클릭 실패")
                                    return False

                                time.sleep(10)

                            print("✅ 로그인 성공")
                            return True
                        else:
                            print("❌ 'Submit' 버튼 클릭 실패")
                    else:
                        print("❌ 비밀번호 입력 실패")
                else:
                    print("❌ 이메일 입력 실패")
            else:
                print("❌ 로그인 버튼 클릭 실패")

        except Exception as e:
            print(f"❌ 로그인 중 오류 발생: {e}")
            return False

        return True

    def close(self):
        """ 브라우저 종료 """
        self.driver.quit()

    def is_element_present(self, xpath, timeout=3):
        """ 특정 요소가 존재하는지 확인 """
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except:
            return False


class FlikiPPTToVideo:
    def __init__(self, driver, auto_start=True):
        """
        FlikiPPTToVideo 클래스 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            auto_start: 자동 실행 여부 (기본값: True)
        """
        self.driver = driver
        self.status = {
            'ppt_button': False,
            'popup': False,
            'script_prompt': False,
            'file_upload': False,
            'video_settings': False,
            'script_generation': False,
            'video_download': False
        }
        
        if auto_start:
            try:
                self.execute_pipeline()
            except Exception as e:
                print(f"❌ 자동 실행 중 오류 발생: {e}")
                self._print_status()

    def execute_pipeline(self):
        """전체 PPT to Video 변환 파이프라인 실행"""
        print("🚀 PPT to Video 자동화 시작")
        
        pipeline_steps = [
            (self._click_ppt_to_video_button, 'ppt_button'),
            # (self._handle_popup, 'popup'),
            (self._enter_script_prompt, 'script_prompt'),
            (self._upload_ppt_file, 'file_upload'),
            (self._configure_video_settings, 'video_settings'),
            (self._generate_and_process_script, 'script_generation'),
            (self._download_video, 'video_download')
        ]

        for step_func, status_key in pipeline_steps:
            try:
                step_func()
                self.status[status_key] = True
                print(f"✅ {step_func.__doc__.strip()} 완료")
            except Exception as e:
                self.status[status_key] = False
                print(f"❌ {step_func.__doc__.strip()} 실패: {e}")
                self._print_status()
                raise

        print("✅ PPT to Video 전체 프로세스 완료!")
        self._print_status()
        return True

    def _print_status(self):
        """현재 실행 상태 출력"""
        print("\n📊 실행 상태:")
        for step, status in self.status.items():
            icon = "✅" if status else "❌"
            print(f"{icon} {step.replace('_', ' ').title()}")
        print()

    def _click_ppt_to_video_button(self):
        """1단계: PPT to Video 버튼 클릭"""
        try:
            if not self.element_click("/html/body/div/main/div/div/div/div/div/div[1]/div/button[4]"):
                raise Exception("PPT to Video 버튼 클릭 실패")
            time.sleep(2)
        except Exception as e:
            raise Exception(f"PPT to Video 버튼 클릭 중 오류: {e}")

    # def _handle_popup(self):
    #     """2단계: 팝업 창 처리"""
    #     try:
    #         if self.is_element_present('//*[@id="radix-:r20:"]'):
    #             self.element_click("/html/body/div/main/div/div/div/div/div/div[1]/div/button[4]")
    #             time.sleep(2)
    #     except Exception as e:
    #         raise Exception(f"팝업 창 처리 중 오류: {e}")

    def _enter_script_prompt(self):
        """3단계: 스크립트 프롬프트 입력"""
        try:
            ppt_prompt = "초보자도 이해할 수 있도록 '강화학습'을 간단명료하게 설명하는 60초 내외의 영상을 만들어줘. 핵심 개념을 짧고 명확하게 전달하고, 일상적인 비유나 쉬운 사례를 1~2개 사용해서 이해를 돕는 구성을 해줘. 전체 설명은 논리적 흐름(문제 제기 → 강화학습 정의 → 예시 → 마무리 요약)을 따라 진행해줘."
            if not self.enter_text('/html/body/div[2]/div/div[2]/div/div[1]/textarea', ppt_prompt):
                raise Exception("스크립트 프롬프트 입력 실패")
            if not self.element_click('/html/body/div[2]/div/div[2]/div/div[2]/div/span/span[1]'):
                # 슬라이더 요소 찾기
                slider = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div[2]/div/span/span[1]")

                # JavaScript를 사용하여 슬라이더 값 설정
                value = 50  # 설정하고자 하는 값
                self.driver.execute_script("arguments[0].value = arguments[1]", slider, value)

                # 슬라이더의 변경 사항을 반영
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", slider)
                raise Exception("영상 길이 설정 실패")

        except Exception as e:
            raise Exception(f"스크립트 프롬프트 입력 중 오류: {e}")

    def _upload_ppt_file(self):
        """4단계: PPT 파일 업로드"""
        try:
            file_input = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[3]/div/input')       
            file_input.send_keys("/Users/pc/Documents/PPTtoVIDEO/testVersion.pptx") # Mac 버전
            # file_input.send_keys("D:\\PPTtoVIDEO\\testVersion.pptx") # Windows 버전
            time.sleep(2)
            
            if not self.element_click('/html/body/div[2]/div/div[3]/div/div/button'):
                raise Exception("Next 버튼 클릭 실패")
            time.sleep(60)
            
            if not self.element_click('/html/body/div[2]/div/div[3]/div/div/button[2]'):
                raise Exception("Next 버튼 클릭 실패")
            time.sleep(2)
        except Exception as e:
            raise Exception(f"파일 업로드 중 오류: {e}")

    def _configure_video_settings(self):
        """5-6단계: 비디오 설정 구성"""
        try:
            # 언어 설정
            language_dropdown = Select(self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[1]/div[1]/select'))
            language_dropdown.select_by_visible_text("Korean")
            time.sleep(1)

            # 톤, 목적, 대상 설정
            settings = [
                ('/html/body/div[2]/div/div[2]/div/div[2]/div/button[2]', 'Informative 톤'),
                ('/html/body/div[2]/div/div[2]/div/div[3]/div/button[4]', 'Educational 톤'),
                ('/html/body/div[2]/div/div[2]/div/div[4]/div/button[2]', 'Other 대상')
            ]
            
            for xpath, setting_name in settings:
                if not self.element_click(xpath):
                    raise Exception(f"{setting_name} 설정 실패")

            # if not self.enter_text('/html/body/div[2]/div/div[2]/div/div[4]/div[2]/input', "Beginner"):
            #     raise Exception("대상 입력 실패")
            # time.sleep(1)
            
            
        except Exception as e:
            raise Exception(f"비디오 설정 구성 중 오류: {e}")

    def _generate_and_process_script(self):
        """7-9단계: 스크립트 생성 및 처리"""
        try:
            if not self.element_click('/html/body/div[2]/div/div[3]/div/div/button[2]'):
                raise Exception("Next 버튼 클릭 실패")
            time.sleep(30)

            if not self.element_click('/html/body/div[2]/div/div[3]/div/div/button[3]'):
                raise Exception("스크립트 생성 버튼 클릭 실패")
            time.sleep(2)
            
            if not self.element_click('/html/body/div[2]/div/div[2]/div/div/div/button[3]'):
                raise Exception("AI 아바타 생성 버튼 클릭 실패")
            time.sleep(2)
            
            if not self.element_click('/html/body/div[2]/div/div[3]/div/div/button[2]'):
                raise Exception("Submit 버튼 클릭 실패")
            time.sleep(90)
        except Exception as e:
            raise Exception(f"스크립트 생성 및 처리 중 오류: {e}")

    def _download_video(self):
        """10-11단계: 비디오 다운로드"""
        try:
            if not self.element_click('/html/body/div/main/div/div/div[1]/nav[2]/button[3]'):
                raise Exception("Download 버튼 클릭 실패")

            if not self.element_click('/html/body/div[2]/div/div[3]/button'):
                raise Exception("Start export 버튼 클릭 실패")
            
            if not self.element_click('/html/body/div[3]/div/div/button[2]'):
                raise Exception("Export 확인 버튼 클릭 실패")
            
            time.sleep(15)
            
            if not self.element_click('/html/body/div[2]/div/div[3]/button'):
                raise Exception("최종 다운로드 버튼 클릭 실패")
        except Exception as e:
            raise Exception(f"비디오 다운로드 중 오류: {e}")

    def is_element_present(self, xpath, timeout=3):
        """ 특정 요소가 존재하는지 확인 """
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except:
            return False

    def element_click(self, xpath, timeout=10):
        """ 지정된 XPATH의 버튼을 클릭 """
        driver = self.driver
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            return True
        except Exception as e:
            print(f"❌ 버튼 '{xpath}' 클릭 중 오류 발생: {e}")
            return False

    def enter_text(self, xpath, text, timeout=10):
        """ 특정 입력 필드에 랜덤 속도로 한 글자씩 입력 """
        driver = self.driver
        try:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.send_select_all_and_clear(element)
            element.send_keys(text)
            # self.type_text_slowly(element, text)
            return True
        except Exception as e:
            print(f"❌ 요소 '{xpath}' 입력 중 오류 발생: {e}")
            return False

    def send_select_all_and_clear(self, element):
        """ 입력 필드 전체 선택 후 삭제 """
        if platform.system() == "Darwin":  # macOS
            element.send_keys(Keys.COMMAND, "a")
        else:  # Windows, Linux
            element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)

    # def type_text_slowly(self, element, text, min_delay=0.1, max_delay=0.5):
    #     """ 사람처럼 랜덤한 속도로 한 글자씩 입력 """
    #     for char in text:
    #         element.send_keys(char)
    #         time.sleep(random.uniform(min_delay, max_delay))  # 랜덤 입력