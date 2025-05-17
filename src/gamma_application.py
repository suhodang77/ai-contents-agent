#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import pyautogui
from dotenv import load_dotenv

class GammaApplication:
    def __init__(self):
        """Initialize the Gamma Application."""
        load_dotenv()  # Load environment variables
        self.setup()
        self.launch_gamma()                 

    def setup(self):
        """Setup the application configuration."""
        # Add your setup logic here
        pass
    
    def launch_gamma(self):                                 
        """Launch the Gamma application."""
        try:
            # macOS에서 Gamma 앱 실행
            subprocess.run(['open', '-a', 'Gamma'])
            print("Gamma 앱이 실행되었습니다.")

            # 앱이 완전히 뜰 때까지 대기
            time.sleep(1)
                    
        except Exception as e:
            print(f"Gamma 앱 실행 중 오류가 발생했습니다: {str(e)}")
    
    def press_tab_multiple_times(self, count):
        """Press the Tab key multiple times using pyautogui."""
        print(f"Tab 키를 {count}번 누릅니다.")
        for _ in range(count):
            pyautogui.press('tab')
            time.sleep(0.1)
    
    def press_enter(self):
        """Press the Enter key using pyautogui."""
        print("Enter 키를 누릅니다.")
        pyautogui.press('enter')
    
    def run(self):
        """Main application logic."""
        self.launch_gamma()
        
        # 첫 번째 시퀀스: Tab 15번, Enter
        self.press_tab_multiple_times(15)
        self.press_enter()
        
        # 0.5초 대기
        time.sleep(0.5)
        
        # 두 번째 시퀀스: Tab 10번, Enter
        self.press_tab_multiple_times(10)
        self.press_enter()
        
        # 3초 대기
        time.sleep(3)
        
        # 세 번째 시퀀스: Tab 3번, Enter
        self.press_tab_multiple_times(3)
        self.press_enter()

if __name__ == "__main__":
    app = GammaApplication()
    app.run()
