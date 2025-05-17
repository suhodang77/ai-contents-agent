from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time
import os
import requests
from rich.console import Console
from rich.markdown import Markdown

# 1️⃣ Selenium 브라우저 설정
options = Options()
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

try:
    # 2️⃣ 릴리스 AI 접속
    url = "https://lilys.ai/digest/3800693/2505424?s=1&nid=2505424"
    driver.get(url)
    time.sleep(2)  # 렌더링 대기

    # 3️⃣ 강의 제목 추출 (textContent + 정제)
    lecture_title_xpath = "/html/body/div[1]/div[1]/div[3]/div"
    try:
        lecture_title_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, lecture_title_xpath))
        )
        full_text = lecture_title_elem.get_attribute("textContent").strip()
        lines = [line.strip() for line in full_text.split("\n") if "지금 가입하면" not in line and line.strip()]
        lecture_title = lines[0] if lines else "강의 제목 없음"
        print(f"📘 정제된 강의 제목: {lecture_title}")
    except Exception:
        print("❌ 강의 제목을 찾지 못했습니다. 기본 제목으로 진행합니다.")
        lecture_title = "강의 제목 없음"

    # 4️⃣ 스크립트 버튼 클릭
    script_button_xpath = "/html/body/div[1]/div[1]/div[3]/div/div[3]/div[2]/div[2]/div[4]/div/div[1]/div[3]/div/div/div"
    script_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, script_button_xpath))
    )
    script_btn.click()
    print("✅ 스크립트 버튼 클릭 완료")
    time.sleep(2)

    # 5️⃣ 복사 버튼 탐색을 위한 스크롤 반복
    scroll_area_xpath = "/html/body/div[1]/div[1]/div[3]/div/div[3]/div[2]/div[2]"
    scroll_area = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, scroll_area_xpath))
    )
    copy_button_xpath = "/html/body/div[1]/div[1]/div[3]/div/div[3]/div[2]/div[2]/div[5]/div[2]/div[3]/div[2]/button/img"

    found = False
    for _ in range(30):
        try:
            copy_btn = driver.find_element(By.XPATH, copy_button_xpath)
            if copy_btn.is_displayed():
                found = True
                break
        except:
            pass
        driver.execute_script("arguments[0].scrollTop += 500", scroll_area)
        time.sleep(0.3)

    if not found:
        raise Exception("❌ 복사 버튼을 끝까지 내려도 찾을 수 없습니다.")

    # 6️⃣ 복사 버튼 클릭
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", copy_btn)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", copy_btn)
    print("📋 복사 버튼 클릭 완료")
    time.sleep(1)

    # 7️⃣ 클립보드에서 스크립트 텍스트 추출
    script_text = pyperclip.paste()
    print("📎 스크립트 복사 완료")

finally:
    driver.quit()

# 8️⃣ Gemini API 프롬프트 구성
prompt = f"""
다음은 강의 영상의 전체 스크립트입니다. 이 스크립트를 기반으로 강의 영상의 상세 페이지를 작성해주세요. 상세 페이지의 구성은 다음과 같습니다:
또한 강의차수도 적어주세요

📘 강의 제목: {lecture_title}

1. 강의 개요
2. 학습 목표 / 기대 효과
3. 강의 커리큘럼 / 목차
4. 강의 내용 설명 (상세 설명)
5. Q&A / 피드백 섹션

[학습자 수준: 초등학생 또는 중학생]

- 설명은 학습자의 수준에 맞게 쉽게 풀어 주세요.
- 초등학생의 경우 어려운 용어는 최대한 피하고, 짧고 간단한 문장을 사용해 주세요.
- 중학생의 경우 약간 어려운 용어도 쓸 수 있지만 반드시 쉬운 설명을 덧붙여 주세요.
- 예시는 학습자의 생활과 밀접한 사례(예: 학교생활, 친구 관계, 스마트폰, 유튜브 등)를 활용해 주세요.
- 내용은 지루하지 않도록 재미있고 친근한 톤으로 작성해 주세요.
- 초등학생에게는 간단한 핵심만, 중학생에게는 조금 더 자세한 이유나 원리도 포함해 주세요.

아래는 스크립트입니다:
====================
{script_text}
====================
"""

# 9️⃣ Gemini API 요청
API_KEY = "AIzaSyBIj15XrDcbebWbbMoz-ROIx1mkmwwmmSw"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}
data = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ]
}

# 🔟 Gemini 응답 출력 및 저장
console = Console()
response = requests.post(API_URL, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    text = result["candidates"][0]["content"]["parts"][0]["text"]

    console.rule(f"[bold green]📘 강의 제목: {lecture_title}")
    console.print(Markdown(text))

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/gemini_output.md", "w", encoding="utf-8") as f:
        f.write(f"# 📘 강의 제목: {lecture_title}\n\n")
        f.write(text)
    print("✅ Gemini 응답이 outputs/gemini_output.md 에 저장되었습니다!")

else:
    console.print(f"[red]❌ Error {response.status_code}[/red]")
    console.print(response.text)
