from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
from ..utils.selenium_setup import setup_selenium_driver
from ..utils.selenium_utils import (
    chrome_focuse,
    press_shift_tab_multiple_times,
    press_tab_multiple_times,
    press_enter,
    paste_text_to_element,
)

# .env 파일에서 환경 변수 로드
load_dotenv(override=True)


class ChatGPTAutomator:
    BASE_PROMPT = """
아래와 같은 조건으로 썸네일용 이미지를 생성하려고 합니다. 별도의 질문/답변 없이 바로 생성해주세요.

### **기본 정보**

- **대상**: {audience_level_description}
- **차시**: {lecture_number}
- **강의명**: {course_name}
- **교수명**: {professor_name}
- **난이도**: {difficulty_level}
- **썸네일 비율**: 16:9
- **스타일**: 교육용 2D 심플 스타일, 밝고 친근한 색감
- **분위기**: 명랑하고 학습에 동기부여를 주는 분위기

---

### **텍스트 레이아웃 및 정확도 요구사항**

### **텍스트 구성**

텍스트는 다음과 같은 4개의 고정된 문구를 **줄 단위로 정확히 표시**해야 하며, 오타 없이 명확하게 인식 가능해야 합니다:

1. **X차시**
2. **강의명**
3. **교수명**
4. 오른쪽 상단의 작은 텍스트: **Lv{difficulty_level}**
- **모든 텍스트는 정확히 해당 문자열로 출력되어야 하며**, '레벌', '레벨:', '차시:' 등으로 잘못 출력되면 안 됩니다.
- **텍스트는 가독성 높은 고딕체 또는 산세리프 스타일의 한국어 글꼴로 출력**되어야 하며, 외계어처럼 깨지거나 잘려보이지 않아야 합니다.
- **텍스트는 이미지 내에 벡터처럼 또렷하고 선명하게 렌더링**되어야 합니다.
- `{difficulty_level}` 는 강의의 레벨 숫자가 들어올 것입니다.
- *"컴푸터적" ⇒ "컴퓨터적"**으로 오타 수정해서 생성해주셔야 합니다.

---

### **텍스트 위치 및 비율**

- 텍스트 블록은 왼쪽 정렬되며, **화면의 왼쪽 10~15% 안쪽 영역**에 배치
- 세로 위치는 **왼쪽 세로 중앙보다 약간 위쪽** (상단에서 20% 정도 아래 위치)
- 텍스트 간 줄 간격은 일정하게 유지되며, 겹치지 않음

**텍스트 크기 비율 예시:**

- **강의명**: 기준 크기 100% (가장 큼), 텍스트 두꺼운 두께
- **X차시, 교수명**: 약 60~70% 크기, 텍스트 얇은 두께
- **Lv{difficulty_level}**: 가장 작고 고정 위치, 약 20% 크기, 박스 형태로 배경색 존재, 텍스트 얇은 두께

---

### **오른쪽 일러스트 요소 조건 (🆕 개선 핵심)**

- **오른쪽 일러스트는 반드시 썸네일 너비의 35% 이내 영역에만 배치**
- **오른쪽 이미지가 중앙이나 왼쪽으로 넘어오지 않도록 강력히 제한**
- **일러스트의 개수는 1개로 제한** (2개 이상 사용 금지)
- **Lv{difficulty_level} 텍스트와 겹치지 않도록** 오른쪽 상단 여백 확보
- 주제에 맞는 심플한 요소 사용

---

### **배경 및 색상 조건**

- 배경은 강의명과 어울리는 **단색 배경**
- 텍스트 색상은 대비가 잘 되는 색

---

### **기타**

- 썸네일에 들어가는 이미지 요소는 중복이 되면 안됩니다. 들어가는 주제가 비슷하더라도 다르게 나와야 하며, 일러스트의 제스쳐 또한 매번 다르게 나와야 합니다.
    """
    
    def __init__(self):
        self.driver, self.chrome_browser_opened_by_script = setup_selenium_driver(
            download_subdir="pdfs", start_url="https://chatgpt.com"
        )
        if not self.driver:
            print("WebDriver 초기화 실패. ChatGPTAutomator 인스턴스 생성 중단.")

    def login(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div/div[1]/div/main/div/div/div[1]/div[3]/div/button[1]",
                    )
                )
            )
            
            chrome_focuse(self.driver)
            time.sleep(1)
            press_shift_tab_multiple_times(3)
            press_enter()
            time.sleep(2)
            press_tab_multiple_times(3)
            press_enter()
            time.sleep(2)
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
        finally:
            login_complete_indicator_xpath = (
                "/html/body/div[1]/div/div[1]/div[1]/div/div/div/nav/div[1]/div"
            )
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located(
                    (By.XPATH, login_complete_indicator_xpath)
                )
            )
            print("로그인 및 페이지 로딩 확인됨.")
            print("자동화 프로세스를 시작합니다.")
            print("=" * 50)
            return True
                
                
    def generate_thumbnail(self, **data):
        paste_text_to_element(
            self.driver,
            "/html/body/div[1]/div/div[1]/div[2]/main/div/div/div[3]/div[1]/div/div/div[2]/form/div[1]/div/div[1]/div[1]/div[2]/div/div/div/div/div/p",
            self.BASE_PROMPT.format(**data)
        )
        press_tab_multiple_times(4)
        press_enter()
        
        

if __name__ == "__main__":
    automator = ChatGPTAutomator()
    automator.login()
    automator.generate_thumbnail(
        course_name="컴퓨터적 사고",
        professor_name="김영태",
        difficulty_level="1",
        audience_level_description="초등학생",
        lecture_number="1"
    )