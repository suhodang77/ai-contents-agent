import requests
import os
import json
import time

# load_dotenv() # main.py에서 load_dotenv() 호출하도록 변경


class LilysSummarizer:
    SUMMARIZED_URLS_FILE = "data/summarized_urls.json"

    def __init__(self, api_key=None):
        """
        LilysSummarizer 클래스 초기화

        Args:
            api_key (str, optional): Lilys AI API 키. .env 파일에서 로드하지 않으려면 직접 전달. Defaults to None.
        """
        if not api_key:
            api_key = os.getenv("LILYS_AI_API_KEY")
            if not api_key:
                raise ValueError(
                    "API 키가 환경 변수로 설정되지 않았습니다. LILYS_AI_API_KEY 환경 변수를 설정하거나 api_key 매개변수를 통해 설정하세요."
                )
        self.api_key = api_key
        self.summarized_urls_data = (
            self._load_summarized_urls()
        )  # 클래스 초기화 시 로드

    def _load_summarized_urls(self):
        """
        (내부 함수) 요약된 URL 및 requestId 정보를 파일에서 로드합니다.
        파일이 없으면 빈 딕셔너리를 반환합니다.
        """
        try:
            with open(self.SUMMARIZED_URLS_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_summarized_urls(self, new_summarized_data):
        """
        (내부 함수) 요약된 URL 및 requestId 정보를 파일에 저장합니다.
        기존 데이터를 유지하고 새로운 데이터를 추가합니다.
        """
        existing_data = self._load_summarized_urls()  # 기존 데이터 로드
        updated_data = existing_data.copy()  # 기존 데이터 복사 (덮어쓰기 방지)

        # 새로운 데이터 업데이트 (딕셔너리 병합)
        updated_data.update(new_summarized_data)

        with open(self.SUMMARIZED_URLS_FILE, "w") as f:
            json.dump(
                updated_data, f, indent=4
            )  # 업데이트된 전체 데이터를 파일에 덮어쓰기

    def get_summary_result_by_request_id(self, request_id, result_type="rawScript"):
        """
        requestId를 사용하여 요약 결과를 가져옵니다.
        """
        result_endpoint = (
            f"https://tool.lilys.ai/summaries/{request_id}?resultType={result_type}"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            result_response = requests.get(result_endpoint, headers=headers)
            result_response.raise_for_status()
            result_data = result_response.json()
            if result_data.get("status") == "done":
                return {"summary": result_data.get("data").get("data")}
            elif result_data.get("status") == "pending":
                return {"status": "pending", "response": result_data}
            elif result_data.get("status") == "failed":
                return {
                    "error": "요약 생성 실패 (requestId 기반 조회)",
                    "response": result_data,
                }
            else:
                return {"status": "unknown", "response": result_data}

        except requests.exceptions.HTTPError as e:
            error_response = e.response
            return {
                "error": "API 요청 실패 (HTTP 에러, requestId 기반 조회)",
                "status_code": error_response.status_code,
                "response": error_response.json()
                if error_response.headers["Content-Type"] == "application/json"
                else error_response.text,
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": "API 요청 실패 (요청 에러, requestId 기반 조회)",
                "exception": str(e),
            }

    def summarize_youtube_video(
        self,
        youtube_url,
        result_language="ko",
        model_type="rawScript",
        max_polling_attempts=10,  # 폴링 시도 횟수 제한 (parameterize)
        polling_interval_seconds=10,  # 폴링 간격 (parameterize)
    ):
        """
        Lilys AI YouTube 요약 API를 사용하여 유튜브 비디오를 요약하고 결과를 반환합니다.
        중복 요약을 방지하고, 기존 requestId가 있는 경우 결과를 재사용하며,
        get_summary_result_by_request_id 함수를 활용하여 폴링 로직을 재사용합니다.

        Args:
            youtube_url (str): 요약할 유튜브 비디오 URL
            api_key (str): Lilys AI API 키
            summarized_urls_data (dict): 이미 요약된 URL 및 requestId 데이터
            result_language (str, optional): 요약 언어 (ko, en 등). Defaults to "ko".
            model_type (str, optional): 모델 유형 (gpt-3.5, gpt-4). Defaults to "summaryNote". # 수정: default 변경
            max_polling_attempts (int, optional): 최대 폴링 시도 횟수. Defaults to 10. # 추가
            polling_interval_seconds (int, optional): 폴링 간격 (초). Defaults to 10. # 추가

        Returns:
            dict: 요약 결과 (성공 시) 또는 에러 메시지 (실패 시)
        """
        result_type = model_type  # result_type 변수 추가

        if youtube_url in self.summarized_urls_data:
            request_id = self.summarized_urls_data[youtube_url]
            print(
                f"이미 요약된 URL입니다. requestId: {request_id}를 사용하여 결과 확인 시도..."
            )
            result = self.get_summary_result_by_request_id(
                request_id, result_type
            )  # 수정: result_type 인자 추가
            if "summary" in result:
                print("기존 요약 결과 로드 성공.")
                return result
            elif "status" in result and result["status"] == "pending":
                print("기존 요약이 아직 처리 중입니다. 폴링을 통해 결과 확인 시도...")
                for _ in range(max_polling_attempts):  # 최대 폴링 횟수 사용
                    time.sleep(polling_interval_seconds)  # 폴링 간격 사용
                    result = self.get_summary_result_by_request_id(
                        request_id, result_type
                    )  # 수정: result_type 인자 추가
                    if "summary" in result:
                        print("기존 요약 결과 로드 성공 (폴링).")
                        return result
                    elif (
                        "status" in result and result["status"] != "pending"
                    ):  # pending 외 다른 상태 (failed, unknown)
                        return result  # 에러 또는 알 수 없는 상태 반환
                    print("요약 생성 중... (폴링)")
                return {
                    "error": "기존 요약 결과를 가져오는데 실패했습니다 (시간 초과, 폴링).",
                    "response": result,
                }  # 폴링 시간 초과
            else:
                print(
                    f"기존 requestId({request_id})로 결과 조회 실패. 다시 요약 시도."
                )  # requestId 조회 실패 시, 다시 요약 시도

        # 새로운 요약 생성 요청 (URL이 summarized_urls_data에 없거나, 기존 requestId 조회 실패 시)
        api_endpoint = "https://tool.lilys.ai/summaries"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "source": {"sourceType": "youtube_video", "sourceUrl": youtube_url},
            "resultLanguage": result_language,
            "modelType": model_type,  # 함수 인자 model_type 사용
        }

        try:
            # 요약 생성 요청
            response = requests.post(
                api_endpoint, headers=headers, data=json.dumps(payload)
            )
            response.raise_for_status()  # HTTP 에러 발생 시 예외 발생

            request_data = response.json()
            request_id = request_data.get("requestId")

            if not request_id:
                return {
                    "error": "requestId를 받지 못했습니다.",
                    "response": request_data,
                }

            print(f"요약 생성 요청 성공. requestId: {request_id}")

            # --- [ 폴링 로직 변경: get_summary_result_by_request_id 함수 활용 ] ---
            last_result = {}  # last_result 초기화
            for _ in range(max_polling_attempts):
                time.sleep(polling_interval_seconds)
                result = self.get_summary_result_by_request_id(
                    request_id, result_type
                )  # 수정: result_type 인자 전달
                last_result = result  # 추가: last_result 에 현재 result 저장
                if "summary" in result:  # 요약 완료 (status: done)
                    new_summarized_data = {youtube_url: request_id}
                    self.summarized_urls_data.update(
                        new_summarized_data
                    )  # 즉시 업데이트
                    self._save_summarized_urls(new_summarized_data)  # 파일에 저장
                    return result
                elif (
                    "status" in result and result["status"] != "pending"
                ):  # pending 외 상태 (failed, unknown)
                    return result  # 에러 또는 알 수 없는 상태 반환
                print("요약 생성 중... (폴링)")  # status: pending (요약 진행 중)
            # --- [ 폴링 로직 변경: get_summary_result_by_request_id 함수 활용 ] ---

            return {
                "error": "요약 결과를 가져오는데 실패했습니다 (시간 초과).",
                "response": last_result,
            }

        except requests.exceptions.HTTPError as e:
            error_response = e.response
            print(f"HTTP 에러 발생: {e}")
            print(f"상태 코드: {error_response.status_code}")
            try:
                error_message = error_response.json()
                print(f"에러 메시지: {error_message}")
                return {
                    "error": "API 요청 실패 (HTTP 에러)",
                    "status_code": error_response.status_code,
                    "response": error_message,
                }
            except json.JSONDecodeError:
                print("에러 응답 JSON 디코딩 실패")
                return {
                    "error": "API 요청 실패 (HTTP 에러, JSON 디코딩 실패)",
                    "status_code": error_response.status_code,
                }

        except requests.exceptions.RequestException as e:
            print(f"요청 에러 발생: {e}")
            return {"error": "API 요청 실패 (요청 에러)", "exception": str(e)}
