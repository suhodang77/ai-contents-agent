import time
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
    press_enter,
    slider_drag,
)
from ..utils.selenium_setup import setup_selenium_driver


class FlikiVideoGenerator:
    def __init__(self):
        """
        FlikiVideoGenerator 클래스를 초기화합니다.

        공통 Selenium WebDriver 설정을 로드하고 Fliki 웹사이트로 이동합니다.
        """
        self.driver = setup_selenium_driver(
            download_subdir="videos", start_url="https://app.fliki.ai/"
        )
        if not self.driver:
            print("WebDriver 초기화 실패. FlikiVideoGenerator 인스턴스 생성 중단.")

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
            chrome_focuse(self.driver)
            time.sleep(1)
            press_tab_multiple_times(1)
            press_enter()
            time.sleep(2)
            press_tab_multiple_times(2)
            press_enter()
            time.sleep(2)
            press_tab_multiple_times(7)
            press_enter()
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

    def _handle_upload_step(self, ppt_file_path, user_level_info):
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
        if not paste_text_to_element(
            self.driver, user_info_textarea_xpath, user_level_info
        ):
            print("경고: 사용자 정보 입력 실패. 계속 진행합니다.")
            
        slider_drag(
            driver=self.driver,
            slider_xpath="/html/body/div[2]/div/div[2]/div/div[2]/div/span/span[1]",
            thumb_xpath="/html/body/div[2]/div/div[2]/div/div[2]/div/span/span[2]/span",
            target_value=15,
        )

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
            WebDriverWait(self.driver, 120).until(
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
            WebDriverWait(self.driver, 240).until(
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
        비디오 생성이 완료될 때까지 기다린 후 생성된 비디오를 다운로드합니다.

        비디오 생성 오버레이가 사라질 때까지 최대 10분간 대기합니다.
        이후 여러 단계의 다운로드 버튼을 클릭하여 다운로드를 시작합니다.

        Returns:
            bool: 다운로드 프로세스 시작 성공 여부 (실제 파일 다운로드 완료 여부는 아님).
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
            print("다운로드 버튼 3 직접 시도...")
            download_button_3_xpath = "/html/body/div[3]/div/div/button[2]"
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, download_button_3_xpath))
                )
                if not element_click(self.driver, download_button_3_xpath):
                    print("오류: 다운로드 버튼 3 직접 클릭 실패.")
                    return False
                print("다운로드 버튼 3 직접 클릭 성공.")
                return self._wait_for_final_download_confirmation()
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

        download_button_3_xpath = "/html/body/div[3]/div/div/button[2]"
        print(f"다운로드 버튼 3 클릭 시도: {download_button_3_xpath}")
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, download_button_3_xpath))
            )
            if not element_click(self.driver, download_button_3_xpath):
                print("오류: 다운로드 버튼 3 클릭 실패.")
                return False
        except TimeoutException:
            print(
                f"오류: 다운로드 버튼 3({download_button_3_xpath})을 찾거나 클릭할 수 없음."
            )
            print("다운로드 버튼 3 없음. 최종 확인 단계로 이동 시도...")

        final_confirmation_button_xpath = "/html/body/div[2]/div/div[3]/button"
        print(
            f"최종 다운로드 확인 버튼 로딩 대기 및 클릭 시도: {final_confirmation_button_xpath}"
        )
        return self._wait_for_final_download_confirmation(
            final_confirmation_button_xpath
        )

    def _wait_for_final_download_confirmation(
        self, xpath="/html/body/div[2]/div/div[3]/button"
    ):
        """
        최종 다운로드 확인 버튼을 기다리고 클릭하는 헬퍼 함수입니다.

        지정된 XPath의 요소가 클릭 가능해질 때까지 최대 30초간 대기합니다.

        Args:
            xpath (str, optional): 클릭할 최종 확인 버튼의 XPath.
                                    Defaults to "/html/body/div[2]/div/div[3]/button".

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

    def generate_video_from_ppt(self, ppt_file_path, prompt):
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

        if not self._handle_upload_step(ppt_file_path, prompt):
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
    if generator.driver:
        if generator.login():
            print("로그인 성공")
            generator.generate_video_from_ppt(
                "data/pdfs/IT-Git.pdf", "영상 제작을 위한 프롬프트"
            )
    else:
        print("FlikiVideoGenerator 초기화 실패.")
