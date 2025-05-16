import os
import time
import glob
from .modules.lilys_summarizer import LilysSummarizer
from .modules.gemini_responder import GeminiResponder
from .modules.gamma_automator import GammaAutomator
from .modules.fliki_video_generator import FlikiVideoGenerator

DATA_DIR = "data"
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
VIDEO_DIR = os.path.join(DATA_DIR, "videos")


def ensure_dir(directory):
    """지정된 디렉토리가 존재하지 않으면 생성합니다."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_latest_file(directory, extension):
    """지정된 디렉토리에서 가장 최근에 수정된 특정 확장자 파일을 찾습니다."""
    list_of_files = glob.glob(os.path.join(directory, f"*.{extension}"))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file


def main():
    print("AI 콘텐츠 생성 에이전트를 시작합니다.")

    # 0. 필요 디렉토리 생성
    ensure_dir(DATA_DIR)
    ensure_dir(PDF_DIR)
    ensure_dir(VIDEO_DIR)
    print(f"데이터 디렉토리 확인: {DATA_DIR}, {PDF_DIR}, {VIDEO_DIR}")

    # 1. 동영상 URL 입력 받기
    youtube_url = input("요약할 YouTube 동영상 URL을 입력하세요: ")
    if not youtube_url:
        print("URL이 입력되지 않았습니다. 프로그램을 종료합니다.")
        return

    # 2. LilysSummarizer로 스크립트 추출
    print("\n--- 2. YouTube 동영상 스크립트 추출 시작 ---")
    try:
        summarizer = LilysSummarizer()
        summary_result = summarizer.summarize_youtube_video(youtube_url)
        if "error" in summary_result:
            print(f"스크립트 추출 실패: {summary_result['error']}")
            return
        original_script = summary_result.get("summary")
        if not original_script:
            print("스크립트를 추출하지 못했습니다.")
            return
        print("스크립트 추출 완료.")
        # print(f"추출된 스크립트: \n{original_script[:500]}...") # 너무 길어서 일부만 출력
    except Exception as e:
        print(f"LilysSummarizer 처리 중 오류 발생: {e}")
        return

    # 3. GeminiResponder로 새로운 동영상 스크립트 생성
    print("\n--- 3. 새로운 동영상 스크립트 생성 시작 ---")
    try:
        responder = GeminiResponder()
        new_script = responder.generate_response(original_script)
        if not new_script:
            print("새로운 스크립트를 생성하지 못했습니다.")
            return
        print("새로운 동영상 스크립트 생성 완료.")
        # print(f"생성된 새 스크립트: \n{new_script[:500]}...") # 너무 길어서 일부만 출력
    except Exception as e:
        print(f"GeminiResponder 처리 중 오류 발생: {e}")
        return

    # 4. GammaAutomator로 PPT 생성
    print("\n--- 4. Gamma를 사용하여 PPT 생성 시작 ---")
    ppt_file_path = None
    try:
        gamma_automator = GammaAutomator()
        if not gamma_automator.driver:
            print(
                "GammaAutomator WebDriver 초기화 실패. PPT 생성을 진행할 수 없습니다."
            )
            return

        if gamma_automator.login():
            print("Gamma 로그인 성공. PPT 생성을 시작합니다.")
            gamma_automator.create_ppt_from_script(new_script)
            print("PPT 생성 프로세스 완료. PDF 파일 다운로드를 기다립니다...")
            # PDF 파일이 다운로드될 시간을 충분히 줍니다.
            # GammaAutomator의 _export_to_pdf에 time.sleep(30)이 이미 존재합니다.
            # 추가 대기 시간이 필요하다면 여기에 추가할 수 있습니다.
            # time.sleep(10) # 예시: 추가 10초 대기

            ppt_file_path = get_latest_file(PDF_DIR, "pdf")
            if ppt_file_path:
                print(f"생성된 PPT (PDF) 파일: {ppt_file_path}")
            else:
                print(f"{PDF_DIR} 에서 생성된 PDF 파일을 찾을 수 없습니다.")
                print("Fliki 동영상 생성을 진행할 수 없습니다.")
                return
        else:
            print("Gamma 로그인 실패. PPT 생성을 진행할 수 없습니다.")
            return
    except Exception as e:
        print(f"GammaAutomator 처리 중 오류 발생: {e}")
        return
    finally:
        if hasattr(gamma_automator, "driver") and gamma_automator.driver:
            gamma_automator.driver.quit()
            print("Gamma WebDriver 종료됨.")

    # 5. FlikiVideoGenerator로 동영상 생성
    if ppt_file_path:
        print("\n--- 5. Fliki를 사용하여 동영상 생성 시작 ---")
        try:
            fliki_generator = FlikiVideoGenerator()
            if not fliki_generator.driver:
                print(
                    "FlikiVideoGenerator WebDriver 초기화 실패. 동영상 생성을 진행할 수 없습니다."
                )
                return

            if fliki_generator.login():
                print("Fliki 로그인 성공. 동영상 생성을 시작합니다.")
                video_generated = fliki_generator.generate_video_from_ppt(
                    ppt_file_path=ppt_file_path
                )
                if video_generated:
                    print(
                        f"동영상 생성 및 다운로드 프로세스 완료/시작됨. {VIDEO_DIR} 디렉토리를 확인하세요."
                    )
                    # FlikiVideoGenerator의 _wait_and_download_video 에서 다운로드를 처리하고
                    # 최종 다운로드 확인까지 진행합니다.
                    # 실제 파일 다운로드 완료를 여기서 명시적으로 확인하려면 추가 로직이 필요할 수 있습니다.
                    # (예: 파일 크기 변화 감지, 특정 시간 동안 대기 후 파일 존재 확인 등)
                    print("최종 동영상 파일을 확인합니다...")
                    time.sleep(30)  # 다운로드를 위한 추가 대기 시간 (필요에 따라 조절)
                    latest_video = get_latest_file(
                        VIDEO_DIR, "mp4"
                    )  # 또는 다른 비디오 확장자
                    if latest_video:
                        print(f"다운로드된 비디오 파일 (추정): {latest_video}")
                    else:
                        print(
                            f"{VIDEO_DIR} 에서 비디오 파일을 찾지 못했습니다. 수동 확인이 필요할 수 있습니다."
                        )
                else:
                    print("동영상 생성/다운로드 프로세스에 실패했습니다.")
            else:
                print("Fliki 로그인 실패. 동영상 생성을 진행할 수 없습니다.")
                return
        except Exception as e:
            print(f"FlikiVideoGenerator 처리 중 오류 발생: {e}")
        finally:
            if hasattr(fliki_generator, "driver") and fliki_generator.driver:
                fliki_generator.driver.quit()
                print("Fliki WebDriver 종료됨.")
    else:
        print("PPT 파일 경로가 없어 동영상 생성을 건너뜁니다.")

    print("\n--- 모든 작업 완료. 프로그램을 종료합니다. ---")


if __name__ == "__main__":
    main()
