import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import yt_dlp

load_dotenv()


class VideoToText:
    def __init__(self, api_key=None, model_name: str = "gemini-2.5-flash-preview-05-20"):
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("GOOGLE_API_KEY")
            if not self.api_key:
                self.api_key = os.environ.get("GEMINI_API_KEY")
            if not self.api_key: 
                raise ValueError(
                    "Error: API 키가 환경 변수로 설정되지 않았습니다. GOOGLE_API_KEY 환경 변수를 설정하거나 api_key 매개변수를 통해 설정하세요."
                )

        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        
    def download_youtube_audio(self, youtube_url: str) -> str:
        ydl_opts = {
            "format": "worst",
            "extractaudio": True,
            "overwrites": True,
            "downloader": "aria2c",
            "audioformat": "wav",
            "outtmpl": os.path.join("data", "script", "lecture_audio.wav"),
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result_code = ydl.download(youtube_url)
        
        if result_code == 0:
            print("[오디오 다운로드 완료]\n")
            return True

    def get_script(self) -> str:
        contents: list[types.Content] = [
            "첨부한 오디오 파일의 스크립트를 추출해주세요. 스크립트 외의 다른 출력이 답변에 포함되지 않도록 해주세요.",
            self.client.files.upload(
                file=os.path.join("data", "script", "lecture_audio.wav")
            ),
        ]
        generate_content_config: types.GenerateContentConfig = (
            types.GenerateContentConfig(
                response_mime_type="text/plain",
            )
        )

        script_chunks = []
        for chunk in self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="", flush=True)
            script_chunks.append(chunk.text)
        print("\n[스크립트 추출 완료]")
        os.remove(os.path.join("data", "script", "lecture_audio.wav"))
        return "".join(script_chunks)


if __name__ == "__main__":
    video_to_text = VideoToText()
    if video_to_text.download_youtube_audio(
        "https://www.youtube.com/watch?v=k-vamAL8hEo"
    ):
        video_to_text.get_script()