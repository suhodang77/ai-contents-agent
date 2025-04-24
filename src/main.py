import os
from dotenv import load_dotenv
from lilys_summarizer import LilysSummarizer
from gemini_responder import GeminiResponder
from gamma_automator import GammaAutomator

if __name__ == "__main__":
    # .env 파일 로드
    load_dotenv()

    # API 키 로드 (각 클래스에서 자체적으로 API 키 검증)
    lilys_api_key = os.getenv("LILYS_AI_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not lilys_api_key:
        print(
            "API 키가 .env 파일에 설정되지 않았습니다. LILYS_AI_API_KEY 환경 변수를 설정해주세요."
        )
        exit()
    if not gemini_api_key:
        print(
            "API 키가 .env 파일에 설정되지 않았습니다. GEMINI_API_KEY 환경 변수를 설정해주세요."
        )
        exit()

    # LilysSummarizer 및 GeminiResponder 인스턴스 생성
    lilys_summarizer = LilysSummarizer(api_key=lilys_api_key)
    gemini_responder = GeminiResponder(api_key=gemini_api_key)
    gamma_automator = GammaAutomator()

    # 요약할 유튜브 비디오 URL
    youtube_video_url = "https://www.youtube.com/watch?v=eRfHp16qJq8"

    # 유튜브 비디오 요약
    summary_result_dict = lilys_summarizer.summarize_youtube_video(youtube_video_url)

    if "error" in summary_result_dict:
        print(summary_result_dict)
        exit()  # 요약 실패 시 main.py 종료

    elif "summary" in summary_result_dict:
        summary_result = summary_result_dict.get("summary").get("rawScript")

        # Gemini 응답 생성
        gemini_response_text = gemini_responder.generate_response(summary_result)

        if gemini_response_text:
            print("\n[Gemini 요약 결과:]")
            print(gemini_response_text)

            if gamma_automator.automate_gamma_ppt_creation(gemini_response_text):
                print("\nGamma PPT 제작 자동화 성공!")
                gamma_automator.export_ppt()
            else:
                print("\nGamma PPT 제작 자동화 실패!")
        else:
            print("\nGemini 응답 생성 실패.")

    elif "status" in summary_result_dict and summary_result_dict["status"] != "done":
        print("\n요약 상태:")
        print(
            summary_result_dict
        )  # pending, unknown 상태 출력 (failed는 error로 처리됨)
