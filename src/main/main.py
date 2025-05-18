from fliki import FlikiLogin, FlikiPPTToVideo

def main():
    """Fliki 로그인 및 PPT to Video 자동화 프로세스 실행"""
    
    # 1. Fliki 로그인
    print("🔑 Fliki 로그인 시도...")
    fliki = FlikiLogin()
    
    try:
        # 2. 로그인 성공 여부 확인
        if not fliki.login():
            print("❌ 로그인 실패. 프로그램을 종료합니다.")
            return
            
        print("✅ 로그인 성공!")
        
        # 3. PPT to Video 변환 프로세스 시작
        print("\n🎬 PPT to Video 자동화 시작...")
        ppt_video = FlikiPPTToVideo(fliki.driver)
        ppt_video.execute_pipeline()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        # 4. 브라우저 종료
        fliki.close()
        print("\n👋 프로그램 종료")

if __name__ == "__main__":
    main()
