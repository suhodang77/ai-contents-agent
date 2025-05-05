import os
import google.generativeai as genai


class GeminiResponder:
    BASE_PROMPT_FILE = "data/base_prompt.md"

    def __init__(
        self,
        api_key=None,
        model_name="gemini-2.5-flash-preview-04-17",
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=65536,
        system_instruction="한국어로 답변해줘",
    ):
        """
        GeminiResponder 클래스를 초기화합니다.

        API 키 설정, 모델 파라미터 구성, 그리고 베이스 프롬프트를 로드합니다.

        Args:
            api_key (str, optional): Google Gemini API 키. 제공되지 않으면
                                    `GEMINI_API_KEY` 환경 변수에서 로드합니다.
                                    Defaults to None.
            model_name (str, optional): 사용할 Gemini 모델의 이름.
                                    Defaults to "gemini-2.5-flash-preview-04-17".
            temperature (float, optional): 응답 생성 시 샘플링 온도를 제어합니다.
                                        Defaults to 1.
            top_p (float, optional): 응답 생성 시 누적 확률을 제어합니다.
                                    Defaults to 0.95.
            top_k (int, optional): 응답 생성 시 고려할 상위 토큰 수를 제어합니다.
                                Defaults to 64.
            max_output_tokens (int, optional): 생성될 응답의 최대 토큰 수.
                                        Defaults to 65536.
            system_instruction (str, optional): 모델에 제공할 시스템 수준의 명령어.
                                            Defaults to "한국어로 답변해줘".
        """
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Error: Gemini API 키가 환경 변수로 설정되지 않았습니다. GEMINI_API_KEY 환경 변수를 설정하거나 api_key 매개변수를 통해 설정하세요."
                )
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens
        self.system_instruction = system_instruction
        self.base_prompt = self._load_base_prompt()

    def _load_base_prompt(self):
        """
        지정된 경로에서 베이스 프롬프트 텍스트 파일을 로드합니다.

        내부적으로 사용되는 헬퍼 메서드입니다.

        Returns:
            str | None: 파일 내용을 문자열로 반환하거나, 파일 로드 실패 시 None을 반환합니다.
        """
        try:
            with open(self.BASE_PROMPT_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(
                f"Error: 베이스 프롬프트 파일 '{self.BASE_PROMPT_FILE}'을 찾을 수 없습니다."
            )
            return None

    def generate_response(self, summary_result):
        """
        베이스 프롬프트와 주어진 요약 결과를 결합하여 Google Gemini API를 호출하고,
        생성된 텍스트 응답을 반환합니다.

        Args:
            summary_result (str): 베이스 프롬프트에 추가될 요약 스크립트.

        Returns:
            str | None: Gemini API로부터 생성된 텍스트 응답 문자열.
                        오류 발생 시 None을 반환합니다.
        """
        if not self.base_prompt:
            print("Error: 베이스 프롬프트를 로드하지 못했습니다.")
            return None

        prompt = f"{self.base_prompt}\n{summary_result}"

        print("\n[Gemini 프롬프트]")
        print(prompt)

        genai.configure(api_key=self.api_key)

        generation_config = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=self.system_instruction,
        )

        chat_session = model.start_chat()

        try:
            response = chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            return None
