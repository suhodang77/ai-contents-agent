import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.main.fliki import FlikiPPTToVideo
from selenium import webdriver

def test_ppt_to_video():
    """
    Fliki PPT to Video 기능 테스트
    1. 브라우저를 열고 Fliki 로그인 페이지로 이동
    2. 1분 동안 로그인할 수 있는 시간 제공
    3. FlikiPPTToVideo 클래스의 기능 실행 및 테스트
    """
    # Chrome 브라우저 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    # 브라우저 실행
    driver = webdriver.Chrome(options=options)
    
    try:
        print("🚀 Fliki PPT to Video 테스트 시작")
        print("1. Fliki 로그인 페이지로 이동합니다...")
        driver.get("https://app.fliki.ai/files/create")
        
        print("2. 1분 동안 로그인할 수 있습니다...")
        print("   로그인이 완료되면 자동으로 테스트가 진행됩니다.")
        time.sleep(60)  # 1분 대기
        
        print("3. FlikiPPTToVideo 기능 테스트 시작")
        ppt_video = FlikiPPTToVideo(driver)
        ppt_video.execute_pipeline()
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
    finally:
        print("브라우저를 종료합니다...")
        driver.quit()

if __name__ == "__main__":
    test_ppt_to_video()
