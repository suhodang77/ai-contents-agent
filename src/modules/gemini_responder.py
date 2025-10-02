import os
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()


class GeminiResponder:
    AUDIENCE_INSTRUCTIONS = {
        "초등학생": {
            "description": "초등학생",
            "script_guidelines": "- 어려운 용어는 최대한 피하고, 짧고 간단한 문장을 사용해 주세요.\n- 예시는 학교생활, 친구 관계, 스마트폰, 유튜브 등 학습자의 생활과 밀접한 사례를 활용해 주세요.\n- 내용은 지루하지 않도록 재미있고 친근한 톤으로 작성해 주세요.\n- 간단한 핵심만 전달해주세요.",
            "detail_guidelines": "- 설명은 초등학생의 수준에 맞게 쉽게 풀어 주세요.\n- 어려운 용어는 최대한 피하고, 짧고 간단한 문장을 사용해 주세요.\n- 예시는 학교생활, 친구 관계, 스마트폰, 유튜브 등 학습자의 생활과 밀접한 사례를 활용해 주세요.\n- 내용은 지루하지 않도록 재미있고 친근한 톤으로 작성해 주세요.\n- 간단한 핵심만 전달해주세요.",
        },
        "중학생": {
            "description": "중학생",
            "script_guidelines": "- 약간 어려운 용어도 쓸 수 있지만 반드시 쉬운 설명을 덧붙여 주세요.\n- 예시는 학교생활, 친구 관계, 스마트폰, 유튜브 등 학습자의 생활과 밀접한 사례를 활용해 주세요.\n- 내용은 지루하지 않도록 재미있고 친근한 톤으로 작성해 주세요.\n- 조금 더 자세한 이유나 원리도 포함해 주세요.",
            "detail_guidelines": "- 설명은 중학생의 수준에 맞게 쉽게 풀어 주세요.\n- 약간 어려운 용어도 쓸 수 있지만 반드시 쉬운 설명을 덧붙여 주세요.\n- 예시는 학교생활, 친구 관계, 스마트폰, 유튜브 등 학습자의 생활과 밀접한 사례를 활용해 주세요.\n- 내용은 지루하지 않도록 재미있고 친근한 톤으로 작성해 주세요.\n- 조금 더 자세한 이유나 원리도 포함해 주세요.",
        },
        "일반인": {
            "description": "해당 분야에 처음 입문하는 일반인",
            "script_guidelines": "- 비전공자도 쉽게 이해할 수 있도록 설명해야 합니다.",
            "detail_guidelines": "- 비전공자도 쉽게 이해할 수 있도록 설명해야 합니다.",
        },
    }

    SCRIPT_BASE_PROMPT = """# 프롬프트

## 역할

당신은 **{lecture_title}** 주제의 전문 강사입니다.

## 목표

제공된 유튜브 영상 요약 스크립트를 바탕으로, 비전공자들이 핵심 정보를 **쉽게 이해**하도록 돕는 **5분 내외의 새로운 영상 강의 스크립트**를 작성해주세요.
답변에는 새로 작성한 스크립트 이외의 답변이나 문장 없이 오로지 스크립트만 답변에 포함되도록 하세요.
스크립트의 첫 시작은 "안녕하세요, **{professor_name}** 강사입니다."로 시작해야 합니다.

## 대상 청중

대상은 {audience_level_description}입니다. 해당 주제에 대한 지식이 부족한 사람들도 쉽게 이해할 수 있도록 설명해야 합니다.
다음은 대상 청중에 따른 추가 지침입니다:
{audience_specific_script_guidelines}

## 형식 및 스타일

* 형식: **강의** (선생님이 학생들에게 설명하듯이)
* 길이: **5분 내외** (스크립트 분량 조절 필요)
* 톤앤매너: **전문적이면서도 친근하게** (너무 딱딱하거나 격식 차리지 않고, 편안하게 정보를 전달하는 느낌)

## 재구성 방식 (대상 청중 지침을 최우선으로 고려)

* **요약 스크립트의 핵심 내용을 적극적으로 활용**하되, **쉽게 풀어서 설명**해주세요.
* **비전공자도 이해하기 쉬운 용어**를 사용하고, **비유**나 **예시**를 적극적으로 활용하여 설명해주세요.
* **핵심 내용을 강조**하고, **시각적인 요소 (화면 구성, CG 등)** 를 활용하여 이해도를 높일 수 있는 부분을 스크립트에 **간단하게 지시**해주세요. (예: "화면에는 핵심 개념을 보여주는 CG 삽입", "칠판에 판서하는 듯한 화면 구성")
* 너무 세부적인 내용보다는 **전체적인 흐름과 핵심 개념 위주**로 설명해주세요.
* **친근한 어투**를 사용하여 시청자들이 **부담 없이** 영상을 시청하고 **정보를 습득**하도록 유도해주세요. (예: "~에 대해 알아볼까요?", "~는 정말 중요합니다!", "쉽게 말해서~" 와 같은 표현 사용)

## 유튜브 영상 요약 스크립트

{script}
"""

    DETAIL_PAGE_PROMPT = """다음은 강의 영상의 전체 스크립트입니다. 이 스크립트를 기반으로 강의 영상의 상세 페이지를 작성해주세요. 상세 페이지의 구성은 다음과 같습니다:
또한 강의차수도 적어주세요
📘 강의 제목: {lecture_title}
👨‍🏫 강사: {professor_name}
1. 강의 개요
2. 학습 목표 / 기대 효과
3. 강의 커리큘럼 / 목차
4. 강의 내용 설명 (상세 설명)
5. Q&A / 피드백 섹션
[학습자 수준: {audience_level_description}]
{audience_specific_detail_guidelines}
아래는 스크립트입니다:
====================
{script}
====================
"""

    def __init__(
        self,
        api_key=None,
        model_name="gemini-2.5-flash",  
        temperature=1.0,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        system_instruction="한국어로 답변해줘",
        prompt_mode="script",
        target_audience="일반인",
    ):
        """GeminiResponder 클래스의 인스턴스를 초기화합니다.

        Args:
            api_key (str, optional): Google API 키. Defaults to None. 환경 변수 `GOOGLE_API_KEY` 또는 `GEMINI_API_KEY`에서 로드됩니다.
                model_name (str, optional): 사용할 Gemini 모델의 이름. Defaults to "gemini-2.5-flash".
                temperature (float, optional): 생성 다양성을 제어하는 값 (0.0 ~ 1.0). Defaults to 1.0.
            top_p (float, optional): 다음 토큰을 선택할 때 고려할 확률 질량의 비율. Defaults to 0.95.
            top_k (int, optional): 다음 토큰을 선택할 때 고려할 상위 토큰의 개수. Defaults to 64.
            max_output_tokens (int, optional): 생성할 최대 토큰 수. Defaults to 8192.
            system_instruction (str, optional): 모델에 제공할 시스템 수준 지침. Defaults to "한국어로 답변해줘".
            prompt_mode (str, optional): 프롬프트 생성 모드 ("script" 또는 "detail"). Defaults to "script".
            target_audience (str, optional): 대상 청중 레벨 ("초등학생", "중학생", "일반인"). Defaults to "일반인".

        Raises:
            ValueError: API 키가 제공되지 않거나 환경 변수에 설정되어 있지 않은 경우.
            ValueError: Google Gen AI 클라이언트 초기화에 실패한 경우.
        """
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Error: API 키가 환경 변수로 설정되지 않았습니다. GOOGLE_API_KEY 환경 변수를 설정하거나 api_key 매개변수를 통해 설정하세요."
                )

        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens
        self.system_instruction = system_instruction
        self.prompt_mode = prompt_mode

        if target_audience not in self.AUDIENCE_INSTRUCTIONS:
            print(
                f"Warning: 유효하지 않은 target_audience 값입니다: '{target_audience}'. '일반인'으로 기본 설정됩니다."
            )
            self.target_audience = "일반인"
        else:
            self.target_audience = target_audience

        try:
            # genai.configure(api_key=api_key) # 이 줄을 제거합니다.
            self.client = genai.Client(api_key=api_key) # genai.Client 인스턴스를 추가합니다.
            # self.model = self.client.models.GenerativeModel(self.model_name) # client를 통해 model을 초기화합니다.
        except Exception as e:
            raise ValueError(f"Error initializing Google Gen AI Client: {e}")

    def generate_response(self, **data):
        """제공된 데이터를 기반으로 Gemini 모델을 사용하여 응답을 생성합니다.

        `prompt_mode`에 따라 다른 프롬프트를 사용하여 스크립트 또는 상세 페이지 내용을 생성합니다.

        Args:
            **data: 프롬프트 생성에 필요한 데이터.
                - `prompt_mode`가 "script"인 경우:
                    - script (str): 원본 유튜브 영상 요약 스크립트.
                    - lecture_title (str): 강의 제목.
                    - professor_name (str): 교수명.
                - `prompt_mode`가 "detail"인 경우:
                    - script (str): 생성된 강의 스크립트.
                    - lecture_title (str): 강의 제목.
                    - professor_name (str): 교수명.

        Returns:
            str: 생성된 응답 텍스트. 오류 발생 시 None을 반환합니다.
        """
        prompt = None
        audience_data = self.AUDIENCE_INSTRUCTIONS[self.target_audience]
        audience_level_description = audience_data["description"]

        try:
            if self.prompt_mode == "script":
                required_keys = ["script", "lecture_title", "professor_name"]
                if not all(key in data for key in required_keys):
                    print(f"Error: 다음 키가 필요합니다: {required_keys}")
                    return None
                format_params = {
                    "audience_level_description": audience_level_description,
                    "audience_specific_script_guidelines": audience_data[
                        "script_guidelines"
                    ],
                    **data,
                }
                prompt = self.SCRIPT_BASE_PROMPT.format(**format_params)
            elif self.prompt_mode == "detail":
                required_keys = ["script", "lecture_title", "professor_name"]
                if not all(key in data for key in required_keys):
                    print(f"Error: 다음 키가 필요합니다: {required_keys}")
                    return None
                format_params = {
                    "audience_level_description": audience_level_description,
                    "audience_specific_detail_guidelines": audience_data[
                        "detail_guidelines"
                    ],
                    **data,
                }
                prompt = self.DETAIL_PAGE_PROMPT.format(**format_params)
            else:
                print(f"Error: 유효하지 않은 prompt_mode입니다: {self.prompt_mode}")
                return None
        except KeyError as e:
            print(f"Error: 프롬프트 포맷팅 중 오류 발생. 누락된 키: {e}")
            return None

        if not prompt:
            print("Error: 프롬프트가 준비되지 않았습니다.")
            return None

        print("\n[Google Gen AI SDK 프롬프트]")
        # print(prompt) # 너무 길어서 주석 처리

        generation_config = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens,
        }
        
        if self.system_instruction:
            pass

        print("\n[답변 생성 중]")
        try:
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=generation_config, # 딕셔너리 형태의 config를 전달
            )
            response_parts = []
            for chunk in response:
                print(chunk.text, end="")
                response_parts.append(chunk.text)
            print("\n[답변 생성 완료]")
            return "".join(response_parts)
        except Exception as e:
            print(f"Error during Google Gen AI API call: {e}")
            return None