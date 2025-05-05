import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..utils.selenium_utils import element_click, paste_text_to_element
from ..utils.selenium_setup import setup_selenium_driver


class GammaAutomator:
    def __init__(self):
        # load_dotenv() # Moved to setup_selenium_driver

        self.driver = setup_selenium_driver(
            download_subdir="pdfs", start_url="https://gamma.app/create/paste"
        )
        if not self.driver:
            print("WebDriver 초기화 실패. GammaAutomator 인스턴스 생성 중단.")
            # Optionally raise an exception or handle the failure appropriately
            # raise RuntimeError("Failed to initialize WebDriver")

    def login(self):  # 수동 로그인
        print("=" * 50)
        print("Gamma.app 웹사이트가 열렸습니다.")
        print("수동으로 로그인을 진행해 주세요.")
        print("로그인 완료 및 다음 페이지 로딩을 기다립니다...")

        # 로그인 후 특정 요소가 나타날 때까지 대기
        login_complete_indicator_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[1]/h2[1]"  # 'Text to presentation' 헤더 또는 유사한 요소
        try:
            WebDriverWait(self.driver, 300).until(  # 5분 대기
                EC.presence_of_element_located(
                    (By.XPATH, login_complete_indicator_xpath)
                )
            )
            print("로그인 및 페이지 로딩 확인됨.")
            print("자동화 프로세스를 시작합니다.")
            print("=" * 50)
            return True
        except TimeoutError:
            print("로그인 시간 초과 또는 페이지 로딩 실패.")
            print("자동화 프로세스를 시작할 수 없습니다.")
            print("=" * 50)
            self.driver.quit()
            return False
        except Exception as e:
            print(f"로그인 확인 중 오류 발생: {e}")
            print("=" * 50)
            self.driver.quit()
            return False

    def _paste_script_and_continue(self, script):
        """스크립트를 붙여넣고 다음 단계로 진행합니다."""
        print("1. 스크립트 붙여넣기 및 계속...")
        # 1. 콘텐츠 영역 선택 후 스크립트 붙여넣기
        content_area_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div"
        if not paste_text_to_element(self.driver, content_area_xpath, script):
            print("스크립트 붙여넣기 실패")
            return False

        # 추가된 버튼 1 클릭
        additional_button_1_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div[2]/button"
        if not element_click(self.driver, additional_button_1_xpath):
            print("추가된 버튼 1 클릭 실패")
            return False

        # 추가된 버튼 2 클릭
        additional_button_2_xpath = "/html/body/div[5]/div[1]/div/div/button[2]"
        if not element_click(self.driver, additional_button_2_xpath):
            print("추가된 버튼 2 클릭 실패")
            return False

        # 2. 계속 버튼 누르기
        continue_button_1_xpath = (
            "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div/div[3]/button"
        )
        if not element_click(self.driver, continue_button_1_xpath):
            print("첫 번째 계속 버튼 클릭 실패")
            return False
        print("스크립트 붙여넣기 및 계속 완료.")
        return True

    def _configure_cards_and_continue(self):
        """카드 설정을 확인하고 다음 단계로 진행합니다."""
        print("2. 카드 설정 및 계속...")
        # 3. 카드 갯수 20장으로 맞추기 (XPath 수정 필요 가능성 있음)
        # Gamma UI 변경으로 XPath가 달라질 수 있습니다. 필요시 업데이트하세요.
        # 현재는 20장 버튼이 기본 선택 상태일 수 있어, 클릭 대신 확인 로직 추가 고려
        card_count_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[4]/div/div[2]/div/div[1]/button[3]"
        for i in range(8):
            element_click(self.driver, card_count_button_xpath)
        print("카드 갯수 설정 단계 (현재는 클릭 생략, 필요시 주석 해제)")
        time.sleep(2)  # 설정 확인을 위한 잠시 대기

        # 4. 계속 버튼 누르기
        continue_button_2_xpath = "/html/body/div[1]/div/div/div/div[1]/div[4]/div/div[2]/div/div[2]/div/button"
        if not element_click(self.driver, continue_button_2_xpath):
            print("두 번째 계속 버튼 클릭 실패")
            return False
        print("카드 설정 및 계속 완료.")
        return True

    def _select_template_and_generate(self):
        """템플릿 선택(가정) 후 생성을 시작합니다."""
        print("3. 템플릿 선택 및 생성 시작...")
        # 5. PPT 생성 버튼 누르기 (템플릿 선택 후 생성 버튼)
        # 템플릿 선택 단계가 있을 수 있습니다. 현재 코드는 템플릿 선택 후 바로 생성 버튼을 누르는 것을 가정합니다.
        # 실제로는 템플릿을 선택하는 로직이 필요할 수 있습니다.
        print("템플릿 선택 단계 (수동 또는 추가 로직 필요)")
        time.sleep(5)  # 템플릿 로딩 및 선택 대기

        generate_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[2]/div/div/button"
        if not element_click(
            self.driver, generate_button_xpath, timeout=30
        ):  # 생성 버튼은 로딩 시간이 길 수 있음
            print("PPT 생성 버튼 클릭 실패")
            return False
        print("생성 시작 버튼 클릭 완료.")
        return True

    def _wait_for_generation(self):
        """PPT 생성이 완료될 때까지 대기합니다. (특정 h2 요소 출현 기준)"""
        print("4. PPT 생성 완료 대기 중...")
        completion_indicator_xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/h2"  # 사용자 요청 XPath

        try:
            # 지정된 h2 요소가 나타날 때까지 대기
            WebDriverWait(self.driver, 300).until(  # 타임아웃 5분 (필요시 조절)
                EC.presence_of_element_located((By.XPATH, completion_indicator_xpath))
            )
            print("PPT 생성 완료")
            # 안정성을 위해 요소 확인 후 잠시 대기
            time.sleep(2)
            return True
        except TimeoutError:
            print("PPT 생성 시간 초과")
            return False
        except Exception as e:
            print(f"생성 완료 대기 중 오류 발생: {e}")
            return False

    def _export_to_pdf(self):
        """생성된 PPT를 PDF로 내보냅니다."""
        print("5. PDF로 내보내기 시작...")
        # 7. 더보기 버튼 누르기
        more_options_button_xpath = (
            "/html/body/div[1]/div/div/div/div/div[1]/div[2]/button"
        )
        if not element_click(self.driver, more_options_button_xpath):
            print("더보기 버튼 클릭 실패")
            return False

        # 8. 내보내기 버튼 누르기
        export_button_xpath = "/html/body/div[61]/div/div/div[1]/button[5]"  # 이 XPath는 동적으로 변할 수 있음
        if not element_click(self.driver, export_button_xpath):
            # XPath가 다를 경우 대비 (텍스트 기반으로 찾기 시도)
            try:
                export_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., '내보내기...')]")
                    )  # 텍스트 기반 탐색
                )
                export_button.click()
                time.sleep(1)
                print("내보내기 버튼 클릭 (텍스트 기반)")
            except Exception as e:
                print(f"내보내기 버튼 클릭 실패: {e}")
                return False

        # 9. PDF로 내보내기 버튼 누르기
        export_pdf_button_xpath = "/html/body/div[121]/div[3]/div/section/div/div[2]/div[2]/button[1]"  # 이 XPath는 동적으로 변할 수 있음
        if not element_click(self.driver, export_pdf_button_xpath):
            # XPath가 다를 경우 대비 (텍스트 기반으로 찾기 시도)
            try:
                export_pdf_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'PDF로 내보내기')]")
                    )  # 텍스트 기반 탐색
                )
                export_pdf_button.click()
                time.sleep(5)  # 다운로드 시작 대기
                print("PDF로 내보내기 버튼 클릭 (텍스트 기반)")
            except Exception as e:
                print(f"PDF로 내보내기 버튼 클릭 실패: {e}")
                return False

        print("PDF 내보내기 시작. 다운로드 폴더를 확인하세요.")
        # 다운로드 완료를 기다리는 로직 추가 가능 (예: 파일 존재 확인)
        time.sleep(30)  # 다운로드 시간 확보 (파일 크기에 따라 조절 필요)
        print("PDF 내보내기 완료.")
        return True

    def create_ppt_from_script(self, script):
        """
        스크립트를 입력받아 Gamma에서 PPT를 생성하고 PDF로 내보냅니다.

        Args:
            script (str): PPT 생성을 위한 스크립트 텍스트
        """
        try:
            if not self._paste_script_and_continue(script):
                return

            if not self._configure_cards_and_continue():
                return

            if not self._select_template_and_generate():
                return

            if not self._wait_for_generation():
                return

            if not self._export_to_pdf():
                return

        except Exception as e:
            print(f"PPT 생성 및 내보내기 중 오류 발생: {e}")
        finally:
            # 작업 완료 후 브라우저 종료 또는 유지 결정
            # self.driver.quit()
            print("자동화 작업 완료.")


