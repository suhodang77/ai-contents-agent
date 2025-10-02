import time
import os
import pyautogui
import glob
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..utils.selenium_utils import (
    element_click,
    paste_text_to_element,
    press_tab_multiple_times,
    chrome_focuse,
)
from ..utils.selenium_setup import setup_selenium_driver


class GammaAutomator:
    def __init__(self, target_audience="일반인"):
        """
        GammaAutomator 클래스를 초기화합니다.
        """
        self.driver, self.chrome_browser_opened_by_script = setup_selenium_driver(
            download_subdir="results", start_url="https://gamma.app/create/paste"
        )
        if not self.driver:
            print("WebDriver 초기화 실패. GammaAutomator 인스턴스 생성 중단.")

        self.target_audience = target_audience

    def login(self):
        """
        사용자가 수동으로 Gamma.app에 로그인할 때까지 기다립니다.

        로그인이 성공적으로 감지되면 True를 반환하고, 시간 초과 또는 오류 발생 시
        WebDriver를 종료하고 False를 반환합니다.

        Returns:
            bool: 로그인 성공 여부.
        """
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div/form/div/div[1]/button",
                    )
                )
            )
            time.sleep(3)

            if self.chrome_browser_opened_by_script:
                chrome_focuse(self.driver)
                time.sleep(1)
            
            # --- 변경된 로그인 키 순서 ---
            # 1. 탭 7
            for _ in range(7):
                pyautogui.press("tab")
                time.sleep(0.7)

            # 2. 방향키 ↓ 3, 엔터
            for _ in range(3):  
                pyautogui.press("down")
                time.sleep(0.7)
            pyautogui.press("enter")
            time.sleep(0.7)
            
            # 3. 탭 3, 엔터
            for _ in range(3):
                pyautogui.press("tab")
                time.sleep(0.7)
            pyautogui.press("enter")

            return True
        except Exception as _:
            login_complete_indicator_xpath = (
                "/html/body/div[1]/div/div/div/div[1]/div[2]/div[1]/h2[1]"
            )
            try:
                WebDriverWait(self.driver, 300).until(
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
        """
        페이지 스타일을 설정하고, 주어진 스크립트를 Gamma의 콘텐츠 영역에 붙여넣은 후,
        '계속' 버튼을 클릭하여 다음 단계로 진행합니다.

        내부적으로 사용되는 헬퍼 메서드입니다.

        Args:
            script (str): PPT 생성을 위한 텍스트 스크립트.

        Returns:
            bool: 모든 단계가 성공적으로 완료되면 True, 아니면 False.
        """
        print("새로운 흐름에 따라 스크립트 생성 및 계속 진행을 시작합니다.")

        # 1. 페이지 스타일 드롭다운 클릭
        print("1. 페이지 스타일 드롭다운 클릭...")
        page_style_dropdown_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[1]/div/button[1]"
        if not element_click(self.driver, page_style_dropdown_xpath):
            print("페이지 스타일 드롭다운 클릭 실패")
            return False

        # 2. 드롭다운 메뉴 중 '일반적' 버튼 클릭
        print("2. '일반적' 버튼 클릭...")
        general_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/button"
        if not element_click(self.driver, general_button_xpath):
            print("XPath 기반 페이지 스타일 '일반적' 버튼 클릭 실패. 텍스트 기반으로 재시도...")
            try:
                # '일반적' 텍스트를 포함하는 버튼을 찾아서 클릭 (Fallback 로직)
                general_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., '일반적')]")
                    )
                )
                general_button.click()
                print("텍스트 기반 페이지 스타일 '일반적' 버튼 클릭 성공.")
            except Exception as e:
                print(f"텍스트 기반 페이지 스타일 '일반적' 버튼 클릭도 실패했습니다: {e}")
                return False

        # 3. 콘텐츠 영역 클릭 후 스크립트 붙여넣기
        print("3. 스크립트 붙여넣기...")
        content_area_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div[2]/div/div[1]/div/div/div[1]/div/div"
        if not paste_text_to_element(self.driver, content_area_xpath, script):
            print("스크립트 붙여넣기 실패")
            return False

        # 4. 옵션 버튼 클릭
        print("4. 옵션 버튼 클릭...")
        options_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div[2]/div/div[2]/div/div[3]"
        if not element_click(self.driver, options_button_xpath):
            print("옵션 버튼 클릭 실패")
            return False

        # 5. 계속 버튼 클릭
        print("5. 계속 버튼 클릭...")
        continue_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div[2]/div/button"
        if not element_click(self.driver, continue_button_xpath):
            print("계속 버튼 클릭 실패")
            return False

        print("모든 단계가 성공적으로 완료되었습니다.")
        return True

    def _configure_cards_and_continue(self):
        """
        '자유 형식'을 선택하고, 카드를 추가한 후 '계속' 버튼을 클릭하여
        다음 단계로 진행합니다.

        내부적으로 사용되는 헬퍼 메서드입니다.

        Returns:
            bool: 카드 설정 및 계속 진행 성공 여부.
        """
        print("2. 카드 설정 및 계속 (신규 흐름 적용)...")

        # XPath 변수 선언
        freestyle_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[3]/div/div/div[2]/div[1]/div[2]/button[1]"
        add_card_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[4]/div/div[2]/div/div[1]/button[3]"
        continue_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[4]/div/div[2]/div/div[2]/div/button"

        # 1. '자유 형식' 버튼 클릭
        print("1. '자유 형식' 버튼 클릭...")
        if not element_click(self.driver, freestyle_button_xpath):
            print("'자유 형식' 버튼 클릭 실패")
            return False

        # 2. 카드 추가 버튼 8번 클릭
        print("2. 카드 추가 버튼 클릭...")
        # 학습 대상자에 따라 카드 추가 횟수 결정 (PPT 분량 조절)
        if self.target_audience == "초등학생":
            card_clicks = 5  # 약 5분 분량
        elif self.target_audience == "중학생":
            card_clicks = 7  # 약 7분 분량
        else:  # 고등학생, 일반인
            card_clicks = 9  # 약 10분 분량

        print(f"학습 대상자({self.target_audience})에 맞춰 카드 {card_clicks}번 추가...")
        for i in range(card_clicks):
            if not element_click(self.driver, add_card_button_xpath):
                print(f"  시도 {i + 1}/{card_clicks}: 카드 추가 버튼 클릭 실패")
                return False
            print(f"  시도 {i + 1}/{card_clicks}: 카드 추가 버튼 클릭 성공.")

        if not element_click(self.driver, continue_button_xpath, timeout=30):
            print("PPT 생성 버튼 클릭 실패")
            return False
        print("생성 시작 버튼 클릭 완료.")
                
        return True

    def _select_template_and_generate(self):
        """
        템플릿 선택 단계를 가정하고 (현재는 수동 선택 대기) '생성' 버튼을 클릭하여
        PPT 생성을 시작합니다.

        내부적으로 사용되는 헬퍼 메서드입니다.
        (주의: 실제 템플릿 선택 로직은 필요시 추가 구현해야 합니다.)

        Returns:
            bool: 생성 시작 버튼 클릭 성공 여부.
        """
        # 현재 Gamma에서 템플릿을 따로 선택이 아닌 형식을 선택할 때 같이 템플릿을 선택하여 이 과정이 사라짐 따라서 _configure_cards_and_continue의 과정에 통합되었습니다.

        # print("3. 템플릿 선택 및 생성 시작...")
        # print("템플릿 선택 단계 (수동 또는 추가 로직 필요)")
        # time.sleep(5)

        # generate_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[2]/div/div/button" 
        # if not element_click(self.driver, continue_button_xpath, timeout=30):
        #     print("PPT 생성 버튼 클릭 실패")
        #     return False
        # print("생성 시작 버튼 클릭 완료.")
        # return True

    def _wait_for_generation(self):
        """
        Gamma의 PPT 생성이 완료될 때까지 대기합니다.

        특정 제목(h2) 요소가 나타나는 것을 기준으로 완료를 판단합니다.
        내부적으로 사용되는 헬퍼 메서드입니다.

        Returns:
            bool: PPT 생성 완료 감지 성공 여부 (시간 초과 시 False).
        """
        print("3. PPT 생성 완료 대기 중...")
        completion_indicator_xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/h2"

        try:
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.XPATH, completion_indicator_xpath))
            )
            print("PPT 생성 완료")
            time.sleep(2)
            return True
        except TimeoutError:
            print("PPT 생성 시간 초과")
            return False
        except Exception as e:
            print(f"생성 완료 대기 중 오류 발생: {e}")
            return False

    def _export_to_pdf(self):
        """
        생성된 Gamma 프레젠테이션을 PDF 파일로 내보내고,
        다운로드된 파일을 지정된 폴더로 이동시킵니다.
        """
        print("5. PDF로 내보내기 시작...")
        
        more_options_button_xpath = (
            "/html/body/div[1]/div/div/div/div/div[1]/div/div[2]/button"
        )
        if not element_click(self.driver, more_options_button_xpath):
            print("더보기 버튼 클릭 실패")
            return False

        export_button_xpath = "/html/body/div[157]/div/div/div[1]/button[6]"
        if not element_click(self.driver, export_button_xpath):
            try:
                export_button = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., '내보내기...')]")
                    )
                )
                export_button.click()
                time.sleep(1)
                print("내보내기 버튼 클릭 (텍스트 기반)")
            except Exception as e:
                print(f"내보내기 버튼 클릭 실패: {e}")
                return False

        export_pdf_button_xpath = (
            "/html/body/div[311]/div[3]/div/section/div/div[2]/div[2]/button[1]"
        )
        if not element_click(self.driver, export_pdf_button_xpath):
            try:
                export_pdf_button = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'PDF로 내보내기')]")
                    )
                )
                export_pdf_button.click()
                print("PDF로 내보내기 버튼 클릭 (텍스트 기반)")
            except Exception as e:
                print(f"PDF로 내보내기 버튼 클릭 실패: {e}")
                return False
        
        time.sleep(5)  # 다운로드가 시작될 시간을 줌
        
        # 다운로드 경로 설정
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        download_directory = os.path.join(current_file_dir, "..", "..", "data", "results")

        # 시스템의 기본 다운로드 폴더에서 가장 최근에 다운로드된 PDF 파일을 찾음
        downloads_folder = download_directory
        if not os.path.exists(downloads_folder):
            print("오류: 시스템의 다운로드 폴더를 찾을 수 없습니다.")
            return False
            
        initial_files = set(glob.glob(os.path.join(downloads_folder, '*.pdf')))
        
        # 새 PDF 파일이 다운로드 될 때까지 기다림
        new_file_path = None
        for _ in range(60): # 최대 60초 대기
            current_files = set(glob.glob(os.path.join(downloads_folder, '*.pdf')))
            new_files = current_files - initial_files
            if new_files:
                new_file_path = max(new_files, key=os.path.getctime)
                print(f"새 PDF 파일 감지: {new_file_path}")
                break
            time.sleep(1)
        
        if not new_file_path:
            print("오류: 지정된 시간 내에 새 PDF 파일이 다운로드되지 않았습니다.")
            return False
        
        # 다운로드된 파일을 원하는 폴더로 이동
        destination_path = os.path.join(download_directory, os.path.basename(new_file_path))
        shutil.move(new_file_path, destination_path)
        print(f"파일을 '{destination_path}'(으)로 성공적으로 이동했습니다.")

        return True

    def _wait_for_new_pdf_in_directory(self, directory_path, max_wait_time, polling_interval=5):
        # 이 함수는 더 이상 사용되지 않지만, 기존 로직을 유지하기 위해 남겨둠.
        # 실제 파일 이동은 _export_to_pdf에서 처리됨.
        print(
            f"'{directory_path}' 디렉토리에서 새 PDF 파일 생성을 {polling_interval}초 간격으로 확인합니다 (최대 {max_wait_time}초)..."
        )
        if not os.path.isdir(directory_path):
            print(
                f"오류: 지정된 다운로드 디렉토리 '{directory_path}'를 찾을 수 없습니다."
            )
            return False

        initial_pdf_files = {
            f for f in os.listdir(directory_path) if f.lower().endswith(".pdf")
        }
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            current_pdf_files = {
                f for f in os.listdir(directory_path) if f.lower().endswith(".pdf")
            }
            newly_added_pdfs = current_pdf_files - initial_pdf_files
            if newly_added_pdfs:
                print(f"새 PDF 파일 감지됨: {newly_added_pdfs}")
                print("PDF 생성 완료 확인됨.")
                return True
            elapsed_time = int(time.time() - start_time)
            if (elapsed_time % (polling_interval * 6) == 0):
                print(
                    f"  새 PDF 파일 대기 중... (경과 시간: {elapsed_time}초 / {max_wait_time}초, 현재 PDF 수: {len(current_pdf_files)})"
                )
            time_left = max_wait_time - (time.time() - start_time)
            if time_left <= 0:
                break
            actual_sleep = min(polling_interval, time_left)
            time.sleep(actual_sleep)
        print(
            f"오류: {max_wait_time}초 내에 '{directory_path}' 디렉토리에서 새 PDF 파일이 감지되지 않았습니다."
        )
        return False

    def create_ppt_from_script(self, script):
        """
        주어진 스크립트를 사용하여 전체 Gamma PPT 생성 및 PDF 내보내기 과정을 자동화합니다.

        Args:
            script (str): PPT 생성을 위한 텍스트 스크립트.
        """
        try:
            if not self._paste_script_and_continue(script):
                return
            if not self._configure_cards_and_continue():
                return
            if not self._wait_for_generation():
                return
            if not self._export_to_pdf():
                return
        except Exception as e:
            print(f"PPT 생성 및 내보내기 중 오류 발생: {e}")
        finally:
            print("자동화 작업 완료.")


if __name__ == "__main__":
    automator = GammaAutomator()
    automator.login()
    automator._paste_script_and_continue("test")
    automator._configure_cards_and_continue()