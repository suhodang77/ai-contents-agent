import requests
import os
import json
import time


class LilysSummarizer:
    def __init__(self, api_key=None):
        """
        LilysSummarizer 클래스 초기화.

        Args:
            api_key (str, optional): Lilys AI API 키.
                                     None이면 환경 변수 'LILYS_AI_API_KEY'에서 로드합니다.
        Raises:
            ValueError: API 키가 제공되지 않거나 환경 변수에도 설정되어 있지 않은 경우.
        """
        if not api_key:
            api_key = os.getenv("LILYS_AI_API_KEY")
            if not api_key:
                raise ValueError(
                    "API 키가 환경 변수로 설정되지 않았습니다. LILYS_AI_API_KEY 환경 변수를 설정하거나 api_key 매개변수를 통해 설정하세요."
                )
        self.api_key = api_key
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_file_dir, "..", "..", "data")
        self.SUMMARIZED_URLS_FILE = os.path.join(data_dir, "summarized_urls.json")
        self.summarized_urls_data = self._load_summarized_urls()

    def _load_summarized_urls(self):
        """
        요약된 URL 및 requestId 정보를 JSON 파일에서 로드합니다.

        Returns:
            dict: 파일에서 로드된 데이터. 파일이 없으면 빈 딕셔너리를 반환합니다.
        """
        try:
            with open(self.SUMMARIZED_URLS_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_summarized_urls(self, new_summarized_data):
        """
        새로운 요약 URL 및 requestId 정보를 JSON 파일에 저장합니다.
        기존 데이터를 유지하고 새로운 데이터를 추가/업데이트합니다.

        Args:
            new_summarized_data (dict): 파일에 저장할 새로운 요약 데이터.
                                         예: {youtube_url: request_id}
        """
        existing_data = self._load_summarized_urls()
        updated_data = existing_data.copy()
        updated_data.update(new_summarized_data)
        with open(self.SUMMARIZED_URLS_FILE, "w") as f:
            json.dump(updated_data, f, indent=4)

    def get_summary_result_by_request_id(self, request_id, result_type="rawScript"):
        """
        제공된 requestId를 사용하여 Lilys AI로부터 요약 결과를 가져옵니다.

        Args:
            request_id (str): 요약 결과를 조회할 요청 ID.
            result_type (str, optional): 원하는 결과 유형(예: 'rawScript', 'summaryNote').
                                         Defaults to "rawScript".

        Returns:
            dict: API 응답. 성공 시 요약 데이터를 포함하거나,
                  처리 중이거나 실패한 경우 관련 상태 및 에러 정보를 포함합니다.
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
        max_polling_attempts=10,
        polling_interval_seconds=10,
    ):
        """
        Lilys AI API를 사용하여 YouTube 비디오를 요약합니다.

        이미 요약된 URL인 경우 저장된 requestId를 사용하여 결과를 가져오려고 시도합니다.
        새로운 URL인 경우 요약 요청을 보내고, 완료될 때까지 폴링합니다.

        Args:
            youtube_url (str): 요약할 YouTube 비디오 URL.
            result_language (str, optional): 요약 결과 언어 (예: 'ko', 'en'). Defaults to "ko".
            model_type (str, optional): 사용할 요약 모델 유형 (예: 'rawScript', 'summaryNote').
                                        Defaults to "rawScript".
            max_polling_attempts (int, optional): 요약 결과 확인을 위한 최대 폴링 시도 횟수.
                                               Defaults to 10.
            polling_interval_seconds (int, optional): 폴링 시도 간 간격(초). Defaults to 10.

        Returns:
            dict: 요약 결과 또는 에러 정보를 담은 딕셔너리.
                  성공 시 'summary' 키에 요약 내용이 포함됩니다.
                  실패 또는 오류 발생 시 'error' 키 및 관련 정보가 포함됩니다.
        """
        result_type = model_type

        if youtube_url in self.summarized_urls_data:
            request_id = self.summarized_urls_data[youtube_url]
            print(
                f"이미 요약된 URL입니다. requestId: {request_id}를 사용하여 결과 확인 시도..."
            )
            result = self.get_summary_result_by_request_id(request_id, result_type)
            if "summary" in result:
                print("기존 요약 결과 로드 성공.")
                return result
            elif "status" in result and result["status"] == "pending":
                print("기존 요약이 아직 처리 중입니다. 폴링을 통해 결과 확인 시도...")
                for _ in range(max_polling_attempts):
                    time.sleep(polling_interval_seconds)
                    result = self.get_summary_result_by_request_id(
                        request_id, result_type
                    )
                    if "summary" in result:
                        print("기존 요약 결과 로드 성공 (폴링).")
                        return result
                    elif "status" in result and result["status"] != "pending":
                        return result
                    print("요약 생성 중... (폴링)")
                return {
                    "error": "기존 요약 결과를 가져오는데 실패했습니다 (시간 초과, 폴링).",
                    "response": result,
                }
            else:
                print(f"기존 requestId({request_id})로 결과 조회 실패. 다시 요약 시도.")

        api_endpoint = "https://tool.lilys.ai/summaries"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "source": {"sourceType": "youtube_video", "sourceUrl": youtube_url},
            "resultLanguage": result_language,
            "modelType": model_type,
        }

        try:
            response = requests.post(
                api_endpoint, headers=headers, data=json.dumps(payload)
            )
            response.raise_for_status()

            request_data = response.json()
            request_id = request_data.get("requestId")

            if not request_id:
                return {
                    "error": "requestId를 받지 못했습니다.",
                    "response": request_data,
                }

            print(f"요약 생성 요청 성공. requestId: {request_id}")
            new_summarized_data = {youtube_url: request_id}
            self.summarized_urls_data.update(new_summarized_data)
            self._save_summarized_urls(new_summarized_data)

            last_result = {}
            for _ in range(max_polling_attempts):
                time.sleep(polling_interval_seconds)
                result = self.get_summary_result_by_request_id(request_id, result_type)
                last_result = result
                if "summary" in result:
                    return result
                elif "status" in result and result["status"] != "pending":
                    return result
                print("요약 생성 중... (폴링)")

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
