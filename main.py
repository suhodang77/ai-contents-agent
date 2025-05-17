import subprocess
import time
import pyautogui
import os

def open_gamma():
    # Gamma 앱 실행
    subprocess.Popen(['open', '-a', 'Gamma'])
    
    # 앱이 완전히 로드될 때까지 대기
    time.sleep(3)
    
    # 로그인 버튼 이미지 경로 설정
    login_button_path = os.path.join('assets', 'login_button.png')
    
    # 로그인 버튼 이미지와 화면 비교
    try:
        # 이미지가 화면에 있는지 확인 (confidence=0.6으로 60% 이상 일치하는지 확인)
        if pyautogui.locateOnScreen(login_button_path, confidence=0.6):
            print("이미 로그인되어 있습니다.")
        else:
            print("로그인이 필요합니다. 로그인을 진행합니다.")
            # Tab 키를 눌러 로그인 버튼으로 이동
            pyautogui.press('tab')
            # Enter 키를 눌러 로그인 버튼 클릭
            pyautogui.press('enter')
    except Exception as e:
        print(f"이미지 인식 중 오류 발생: {e}")

if __name__ == "__main__":
    open_gamma() 