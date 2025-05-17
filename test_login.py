from gamma_automator import GammaAutomator
import time

def test_login():
    print("Gamma 로그인 테스트를 시작합니다...")
    
    # GammaAutomator 인스턴스 생성
    automator = GammaAutomator()
    
    try:
        # 로그인 시도
        print("로그인을 시도합니다...")
        if automator.login():
            print("로그인 성공!")
            # 로그인 성공 후 5초 대기
            time.sleep(5)
        else:
            print("로그인 실패!")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 브라우저 종료
        print("브라우저를 종료합니다...")
        automator.driver.quit()

if __name__ == "__main__":
    test_login() 