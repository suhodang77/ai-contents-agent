import time
import os
import platform
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..utils.selenium_utils import (
    element_click,
    paste_text_to_element,
    press_shift_tab_multiple_times,
    press_enter,
    chrome_focuse,
)
from ..utils.selenium_setup import setup_selenium_driver


class GammaAutomator:
    def __init__(self):
        """
        GammaAutomator 클래스를 초기화합니다.

        Selenium WebDriver를 설정하고 Gamma 웹사이트의 '텍스트 붙여넣기' 페이지로 이동합니다.
        WebDriver 초기화에 실패하면 오류 메시지를 출력합니다.
        """
        self.driver, self.chrome_browser_opened_by_script = setup_selenium_driver(
            download_subdir="pdfs", start_url="https://gamma.app/create/paste"
        )
        if not self.driver:
            print("WebDriver 초기화 실패. GammaAutomator 인스턴스 생성 중단.")

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
                time.sleep(5)
                press_shift_tab_multiple_times(1)
                press_enter()
            else:
                press_shift_tab_multiple_times(9)
                if platform.system() == "Windows":
                    press_shift_tab_multiple_times(1)
                press_enter()
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
        주어진 스크립트를 Gamma의 콘텐츠 영역에 붙여넣고 '계속' 버튼을 클릭하여
        다음 단계로 진행합니다.

        내부적으로 사용되는 헬퍼 메서드입니다.

        Args:
            script (str): PPT 생성을 위한 텍스트 스크립트.

        Returns:
            bool: 스크립트 붙여넣기 및 계속 진행 성공 여부.
        """
        print("1. 스크립트 붙여넣기 및 계속...")
        content_area_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div"
        if not paste_text_to_element(self.driver, content_area_xpath, script):
            print("스크립트 붙여넣기 실패")
            return False

        page_style_dropdown_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div[2]/button"
        if not element_click(self.driver, page_style_dropdown_xpath):
            print("페이지 스타일 드롭다운 클릭 실패")
            return False

        general_button_xpath = "/html/body/div[5]/div[1]/div/div/button[2]"
        if not element_click(self.driver, general_button_xpath):
            print(
                "XPath 기반 페이지 스타일 '일반적' 버튼 클릭 실패. 텍스트 기반으로 재시도..."
            )
            try:
                # '일반적' 텍스트를 포함하는 버튼을 찾아서 클릭
                general_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., '일반적')]")
                    )
                )
                general_button.click()
                print("텍스트 기반 페이지 스타일 '일반적' 버튼 클릭 성공.")
            except Exception as e:
                print(f"텍스트 기반 페이지 스타일 '일반적' 버튼 클릭 실패: {e}")
                return False

        continue_button_1_xpath = (
            "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div/div/div[3]/button"
        )
        if not element_click(self.driver, continue_button_1_xpath):
            print("첫 번째 계속 버튼 클릭 실패")
            return False
        print("스크립트 붙여넣기 및 계속 완료.")
        return True

    def _configure_cards_and_continue(self):
        """
        카드 설정을 구성하고 (현재는 고정 로직) '계속' 버튼을 클릭하여
        다음 단계로 진행합니다.

        내부적으로 사용되는 헬퍼 메서드입니다.
        (주의: 카드 수 설정 로직은 UI 변경에 따라 수정이 필요할 수 있습니다.)

        Returns:
            bool: 카드 설정 및 계속 진행 성공 여부.
        """
        print("2. 카드 설정 및 계속...")
        card_count_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[4]/div/div[2]/div/div[1]/button[3]"

        print("카드 갯수 설정 시도 중...")
        clicked_successfully_count = 0
        time.sleep(10)
        for i in range(8):  # 최대 8번 클릭 시도
            try:
                # 요소가 존재하는지 짧은 시간(예: 2초) 동안 확인
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, card_count_button_xpath))
                )
                # 요소가 존재하면 클릭 시도
                if element_click(self.driver, card_count_button_xpath):
                    print(f"  시도 {i + 1}/8: 카드 카운트 버튼 클릭 성공.")
                    clicked_successfully_count += 1
                else:
                    print(f"  시도 {i + 1}/8: 카드 카운트 버튼은 존재하지만 클릭 실패.")
            except TimeoutException:
                print(
                    f"  시도 {i + 1}/8: 카드 카운트 버튼({card_count_button_xpath})을 찾을 수 없어 클릭을 건너뜁니다."
                )

        print(
            f"카드 갯수 설정 완료: 총 {clicked_successfully_count}번 성공적으로 클릭됨."
        )
        time.sleep(2)  # 기존 로직의 time.sleep(2) 유지

        continue_button_2_xpath = "/html/body/div[1]/div/div/div/div[1]/div[4]/div/div[2]/div/div[2]/div/button"
        if not element_click(self.driver, continue_button_2_xpath):
            print("두 번째 계속 버튼 클릭 실패")
            return False
        print("카드 설정 및 계속 완료.")
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
        print("3. 템플릿 선택 및 생성 시작...")
        print("템플릿 선택 단계 (수동 또는 추가 로직 필요)")
        time.sleep(5)

        generate_button_xpath = "/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[2]/div/div/button"
        if not element_click(self.driver, generate_button_xpath, timeout=30):
            print("PPT 생성 버튼 클릭 실패")
            return False
        print("생성 시작 버튼 클릭 완료.")
        return True

    def _wait_for_generation(self):
        """
        Gamma의 PPT 생성이 완료될 때까지 대기합니다.

        특정 제목(h2) 요소가 나타나는 것을 기준으로 완료를 판단합니다.
        내부적으로 사용되는 헬퍼 메서드입니다.

        Returns:
            bool: PPT 생성 완료 감지 성공 여부 (시간 초과 시 False).
        """
        print("4. PPT 생성 완료 대기 중...")
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
        생성된 Gamma 프레젠테이션을 PDF 파일로 내보냅니다.

        '더보기' 메뉴를 통해 내보내기 옵션을 선택하고 PDF 다운로드를 시작합니다.
        내부적으로 사용되는 헬퍼 메서드입니다.
        (주의: 메뉴 구조 변경 시 XPath 수정이 필요할 수 있습니다.)

        Returns:
            bool: PDF 내보내기 시작 성공 여부.
        """
        print("5. PDF로 내보내기 시작...")
        more_options_button_xpath = (
            "/html/body/div[1]/div/div/div/div/div[1]/div[2]/button"
        )
        if not element_click(self.driver, more_options_button_xpath):
            print("더보기 버튼 클릭 실패")
            return False

        export_button_xpath = "/html/body/div[61]/div/div/div[1]/button[5]"
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
            "/html/body/div[121]/div[3]/div/section/div/div[2]/div[2]/button[1]"
        )
        if not element_click(self.driver, export_pdf_button_xpath):
            try:
                export_pdf_button = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'PDF로 내보내기')]")
                    )
                )
                export_pdf_button.click()
                # time.sleep(5) # 기존 텍스트 기반 클릭 후 대기 시간 제거
                print("PDF로 내보내기 버튼 클릭 (텍스트 기반)")
            except Exception as e:
                print(f"PDF로 내보내기 버튼 클릭 실패: {e}")
                return False

        # PDF 내보내기 명령 후 상태 UI가 나타날 때까지 충분히 대기합니다.
        time.sleep(10)

        print("PDF 내보내기 시작. 다운로드 폴더를 확인하세요.")

        # PDF 생성 완료 상태를 기다립니다.
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        download_directory = os.path.join(current_file_dir, "..", "..", "data", "pdfs")
        max_wait_time_for_pdf = 3600  # PDF 생성 대기 시간 (초)

        if self._wait_for_new_pdf_in_directory(
            download_directory, max_wait_time_for_pdf
        ):
            print("추가 10초 대기 후 다음 작업을 진행합니다.")
            time.sleep(3)  # PDF 파일 시스템 반영 및 안정화 대기
            print("PDF 내보내기 완료.")
            return True
        else:
            return False

    def _wait_for_new_pdf_in_directory(
        self, directory_path, max_wait_time, polling_interval=5
    ):
        """
        지정된 디렉토리에 새 PDF 파일이 생성될 때까지 폴링합니다.

        Args:
            directory_path (str): 모니터링할 디렉토리 경로.
            max_wait_time (int): 최대 대기 시간 (초).
            polling_interval (int): 폴링 간격 (초).

        Returns:
            bool: 새 PDF 파일이 감지되면 True, 시간 초과 시 False.
        """
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
        print(
            f"  초기 PDF 파일 목록 (총 {len(initial_pdf_files)}개): {initial_pdf_files if initial_pdf_files else '없음'}"
        )

        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            current_pdf_files = {
                f for f in os.listdir(directory_path) if f.lower().endswith(".pdf")
            }
            newly_added_pdfs = current_pdf_files - initial_pdf_files

            if newly_added_pdfs:
                print(f"  새 PDF 파일 감지됨: {newly_added_pdfs}")
                print("PDF 생성 완료 확인됨.")
                return True

            # 진행 상황을 더 자주 로깅 (예: 매 30초 또는 폴링 인터벌의 배수)
            elapsed_time = int(time.time() - start_time)
            if (
                elapsed_time % (polling_interval * 6) == 0
            ):  # 약 30초마다 로깅 (polling_interval이 5일때)
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
        current_pdf_files_on_timeout = {
            f for f in os.listdir(directory_path) if f.lower().endswith(".pdf")
        }
        print(
            f"  시간 초과 시점 PDF 파일 목록 (총 {len(current_pdf_files_on_timeout)}개): {current_pdf_files_on_timeout if current_pdf_files_on_timeout else '없음'}"
        )
        print(
            "PDF 내보내기가 실패했거나 시간이 더 필요할 수 있습니다. Selenium 드라이버의 다운로드 경로 설정을 확인해주세요."
        )
        return False

    def create_ppt_from_script(self, script):
        """
        주어진 스크립트를 사용하여 전체 Gamma PPT 생성 및 PDF 내보내기 과정을 자동화합니다.

        스크립트 붙여넣기, 카드 설정, 생성 시작, 완료 대기, PDF 내보내기 단계를
        순차적으로 실행합니다.

        Args:
            script (str): PPT 생성을 위한 텍스트 스크립트.
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
            print("자동화 작업 완료.")


if __name__ == "__main__":
    automator = GammaAutomator()
    automator.login()