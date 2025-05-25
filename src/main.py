import os
import time
import glob
# from urllib.parse import urlparse, parse_qs
# from .modules.lilys_summarizer import LilysSummarizer
from .modules.gemini_responder import GeminiResponder
from .modules.gamma_automator import GammaAutomator
from .modules.fliki_video_generator import FlikiVideoGenerator
# from .modules.chat_gpt_automator import ChatGPTAutomator

DATA_DIR = "data"
GENERATED_TEXT_DIR = os.path.join(DATA_DIR, "generated_texts")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
VIDEO_DIR = os.path.join(DATA_DIR, "videos")


def ensure_dir(directory):
    """지정된 디렉토리가 존재하지 않으면 생성합니다."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_generated_script(content: str, filename: str):
    """생성된 콘텐츠를 지정된 파일 이름으로 저장합니다."""
    ensure_dir(GENERATED_TEXT_DIR)
    file_path = os.path.join(GENERATED_TEXT_DIR, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"콘텐츠가 '{file_path}'에 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"파일 저장 중 오류 발생 ('{file_path}'): {e}")


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
    ensure_dir(GENERATED_TEXT_DIR)
    print(
        f"데이터 디렉토리 확인: {DATA_DIR}, {PDF_DIR}, {VIDEO_DIR}, {GENERATED_TEXT_DIR}"
    )

    # # 1. 동영상 정보 입력 받기
    # youtube_url_input = input("요약할 YouTube 동영상 URL을 입력하세요: ")
    # if not youtube_url_input:
    #     print("URL이 입력되지 않았습니다. 프로그램을 종료합니다.")
    #     return

    # try:
    #     parsed_url = urlparse(youtube_url_input)
    #     if parsed_url.hostname == "youtu.be":  # 2번 포맷
    #         video_id = parsed_url.path[1:]  # 맨 앞의 '/' 제거
    #         youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    #     elif parsed_url.hostname in ("www.youtube.com", "youtube.com"):  # 1번 포맷
    #         query_params = parse_qs(parsed_url.query)
    #         video_id = query_params.get("v", [None])[0]
    #         if video_id:
    #             youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    #         else:
    #             raise ValueError("유효한 YouTube 비디오 ID를 찾을 수 없습니다.")
    #     else:
    #         raise ValueError("유효한 YouTube URL이 아닙니다.")
    #     print(f"변환된 URL: {youtube_url}")
    # except ValueError as e:
    #     print(f"URL 처리 중 오류 발생: {e}")
    #     return
    # except Exception as e:
    #     print(f"알 수 없는 오류 발생: {e}")
    #     return

    # 2. 강의 정보 입력 받기
    lecture_title, professor_name, difficulty_level, lecture_number = input("강의 제목, 교수명, 난이도, 차시를 공백으로 구분하여 입력하세요: ").split()
    if not lecture_title or not professor_name or not difficulty_level or not lecture_number:
        print("강의 제목이 입력되지 않았습니다. 프로그램을 종료합니다.")
        return

    # 3. 학습 대상자 입력 받기
    valid_audiences = ["초등학생", "중학생", "일반인"]
    target_audience_input = input(
        f"학습 대상자를 입력하세요 ({', '.join(valid_audiences)}, 기본값: 일반인): "
    )
    if not target_audience_input or target_audience_input not in valid_audiences:
        print("유효하지 않은 대상자입니다. 기본값 '일반인'으로 설정합니다.")
        target_audience = "일반인"
    else:
        target_audience = target_audience_input
    print(f"학습 대상자: {target_audience}")
    
    # 4. 기존 영상 스크립트 입력 받기
    original_script = None
    script_file_path = os.path.join(DATA_DIR, "script", "script.txt")
    try:
        with open(script_file_path, 'r', encoding='utf-8') as f:
            original_script = f.read()
        print(f"예시 파일 '{script_file_path}'이(가) 생성되었습니다.\n")
    except Exception as e:
        print(f"예시 파일 생성 중 오류 발생: {e}\n")

    # # 2. LilysSummarizer로 스크립트 추출
    # print("\n--- 2. YouTube 동영상 스크립트 추출 시작 ---")
    # try:
    #     summarizer = LilysSummarizer()
    #     summary_result = summarizer.summarize_youtube_video(youtube_url)
    #     if "error" in summary_result:
    #         print(f"스크립트 추출 실패: {summary_result['error']}")
    #         return
    #     original_script = summary_result.get("summary")
    #     if not original_script:
    #         print("스크립트를 추출하지 못했습니다.")
    #         return
    #     print("스크립트 추출 완료.")
    # except Exception as e:
    #     print(f"LilysSummarizer 처리 중 오류 발생: {e}")
    #     return

    # 3. GeminiResponder로 새로운 동영상 스크립트 생성
    print("\n--- 3. 새로운 동영상 스크립트 생성 시작 ---")
    new_script = None  # new_script를 try 블록 외부에서 초기화
    try:
        # 스크립트 생성을 위한 Responder
        script_responder = GeminiResponder(
            prompt_mode="script", target_audience=target_audience
        )
        new_script = script_responder.generate_response(
            script=original_script
        )  # 'script' 키워드 인자 사용
        if not new_script:
            print("새로운 스크립트를 생성하지 못했습니다.")
            # 상세 페이지 생성을 시도하지 않고 종료할 수 있지만, 요구사항에 따라 new_script가 없어도 진행할 수 있도록 return은 주석 처리
            # return
        else:
            print("새로운 동영상 스크립트 생성 완료.")
            save_generated_script(new_script, "generated_script.txt")

    except Exception as e:
        print(f"새로운 동영상 스크립트 생성 중 오류 발생: {e}")
        # 상세 페이지 생성을 시도하지 않고 종료할 수 있지만, 요구사항에 따라 new_script가 없어도 진행할 수 있도록 return은 주석 처리
        # return

    # 4. GeminiResponder로 상세페이지 생성
    print("\n--- 4. 상세페이지 생성 시작 ---")
    if new_script:  # new_script가 존재할 때만 상세 페이지 생성 시도
        try:
            # 상세 페이지 생성을 위한 Responder
            detail_responder = GeminiResponder(
                prompt_mode="detail", target_audience=target_audience
            )
            # lecture_title은 사용자가 입력한 값을 사용하거나, 여기서 새로 정의할 수 있습니다.
            # 여기서는 함수 상단에서 입력받은 lecture_title을 사용합니다.
            detail_page_content = detail_responder.generate_response(
                lecture_title=lecture_title,  # 사용자가 입력한 강의 제목 사용
                script=new_script,  # 생성된 새 스크립트를 사용
            )
            if not detail_page_content:
                print("상세 페이지 내용을 생성하지 못했습니다.")
            else:
                print("상세 페이지 생성 완료.")
                save_generated_script(detail_page_content, "detail_page.txt")
                print("\n[생성된 상세 페이지 내용]")
                print(detail_page_content)

        except Exception as e:
            print(f"상세 페이지 생성 중 오류 발생: {e}")
    else:
        print("새로운 스크립트가 없어 상세 페이지를 생성할 수 없습니다.")

    # 5. 생성된 스크립트 및 상세 페이지 내용 파일로 저장 (위에서 주석처리된 부분을 여기에 통합하거나 별도 함수로 관리)

    # 5. GammaAutomator로 PPT 생성
    print("\n--- 5. Gamma를 사용하여 PPT 생성 시작 ---")
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

    # 6. FlikiVideoGenerator로 동영상 생성
    if ppt_file_path:
        print("\n--- 6. Fliki를 사용하여 동영상 생성 시작 ---")
        try:
            fliki_generator = FlikiVideoGenerator(
                target_audience=target_audience,
                lecture_title=lecture_title,
            )
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
    
    # # 7. ChatGPTAutomator로 썸네일 생성
    # print("\n--- 7. ChatGPTAutomator로 썸네일 생성 시작 ---")
    # try:
    #     chatgpt_automator = ChatGPTAutomator()
    #     if chatgpt_automator.login():
    #         print("ChatGPT 로그인 성공. 썸네일 생성을 시작합니다.")
    #         chatgpt_automator.generate_thumbnail(
    #             course_name=lecture_title,
    #             professor_name=professor_name,
    #             difficulty_level=difficulty_level,
    #             audience_level_description=target_audience,
    #             lecture_number=lecture_number
    #         )
    #         print("썸네일 생성 완료. 결과를 확인합니다.")
    #     else:
    #         print("ChatGPT 로그인 실패. 썸네일 생성을 진행할 수 없습니다.")
    # except Exception as e:
    #     print(f"ChatGPTAutomator 처리 중 오류 발생: {e}")
    


if __name__ == "__main__":
    main()
