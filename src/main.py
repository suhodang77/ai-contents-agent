import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import shutil
import glob
from urllib.parse import urlparse, parse_qs
from .modules.video_to_text import VideoToText
from .modules.gemini_responder import GeminiResponder
from .modules.gamma_automator import GammaAutomator
from .modules.fliki_video_generator import FlikiVideoGenerator

# 기존 main.py의 상수와 함수들을 그대로 사용
DATA_DIR = "data"
GENERATED_TEXT_DIR = os.path.join(DATA_DIR, "generated_texts")
RESULT_DIR = os.path.join(DATA_DIR, "results")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_generated_script(content: str, filename: str):
    ensure_dir(GENERATED_TEXT_DIR)
    file_path = os.path.join(GENERATED_TEXT_DIR, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path
    except IOError as e:
        messagebox.showerror("파일 저장 오류", f"파일 저장 중 오류 발생 ('{file_path}'): {e}")
        return None

def get_latest_file(directory, extension):
    list_of_files = glob.glob(os.path.join(directory, f"*.{extension}"))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file

def reset_dir():
    if os.path.isdir(AUDIO_DIR):
        shutil.rmtree(AUDIO_DIR)
        
class AICreatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Contents Agent")
        self.geometry("800x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 1단계 입력 변수
        self.youtube_url = tk.StringVar()
        self.lecture_title = tk.StringVar()
        self.professor_name = tk.StringVar()
        self.difficulty_level = tk.StringVar(value="초")
        self.lecture_number = tk.StringVar()
        self.target_audience = tk.StringVar(value="일반인")

        # 단계별 결과 변수
        self.new_script = None
        self.script_path = None
        self.detail_path = None
        self.gamma_prompt_path = None
        self.ppt_path = None
        self.fliki_prompt_path = None
        self.video_path = None

        self._setup_ui()

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.step1_frame = ttk.Frame(self.notebook, padding="10")
        self.step2_frame = ttk.Frame(self.notebook, padding="10")
        self.step3_frame = ttk.Frame(self.notebook, padding="10")
        self.step4_frame = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.step1_frame, text="1단계: 정보 입력")
        self.notebook.add(self.step2_frame, text="2단계: 스크립트 확인")
        self.notebook.add(self.step3_frame, text="3단계: PPT 확인")
        self.notebook.add(self.step4_frame, text="4단계: 동영상 확인")

        self._create_step1_ui()
        self._create_step2_ui()
        self._create_step3_ui()
        self._create_step4_ui()
        
        self._go_to_step(1)

    def _create_step1_ui(self):
        # 1단계 UI 구성 (입력 필드)
        frame = self.step1_frame
        ttk.Label(frame, text="YouTube URL:").pack(pady=5, anchor="w")
        ttk.Entry(frame, textvariable=self.youtube_url).pack(fill="x", pady=2)
        
        ttk.Label(frame, text="강의 제목:").pack(pady=5, anchor="w")
        ttk.Entry(frame, textvariable=self.lecture_title).pack(fill="x", pady=2)
        
        ttk.Label(frame, text="교수명:").pack(pady=5, anchor="w")
        ttk.Entry(frame, textvariable=self.professor_name).pack(fill="x", pady=2)
        
        ttk.Label(frame, text="난이도:").pack(pady=5, anchor="w")
        level_frame = ttk.Frame(frame)
        level_frame.pack(fill="x", pady=2)
        for level in ["초", "중", "고"]:
            ttk.Radiobutton(level_frame, text=level, variable=self.difficulty_level, value=level).pack(side="left", padx=5)
            
        ttk.Label(frame, text="차시:").pack(pady=5, anchor="w")
        ttk.Entry(frame, textvariable=self.lecture_number).pack(fill="x", pady=2)
        
        ttk.Label(frame, text="학습 대상자:").pack(pady=5, anchor="w")
        audience_frame = ttk.Frame(frame)
        audience_frame.pack(fill="x", pady=2)
        for audience in ["초등학생", "중학생", "일반인"]:
            ttk.Radiobutton(audience_frame, text=audience, variable=self.target_audience, value=audience).pack(side="left", padx=5)

        ttk.Button(frame, text="다음", command=lambda: self._run_in_thread(self._step1_next)).pack(pady=20, fill="x")

    def _create_step2_ui(self):
        # 2단계 UI 구성 (스크립트 확인)
        frame = self.step2_frame
        ttk.Label(frame, text="생성된 스크립트 확인:").pack(pady=5, anchor="w")
        self.script_path_label = ttk.Label(frame, text="")
        self.script_path_label.pack(pady=2, anchor="w")
        ttk.Button(frame, text="스크립트 열기", command=lambda: os.startfile(self.script_path) if self.script_path else None).pack(pady=5, fill="x")
        
        ttk.Label(frame, text="상세 페이지 확인:").pack(pady=5, anchor="w")
        self.detail_path_label = ttk.Label(frame, text="")
        self.detail_path_label.pack(pady=2, anchor="w")
        ttk.Button(frame, text="상세 페이지 열기", command=lambda: os.startfile(self.detail_path) if self.detail_path else None).pack(pady=5, fill="x")

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20, fill="x")
        ttk.Button(button_frame, text="종료", command=self.destroy).pack(side="left", expand=True, padx=5)
        ttk.Button(button_frame, text="다음", command=lambda: self._run_in_thread(self._step2_next)).pack(side="right", expand=True, padx=5)

    def _create_step3_ui(self):
        # 3단계 UI 구성 (PPT 확인)
        frame = self.step3_frame
        ttk.Label(frame, text="생성된 PPT 확인 (PDF):").pack(pady=5, anchor="w")
        self.ppt_path_label = ttk.Label(frame, text="")
        self.ppt_path_label.pack(pady=2, anchor="w")
        ttk.Button(frame, text="PPT 열기", command=lambda: os.startfile(self.ppt_path) if self.ppt_path else None).pack(pady=5, fill="x")

        ttk.Label(frame, text="Gamma 입력 스크립트:").pack(pady=5, anchor="w")
        self.gamma_prompt_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
        self.gamma_prompt_text.pack(fill="both", expand=True, pady=5)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20, fill="x")
        ttk.Button(button_frame, text="종료", command=self.destroy).pack(side="left", expand=True, padx=5)
        ttk.Button(button_frame, text="다음", command=lambda: self._run_in_thread(self._step3_next)).pack(side="right", expand=True, padx=5)

    def _create_step4_ui(self):
        # 4단계 UI 구성 (동영상 확인)
        frame = self.step4_frame
        ttk.Label(frame, text="생성된 동영상 확인:").pack(pady=5, anchor="w")
        self.video_path_label = ttk.Label(frame, text="")
        self.video_path_label.pack(pady=2, anchor="w")
        ttk.Button(frame, text="동영상 열기", command=lambda: os.startfile(self.video_path) if self.video_path else None).pack(pady=5, fill="x")

        ttk.Label(frame, text="Fliki 입력 프롬프트:").pack(pady=5, anchor="w")
        self.fliki_prompt_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
        self.fliki_prompt_text.pack(fill="both", expand=True, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20, fill="x")
        ttk.Button(button_frame, text="종료", command=self.destroy).pack(side="left", expand=True, padx=5)
        
    def _run_in_thread(self, target_function):
        self._show_progress_window()
        threading.Thread(target=target_function, daemon=True).start()

    def _show_progress_window(self):
        self.progress_win = tk.Toplevel(self)
        self.progress_win.title("진행 상황")
        self.progress_win.geometry("400x150")
        self.progress_win.transient(self)
        self.progress_win.grab_set()

        self.progress_label = ttk.Label(self.progress_win, text="준비 중...", font=("Helvetica", 12))
        self.progress_label.pack(pady=20)
        self.progress_bar = ttk.Progressbar(self.progress_win, orient="horizontal", length=300, mode="indeterminate")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()

    def _update_progress(self, message):
        if hasattr(self, "progress_label"):
            self.progress_label.config(text=message)
            self.progress_win.update()
        
    def _hide_progress_window(self):
        if hasattr(self, "progress_win"):
            self.progress_bar.stop()
            self.progress_win.destroy()

    def on_closing(self):
        if hasattr(self, "progress_win") and self.progress_win.winfo_exists():
            self.progress_win.destroy()
        self.destroy()

    def _step1_next(self):  
        try:
            self._update_progress("입력 값 유효성 검사...")
            url = self.youtube_url.get()
            if not url:
                messagebox.showerror("입력 오류", "YouTube URL을 입력해주세요.")
                self._hide_progress_window()
                return

            self._update_progress("1. YouTube 동영상 스크립트 추출 시작...")
            video_to_text = VideoToText()
            if not video_to_text.download_youtube_audio(url):
                messagebox.showerror("오류", "YouTube 오디오 다운로드에 실패했습니다.")
                self._hide_progress_window()
                return
            original_script = video_to_text.get_script()
            
            self._update_progress("2. 새로운 동영상 스크립트 생성 시작...")
            script_responder = GeminiResponder(prompt_mode="script", target_audience=self.target_audience.get())
            # --- 수정된 부분 ---
            self.new_script = script_responder.generate_response(
                script=original_script,
                lecture_title=self.lecture_title.get(),
                professor_name=self.professor_name.get()
            )
            # --- 여기까지 ---
            if not self.new_script:
                messagebox.showerror("오류", "새로운 스크립트를 생성하지 못했습니다.")
                self._hide_progress_window()
                return
            self.script_path = save_generated_script(self.new_script, "generated_script.txt")
            
            self._update_progress("3. 상세 페이지 생성 시작...")
            detail_responder = GeminiResponder(prompt_mode="detail", target_audience=self.target_audience.get())
            # --- 수정된 부분 ---
            detail_page_content = detail_responder.generate_response(
                lecture_title=self.lecture_title.get(),
                script=self.new_script,
                professor_name=self.professor_name.get()
            )
            # --- 여기까지 ---
            if not detail_page_content:
                messagebox.showerror("오류", "상세 페이지 내용을 생성하지 못했습니다.")
                self._hide_progress_window()
                return
            self.detail_path = save_generated_script(detail_page_content, "detail_page.txt")

            self.script_path_label.config(text=f"파일 경로: {self.script_path}")
            self.detail_path_label.config(text=f"파일 경로: {self.detail_path}")

            self._hide_progress_window()
            self._go_to_step(2)
        except Exception as e:
            self._hide_progress_window()
            messagebox.showerror("오류", f"1단계 처리 중 오류 발생: {e}")
            
    def _step2_next(self):
        try:
            self._update_progress("4. Gamma를 사용하여 PPT 생성 시작...")
            gamma_automator = GammaAutomator()
            
            self._update_progress("   - Gamma 로그인 대기 중...")
            if not gamma_automator.login():
                messagebox.showerror("오류", "Gamma 로그인에 실패했습니다.")
                return
            
            self._update_progress("   - PPT 스크립트 파일 저장...")
            self.gamma_prompt_path = save_generated_script(self.new_script, "gamma_input_prompt.txt")
            if not self.gamma_prompt_path:
                self.gamma_prompt_path = "(저장 실패)"
            
            self._update_progress("   - PPT 생성 자동화 시작...")
            gamma_automator.create_ppt_from_script(self.new_script)
            
            self._update_progress("   - 생성된 PDF 파일 확인...")
            # 수정: Gamma 결과물 폴더 경로로 변경
            self.ppt_path = get_latest_file(RESULT_DIR, "pdf")
            if not self.ppt_path:
                messagebox.showerror("오류", "생성된 PDF 파일을 찾을 수 없습니다.")
                return

            self.ppt_path_label.config(text=f"파일 경로: {self.ppt_path}")
            
            self.gamma_prompt_text.delete("1.0", tk.END)
            with open(self.gamma_prompt_path, 'r', encoding='utf-8') as f:
                self.gamma_prompt_text.insert(tk.END, f.read())

            self._hide_progress_window()
            self._go_to_step(3)
        except Exception as e:
            self._hide_progress_window()
            messagebox.showerror("오류", f"2단계 처리 중 오류 발생: {e}")
        finally:
            if hasattr(gamma_automator, "driver") and gamma_automator.driver:
                gamma_automator.driver.quit()

    def _step3_next(self):
        try:
            self._update_progress("5. Fliki를 사용하여 동영상 생성 시작...")
            fliki_generator = FlikiVideoGenerator(
                target_audience=self.target_audience.get(),
                lecture_title=self.lecture_title.get(),
            )
            
            self._update_progress("   - Fliki 로그인 대기 중...")
            if not fliki_generator.login():
                messagebox.showerror("오류", "Fliki 로그인에 실패했습니다.")
                return
            
            self._update_progress("   - Fliki 프롬프트 파일 저장...")
            fliki_prompt_content = fliki_generator.BASE_SCRIP.format(
                target_audience=self.target_audience.get(),
                lecture_title=self.lecture_title.get()
            )
            self.fliki_prompt_path = save_generated_script(fliki_prompt_content, "fliki_input_prompt.txt")
            if not self.fliki_prompt_path:
                self.fliki_prompt_path = "(저장 실패)"
            
            self._update_progress("   - 동영상 생성 자동화 시작...")
            video_generated = fliki_generator.generate_video_from_ppt(
                ppt_file_path=self.ppt_path
            )
            if not video_generated:
                messagebox.showerror("오류", "동영상 생성 프로세스에 실패했습니다.")
                return
            
            self._update_progress("   - 동영상 다운로드 대기 중...")
            # 수정: Fliki 결과물 폴더 경로로 변경
            self.video_path = get_latest_file(RESULT_DIR, "mp4")

            self.video_path_label.config(text=f"파일 경로: {self.video_path}")

            self.fliki_prompt_text.delete("1.0", tk.END)
            with open(self.fliki_prompt_path, 'r', encoding='utf-8') as f:
                self.fliki_prompt_text.insert(tk.END, f.read())
            
            self._hide_progress_window()
            self._go_to_step(4)
        except Exception as e:
            self._hide_progress_window()
            messagebox.showerror("오류", f"3단계 처리 중 오류 발생: {e}")
        finally:
            if hasattr(fliki_generator, "driver") and fliki_generator.driver:
                fliki_generator.driver.quit()

    def _go_to_step(self, step_number):
        for i in range(4):
            if (i + 1) == step_number:
                self.notebook.tab(i, state="normal")
                self.notebook.select(i)
            elif (i + 1) < step_number:
                self.notebook.tab(i, state="normal")
            else:
                self.notebook.tab(i, state="disabled")

if __name__ == "__main__":
    reset_dir()
    ensure_dir(DATA_DIR)
    ensure_dir(RESULT_DIR)
    ensure_dir(AUDIO_DIR)
    ensure_dir(GENERATED_TEXT_DIR)
    # 수정: Gamma와 Fliki의 새로운 폴더도 생성
    # ensure_dir(os.path.join(RESULT_DIR, "gamma_pdfs"))
    # ensure_dir(os.path.join(RESULT_DIR, "fliki_videos"))
    app = AICreatorGUI()
    app.mainloop()