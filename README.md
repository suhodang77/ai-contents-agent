# AI Contents Agent

## 주요 기능

- **YouTube 스크립트 추출**: 지정된 YouTube 동영상의 음성을 추출하여 텍스트 스크립트로 변환합니다.
- **AI 스크립트 재구성**: Google Gemini AI 모델을 사용하여 원본 스크립트를 특정 학습 대상자(초등학생, 중학생, 일반인)에 맞춰 교육용 스크립트로 재생성합니다.
- **Gamma PPT 자동 생성**: 생성된 스크립트를 바탕으로 Gamma.app 서비스를 자동화하여 프레젠테이션(PPT)을 생성하고 PDF 파일로 내보냅니다.
- **Fliki 영상 자동 생성**: 생성된 PPT 파일을 기반으로 Fliki.ai 서비스를 자동화하여 AI 보이스오버가 포함된 영상을 제작합니다.
- **ChatGPT 썸네일 생성 (주석 처리됨)**: DALL-E를 통해 강의 정보에 맞는 썸네일을 생성하는 기능이 포함되어 있습니다.

## 사전 준비 사항

1. **Python**: Python 3.12.9 버전이 설치되어 있어야 합니다.
2. **Google Chrome**: Selenium 자동화를 위해 Google Chrome 브라우저가 설치되어 있어야 합니다.
3. **aria2c (설치 권장)**: `yt-dlp`가 오디오를 더 빠르게 다운로드하기 위해 `aria2c` 다운로더를 사용합니다. 시스템에 설치되어 있으면 다운로드 성능이 향상됩니다. (설치하지 않아도 작동은 가능)

## 설치 및 설정 방법

### 1. 레포지토리 복제

```bash
git clone https://github.com/suhodang/ai-contents-agent.git
cd ai-contents-agent
```

### 2. Python 가상환경 생성 및 활성화

프로젝트의 의존성을 시스템의 다른 패키지와 격리하기 위해 가상환경을 사용하는 것을 강력히 권장합니다.

- **macOS / Linux:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

- **Windows:**

    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

### 3. 의존성 패키지 설치

`docs/requirements.txt` 파일에 명시된 모든 필수 파이썬 라이브러리를 설치합니다.

```bash
pip install -r docs/requirements.txt
```

### 4. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 Google Gemini API 키를 추가해야 합니다.

1. `.env.example` 파일의 이름에서 `.example`을 지웁니다.
2. `your_google_api_key` 부분을 실제 키로 교체합니다.

    이 API 키는 `GeminiResponder` 및 `VideoToText` 모듈에서 사용됩니다.

## 프로그램 실행 방법
###  최신 버전-V1.3 실행 설명서 notion 링크
 https://www.notion.so/suhodang/ai-contents-agent-248cc5b2d34280168f20c2af6f7162d6?source=copy_link

<details>
<summary><font size="4"><b>V1.0 실행 설명서</font></summary>  

### 1. 스크립트 실행

#### Windows

명령 프롬프트(cmd)나 PowerShell에서 아래 명령어를 실행합니다.

```powershell
run.bat
```

#### macOS / Linux

프로젝트 루트 디렉토리에서 아래의 쉘 스크립트를 실행합니다.

```bash
source run.sh
```

또는 직접 Python 모듈을 실행할 수도 있습니다.

```bash
python -m src.main
```

### 2. 사용자 입력

스크립트가 실행되면 터미널에 다음과 같은 정보를 순서대로 입력해야 합니다.

1. **YouTube 동영상 URL**: 분석할 동영상의 주소.
2. **강의 정보**: `강의 제목, 교수명, 난이도, 차시`를 쉼표와 공백(`, `)으로 구분하여 입력.
3. **학습 대상자**: `초등학생`, `중학생`, `일반인` 중 하나를 선택하여 입력 (기본값: 일반인).

### 3. 웹 서비스 수동 로그인

스크립트가 Gamma, Fliki 등 웹사이트에 처음 접속하면, 브라우저 창이 활성화되며 사용자가 직접 로그인해야 합니다.

- 스크립트는 사용자가 로그인을 완료하고 다음 페이지로 넘어갈 때까지 자동으로 대기합니다.
- 로그인이 완료되면 자동화 프로세스가 계속 진행됩니다.

### 4. 결과 확인

- 생성된 텍스트 파일(스크립트, 상세페이지): `data/generated_texts/`
- Gamma에서 생성된 최종 PPT(PDF 형식) 파일: `data/results/`
- Fliki에서 생성된 최종 동영상(MP4 형식) 파일: `data/results/`
</details>

## 프로젝트 구조

```txt
.
├── run.sh                    # 프로그램 실행 스크립트(macOS / Linux)
├── run.bat                   # 프로그램 실행 스크립트(Windows)
├── data/                     # 데이터 저장용 디렉토리 (자동 생성)
│   ├── generated_texts/      # AI가 생성한 스크립트, 상세페이지 저장
│   ├── results/              # 최종 결과물(PPT, 영상) 저장
│   ├── audio/                # YouTube에서 추출한 음성 파일 저장
│   └── selenium-dev-profile/ # Selenium용 Chrome 프로필
├── docs/
│   └── requirements.txt      # Python 의존성 목록
├── src/
│   ├── main.py               # 메인 실행 파일
│   ├── modules/              # 기능별 모듈
│   │   ├── video_to_text.py
│   │   ├── gemini_responder.py
│   │   ├── gamma_automator.py
│   │   └── fliki_video_generator.py
│   └── utils/                # 유틸리티 함수
│       └── selenium_setup.py
│       └── selenium_utils.py
└── .env                      # (사용자가 생성) 환경 변수 파일
```

## 주요 의존성

- selenium==4.33.0
- google-genai==1.21.1
- PyAutoGUI==0.9.54
- yt-dlp==2025.6.9
- python-dotenv==1.1.0
- requests==2.32.3
