import time
import os
import pyautogui # pyautogui import 추가
import glob
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..utils.selenium_utils import (
    element_click,
    paste_text_to_element,
    upload_file_to_element,
    select_dropdown_option,
    chrome_focuse,
    press_tab_multiple_times,
    slider_drag,
)
from ..utils.selenium_setup import setup_selenium_driver


class FlikiVideoGenerator:
    BASE_SCRIP = """{target_audience}도 충분히 이해할 수 있도록 '{lecture_title}'이라는 개념을 쉽고 명확하게 설명하는 교육용 영상을 제작해줘.
설명은 너무 기술적이거나 전문적인 용어를 사용하지 말고, 일상생활에서 쉽게 접할 수 있는 상황이나 친숙한 예시를 활용해 설명해줘.
핵심 개념은 짧고 간결하게 정리하되, 아이들이 자연스럽게 흥미를 가질 수 있도록 이야기하듯 전달해줘.
영상은 다음과 같은 논리적 구조를 따라 구성해줘: 먼저, 강화학습이 필요한 상황이나 문제를 간단히 제시한 뒤, {lecture_title}의 정의를 {target_audience} 수준의 언어로 설명해줘.
이어서 1~2개의 쉬운 비유나 사례(예: 게임, 동물 훈련, 학습 보상 등)를 들어 {lecture_title}이 어떻게 작동하는지를 보여주고, 마지막에는 주요 내용을 요약하고 {lecture_title}이 어떤 분야에서 활용되는지도 간략히 언급해줘.
전체적으로 밝고 친근한 분위기로 구성해줘"""

    def __init__(self, **data):
        """
        FlikiVideoGenerator 클래스를 초기화합니다.

        공통 Selenium WebDriver 설정을 로드하고 Fliki 웹사이트로 이동합니다.
        """
        self.driver, self.chrome_browser_opened_by_script = setup_selenium_driver(
            download_subdir="results", start_url="https://app.fliki.ai/"
        )
        if not self.driver:
            print("WebDriver 초기화 실패. FlikiVideoGenerator 인스턴스 생성 중단.")

        self.target_audience = data.get("target_audience", "일반인")
        self.lecture_title = data.get("lecture_title", "강의 제목")

    def login(self):
        """
        사용자가 수동으로 Fliki.ai에 로그인할 때까지 기다립니다.

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
                        "/html/body/div/div[2]/div[2]/div/button",
                    )
                )
            )
            time.sleep(3)

            chrome_focuse(self.driver)
            time.sleep(5)

            # --- 변경된 로그인 키 순서 ---
            # 1. 탭 3, 엔터
            for _ in range(3):
                pyautogui.press("tab")
                time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(1)

            # 2. 방향키↓ 1, 엔터
            pyautogui.press("down")
            time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(1)

            # 3. 탭 1, 엔터
            pyautogui.press("tab")
            time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(3)

            # 4. 방향키↓ 2, 엔터
            for _ in range(2):
                pyautogui.press("down")
                time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(1)

            # 5. 탭 2, 엔터
            for _ in range(2):
                pyautogui.press("tab")
                time.sleep(0.2)
            pyautogui.press("enter")
            # --- 여기까지 변경 ---

            return True
        except Exception as _:
            login_complete_indicator_xpath = (
                "/html/body/div/main/div/div/div/div/div/div[1]/div/button[4]"
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

    def _handle_upload_step(self, ppt_file_path):
        """
        PPT 파일 업로드 및 초기 정보 입력 단계를 처리합니다.

        Args:
            ppt_file_path (str): 업로드할 PPT 파일의 경로.
            user_level_info (str): 사용자 수준 정보 프롬프트.

        Returns:
            bool: 업로드 단계 성공 여부.
        """
        print("[단계 1/5: 업로드]")
        ppt_button_xpath = (
            "/html/body/div/main/div/div/div/div/div/div[1]/div/button[4]"
        )
        print(f"PPT 버튼 클릭 시도: {ppt_button_xpath}")
        if not element_click(self.driver, ppt_button_xpath):
            print("오류: PPT 버튼 클릭 실패.")
            return False

        user_info_textarea_xpath = "/html/body/div[2]/div/div[2]/div/div[1]/textarea"
        print(f"사용자 정보 입력 시도: {user_info_textarea_xpath}")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, user_info_textarea_xpath))
            )
        except TimeoutException:
            print(
                f"오류: 사용자 정보 입력란({user_info_textarea_xpath})을 찾을 수 없습니다."
            )
            return False

        format_params = {
            "target_audience": self.target_audience,
            "lecture_title": self.lecture_title,
        }
        if not paste_text_to_element(
            self.driver,
            user_info_textarea_xpath,
            self.BASE_SCRIP.format(**format_params),
        ):
            print("경고: 사용자 정보 입력 실패. 계속 진행합니다.")

        print("슬라이더 드래그 시도...")
        slider_drag(
            driver=self.driver,
            slider_xpath="/html/body/div[2]/div/div[2]/div/div[2]/div/span/span[1]",
            thumb_xpath="/html/body/div[2]/div/div[2]/div/div[2]/div/span/span[2]/span",
            target_value=15,
        )
        print("슬라이더 드래그 완료.")

        file_input_xpath = "/html/body/div[2]/div/div[2]/div/div[3]/div/input"
        print("PPT 파일 업로드 시도...")
        if not upload_file_to_element(
            self.driver,
            trigger_xpath=None,
            file_input_xpath=file_input_xpath,
            file_path=ppt_file_path,
        ):
            print(f"업로드 실패 (input: {file_input_xpath}).")
            return False
        print("PPT 파일 업로드 요청 성공.")
        time.sleep(5)

        upload_next_button_xpath = "/html/body/div[2]/div/div[3]/div/div/button"
        print(f"Next 버튼 클릭 시도: {upload_next_button_xpath}")
        try:
            WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, upload_next_button_xpath))
            )
        except TimeoutException:
            print(
                f"오류: Next 버튼({upload_next_button_xpath})이 활성화되지 않거나 시간 초과."
            )
            return False
        if not element_click(self.driver, upload_next_button_xpath):
            print("오류: Next 버튼 클릭 실패.")
            return False

        print("업로드 단계 완료.")
        return True

    def _handle_template_step(self):
        """
        템플릿 선택 단계를 처리합니다 (건너뛰기).

        Returns:
            bool: 템플릿 건너뛰기 성공 여부.
        """
        print("[단계 2/5: 템플릿]")
        template_skip_button_xpath = "/html/body/div[2]/div/div[3]/div/div/button[2]"
        print(f"Skip 버튼 확인 및 클릭 시도: {template_skip_button_xpath}")
        try:
            WebDriverWait(self.driver, 600).until(
                EC.element_to_be_clickable((By.XPATH, template_skip_button_xpath))
            )
            print("'Skip' 버튼 확인됨. 클릭합니다.")
            if not element_click(self.driver, template_skip_button_xpath):
                print("오류: Skip 버튼 클릭 실패.")
                return False
        except TimeoutException:
            print(
                f"오류: Skip 버튼({template_skip_button_xpath})을 찾거나 클릭할 수 없음."
            )
            return False

        print("템플릿 단계 완료 (Skip).")
        return True

    def _handle_style_step(self):
        """
        언어 및 방언 선택 단계를 처리합니다 (건너뛰기).

        Returns:
            bool: 스타일 단계 건너뛰기 성공 여부.
        """
        print("[단계 3/5: 스타일]")
        language_select_xpath = "/html/body/div[2]/div/div[2]/div/div[1]/div[1]/select"
        print("언어 선택 (Korean) 시도...")
        if not select_dropdown_option(
            self.driver, language_select_xpath, option_text="Korean"
        ):
            print("오류: 언어(Korean) 선택 실패.")
            return False

        dialect_select_xpath = "/html/body/div[2]/div/div[2]/div/div[1]/div[2]/select"
        dialect_option_text = "Korea"
        print(f"말투 선택 ({dialect_option_text}) 시도...")
        if not select_dropdown_option(
            self.driver, dialect_select_xpath, option_text=dialect_option_text
        ):
            print(
                f"경고: 말투 '{dialect_option_text}' 선택 실패. 기본값으로 진행될 수 있음."
            )

        style_skip_button_xpath = "/html/body/div[2]/div/div[3]/div/div/button[2]"
        print(f"Skip 버튼 클릭 시도: {style_skip_button_xpath}")
        time.sleep(1)
        if not element_click(self.driver, style_skip_button_xpath):
            print("오류: 스타일 단계의 Skip 버튼 클릭 실패.")
            return False

        print("스타일 단계 완료 (Skip).")
        return True

    def _handle_script_step(self):
        """
        스크립트 검토 단계를 처리합니다 (다음).

        Returns:
            bool: 스크립트 단계 진행 성공 여부.
        """
        print("[단계 4/5: 스크립트]")
        script_next_button_xpath = "/html/body/div[2]/div/div[3]/div/div/button[3]"
        print(f"Next 버튼 확인 및 클릭 시도: {script_next_button_xpath}")
        try:
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, script_next_button_xpath))
            )
            print("'Next' 버튼 확인됨. 클릭합니다.")
            if not element_click(self.driver, script_next_button_xpath):
                print("오류: 스크립트 단계의 Next 버튼 클릭 실패.")
                return False
        except TimeoutException:
            print(
                f"오류: 스크립트 단계의 Next 버튼({script_next_button_xpath})을 찾거나 클릭할 수 없음."
            )
            return False

        print("스크립트 단계 완료 (Next).")
        return True

    def _handle_customization_step(self):
        """
        최종 사용자 정의 단계를 처리합니다 (제출).

        Returns:
            bool: 사용자 정의 단계 제출 성공 여부.
        """
        print("[단계 5/5: 사용자 정의]")
        submit_button_xpath = "/html/body/div[2]/div/div[3]/div/div/button[2]"
        print(f"Submit 버튼 확인 및 클릭 시도: {submit_button_xpath}")
        try:
            WebDriverWait(self.driver, 600).until(
                EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
            )
            print("'Submit' 버튼 확인됨. 클릭합니다.")
            if not element_click(self.driver, submit_button_xpath):
                print("오류: Submit 버튼 클릭 실패.")
                return False
        except TimeoutException:
            print(f"오류: Submit 버튼({submit_button_xpath})을 찾거나 클릭할 수 없음.")
            return False

        print("사용자 정의 단계 완료 (Submit).")
        return True

    def _wait_and_download_video(self):
        """
        비디오 생성이 완료될 때까지 기다린 후 생성된 비디오를 다운로드하고
        지정된 폴더로 이동시킵니다.
        """
        print("[다운로드 단계 시작]")

        generation_overlay_xpath = "/html/body/div[2]/div/div"
        print(
            f"비디오 생성 완료 대기 중... (오버레이 사라짐 감지: {generation_overlay_xpath})"
        )
        try:
            WebDriverWait(self.driver, 600).until(
                EC.invisibility_of_element_located((By.XPATH, generation_overlay_xpath))
            )
            print("비디오 생성 완료 감지됨.")
        except TimeoutException:
            print(
                f"오류: 비디오 생성 시간 초과 (10분). 오버레이({generation_overlay_xpath})가 사라지지 않았습니다."
            )
            return False
        except Exception as e:
            print(f"오류: 비디오 생성 대기 중 예상치 못한 오류 발생: {e}")
            return False

        time.sleep(3)

        download_button_1_xpath = "/html/body/div/main/div/div/div[1]/nav[2]/button[3]"
        print(f"다운로드 버튼 1 클릭 시도: {download_button_1_xpath}")
        if not element_click(self.driver, download_button_1_xpath):
            print("오류: 다운로드 버튼 1 클릭 실패.")
            print("페이지 새로고침 후 재시도...")
            self.driver.refresh()
            time.sleep(5)
            if not element_click(self.driver, download_button_1_xpath):
                print("오류: 새로고침 후에도 다운로드 버튼 1 클릭 실패.")
                return False
            print("새로고침 후 다운로드 버튼 1 클릭 성공.")

        download_button_2_xpath = "/html/body/div[2]/div/div[3]/button"
        print(f"다운로드 버튼 2 클릭 시도: {download_button_2_xpath}")
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, download_button_2_xpath))
            )
            if not element_click(self.driver, download_button_2_xpath):
                print("오류: 다운로드 버튼 2 클릭 실패.")
                return False
        except TimeoutException:
            print(
                f"오류: 다운로드 버튼 2({download_button_2_xpath})를 찾거나 클릭할 수 없음."
            )
        except Exception as e:
            print(f"오류: 다운로드 버튼 2({download_button_2_xpath}) 처리 중 예상치 못한 오류 발생: {e}")

        download_button_3_xpath = "/html/body/div[3]/div/div/button[2]"
        print(f"다운로드 버튼 3 클릭 시도: {download_button_3_xpath}")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, download_button_3_xpath))
            )
            if not element_click(self.driver, download_button_3_xpath):
                print("오류: 다운로드 버튼 3 직접 클릭 실패.")
                return False
            print("다운로드 버튼 3 직접 클릭 성공.")
        except TimeoutException:
            print(
                f"오류: 다운로드 버튼 3({download_button_3_xpath})도 직접 찾거나 클릭할 수 없음."
            )
            return False
        except Exception as e_direct3:
            print(
                f"오류: 다운로드 버튼 3 직접 클릭 중 예상치 못한 오류 발생: {e_direct3}"
            )
            return False

        final_confirmation_button_xpath = "/html/body/div[2]/div/div[3]/button[2]"
        print(
            f"최종 다운로드 확인 버튼 로딩 대기 및 클릭 시도: {final_confirmation_button_xpath}"
        )
        try:
            WebDriverWait(self.driver, 3600).until(
                EC.element_to_be_clickable((By.XPATH, final_confirmation_button_xpath))
            )
            print(f"최종 확인 버튼 ({final_confirmation_button_xpath}) 활성화됨. 클릭합니다.")
            if not element_click(self.driver, final_confirmation_button_xpath):
                print(
                    f"경고: 최종 확인 버튼 ({final_confirmation_button_xpath}) 클릭 실패. 이미 다운로드가 시작되었거나 요소가 사라졌을 수 있습니다."
                )
            else:
                print("최종 확인 버튼 클릭 완료.")
        except TimeoutException:
            print(
                f"오류: 최종 확인 버튼 ({final_confirmation_button_xpath})이 지정된 시간 내에 활성화되지 않음. 다운로드가 이미 시작되었거나 다른 문제가 발생했을 수 있습니다."
            )
        except Exception as e:
            print(f"오류: 최종 확인 버튼 ({final_confirmation_button_xpath}) 처리 중 예상치 못한 오류 발생: {e}")
        
        time.sleep(15)  # 다운로드가 완료될 시간을 줌

        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        download_directory = os.path.join(current_file_dir, "..", "..", "data", "results", "fliki_videos")
        
        # 다운로드 디렉토리 생성
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)

        # 시스템의 기본 다운로드 폴더에서 가장 최근에 다운로드된 동영상 파일을 찾음
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(downloads_folder):
            print("오류: 시스템의 다운로드 폴더를 찾을 수 없습니다.")
            return False
            
        initial_files = set(glob.glob(os.path.join(downloads_folder, '*.mp4')))
        
        new_file_path = None
        for _ in range(30):  # 최대 30초 대기
            current_files = set(glob.glob(os.path.join(downloads_folder, '*.mp4')))
            new_files = current_files - initial_files
            if new_files:
                new_file_path = max(new_files, key=os.path.getctime)
                print(f"새 동영상 파일 감지: {new_file_path}")
                break
            time.sleep(1)
        
        if not new_file_path:
            print("오류: 지정된 시간 내에 새 동영상 파일이 다운로드되지 않았습니다.")
            return False
        
        destination_path = os.path.join(download_directory, os.path.basename(new_file_path))
        shutil.move(new_file_path, destination_path)
        print(f"파일을 '{destination_path}'(으)로 성공적으로 이동했습니다.")
        
        return True
    
    def _wait_for_final_download_confirmation(
        self, xpath="/html/body/div[2]/div/div[3]/button[2]"
    ):
        """
        최종 다운로드 확인 버튼을 기다리고 클릭하는 헬퍼 함수입니다.

        지정된 XPath의 요소가 클릭 가능해질 때까지 최대 30초간 대기합니다.

        Args:
            xpath (str, optional): 클릭할 최종 확인 버튼의 XPath.
                                    Defaults to "/html/body/div[2]/div/div[3]/button[2]".

        Returns:
            bool: 최종 확인 버튼 클릭 (또는 자동 시작으로 인한 성공 추정) 여부.
        """
        try:
            WebDriverWait(self.driver, 3600).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            print(f"최종 확인 버튼 ({xpath}) 활성화됨. 클릭합니다.")
            if not element_click(self.driver, xpath):
                print(
                    f"경고: 최종 확인 버튼 ({xpath}) 클릭 실패. 이미 다운로드가 시작되었거나 요소가 사라졌을 수 있습니다."
                )
                print("다운로드가 시작되었는지 확인하세요.")
                return True
            print("최종 확인 버튼 클릭 완료.")
            print("다운로드가 시작되었는지 확인하세요.")
            return True
        except TimeoutException:
            print(
                f"오류: 최종 확인 버튼 ({xpath})이 지정된 시간 내에 활성화되지 않음. 다운로드가 이미 시작되었거나 다른 문제가 발생했을 수 있습니다."
            )
            print("다운로드가 자동으로 시작되었을 수 있습니다. 확인해주세요.")
            return True
        except Exception as e:
            print(f"오류: 최종 확인 버튼 ({xpath}) 처리 중 예상치 못한 오류 발생: {e}")
            return False
            
    def generate_video_from_ppt(self, ppt_file_path):
        """
        로그인된 Fliki.ai 세션에서 PPT 파일을 사용하여 비디오 생성 프로세스를 조율합니다.

        업로드, 템플릿, 스타일, 스크립트, 사용자 정의 단계를 순차적으로 실행하고,
        마지막으로 비디오 생성 대기 및 다운로드를 시작합니다.

        Args:
            ppt_file_path (str): 업로드할 PPT 파일의 경로.
            prompt (str, optional): 영상 제작을 위한 500자 이내의 프롬프트.

        Returns:
            bool: 전체 비디오 생성 및 다운로드 시작 프로세스의 성공 여부.
                다운로드 실패 시에도 생성 제출이 성공했다면 True를 반환할 수 있습니다.
        """
        if not self.driver:
            print("WebDriver가 초기화되지 않아 비디오 생성을 시작할 수 없습니다.")
            return False

        print(f"--- Fliki 비디오 생성 시작 (PPT: {ppt_file_path}) ---")

        if not self._handle_upload_step(ppt_file_path):
            print("비디오 생성 실패: 업로드 단계에서 오류 발생.")
            return False

        if not self._handle_template_step():
            print("비디오 생성 실패: 템플릿 단계에서 오류 발생.")
            return False

        if not self._handle_style_step():
            print("비디오 생성 실패: 스타일 단계에서 오류 발생.")
            return False

        if not self._handle_script_step():
            print("비디오 생성 실패: 스크립트 단계에서 오류 발생.")
            return False

        if not self._handle_customization_step():
            print("비디오 생성 실패: 사용자 정의 단계에서 오류 발생.")
            return False

        print("--- 비디오 생성 프로세스 성공적으로 제출 완료 ---")
        time.sleep(5)

        print("--- 비디오 생성 완료 대기 및 다운로드 시작 ---")
        if not self._wait_and_download_video():
            print("비디오 다운로드 실패.")
            return True
        else:
            print("--- 비디오 다운로드 프로세스 완료 --- ")

        return True


if __name__ == "__main__":
    generator = FlikiVideoGenerator()
    generator.login()