if __name__ == "__main__":
    automator = GammaAutomator()
    if hasattr(automator, "driver"):  # driver 초기화 성공 시에만 실행
        # 예시 스크립트
        example_script = """
        # AI Contents Agent 개발

        ## 프로젝트 목표
        - 주어진 스크립트를 기반으로 자동으로 PPT 콘텐츠 생성
        - 다양한 AI 모델(Gamma, Tome 등) 연동 지원
        - 사용자 친화적인 인터페이스 제공

        ## 주요 기능
        1. 스크립트 입력 및 분석
        2. AI 모델 선택 및 API 연동
        3. PPT 생성 자동화 (Selenium 활용)
        4. 생성된 PPT 편집 및 관리
        5. 결과물 내보내기 (PDF, PPTX)

        ## 기술 스택
        - Python, Selenium, FastAPI
        - OpenAI API, Gamma/Tome 등
        - HTML/CSS/JavaScript (프론트엔드)

        ## 기대 효과
        - 콘텐츠 제작 시간 단축
        - 아이디어 구체화 및 시각화 지원
        - 반복 작업 자동화를 통한 생산성 향상
        """
        automator.login()
        automator.create_ppt_from_script(example_script)
        # 사용 후 드라이버 종료
        # automator.driver.quit()
    else:
        print("GammaAutomator 초기화 실패")
