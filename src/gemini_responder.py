import os
import google.generativeai as genai


class GeminiResponder:
    BASE_PROMPT_FILE = "data/base_prompt.md"

    def __init__(
        self,
        api_key=None,
        model_name="gemini-2.5-pro-exp-03-25",
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=65536,
        system_instruction="한국어로 답변해줘",
    ):
        """
        GeminiResponder 클래스 초기화

        Args:
            api_key (str, optional): Google Gemini API 키. .env 파일에서 로드하지 않으려면 직접 전달. Defaults to None.
            model_name (str, optional): 사용할 Gemini 모델 이름. Defaults to "gemini-2.0-flash-thinking-exp-01-21".
            temperature (float, optional): 생성 모델의 temperature 설정. Defaults to 1.
            top_p (float, optional): 생성 모델의 top_p 설정. Defaults to 0.95.
            top_k (int, optional): 생성 모델의 top_k 설정. Defaults to 64.
            max_output_tokens (int, optional): 생성 모델의 최대 출력 토큰 수. Defaults to 65536.
            system_instruction (str, optional): Gemini 모델의 시스템 명령어. Defaults to "".
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
        (내부 함수) 베이스 프롬프트 텍스트 파일을 로드합니다.
        """
        try:
            with open(
                self.BASE_PROMPT_FILE, "r", encoding="utf-8"
            ) as f:  # UTF-8 인코딩 명시
                return f.read()
        except FileNotFoundError:
            print(
                f"Error: 베이스 프롬프트 파일 '{self.BASE_PROMPT_FILE}'을 찾을 수 없습니다."
            )
            return None

    def generate_response(self, summary_result):  # 요약 스크립트를 인자로 받음
        """
        Google Gemini API를 사용하여 주어진 프롬프트에 대한 텍스트 응답을 생성합니다.
        """
        if not self.base_prompt:  # 베이스 프롬프트 로드 실패 시 에러 처리
            print("Error: 베이스 프롬프트를 로드하지 못했습니다.")
            return None

        # 최종 프롬프트 조합 (베이스 프롬프트 + 요약 스크립트)
        # prompt = self.base_prompt.replace(
        #     "\n\n[유튜브 영상 요약 스크립트]",
        #     summary_result,  # 베이스 프롬프트 템플릿에 요약 스크립트 삽입
        # )

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
