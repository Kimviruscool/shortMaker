import yt_dlp
import os
import glob
import sys
import time

# ---------------------------------------------------------
# 1. 경로 설정 (Flask 환경 호환성 강화)
# ---------------------------------------------------------
current_file_path = os.path.abspath(__file__)
download_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(download_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from Detour.Cookie import CookieManager
    from Detour.Phone import PhoneManager
except ImportError:
    print("⚠️ [V&T] Detour 모듈을 찾을 수 없습니다.")


    class CookieManager:
        def get_cookie_path(self): return None


    class PhoneManager:
        def get_client_mode(self, mode): return {}


class Downloader:
    def __init__(self):
        # 1. 저장 폴더 (절대 경로)
        self.output_folder = os.path.join(project_root, "Shorts_Result")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # 2. FFmpeg 경로
        self.ffmpeg_path = os.path.join(project_root, "ffmpeg.exe")
        self.has_ffmpeg = os.path.exists(self.ffmpeg_path)

        if not self.has_ffmpeg:
            print(f"⚠️ [V&T] FFmpeg 없음 (경로: {self.ffmpeg_path}) -> 전체 다운로드 모드")

        self.cookie_manager = CookieManager()
        self.phone_manager = PhoneManager()

    def process(self, url, start_time, duration=60):
        # 🚨 수정된 전략: 'web'을 1순위로 둡니다. (쿠키 적용 가능 모드)
        retry_strategies = ["web", "android", "ios"]

        cookie_path = self.cookie_manager.get_cookie_path()
        if cookie_path:
            print(f"🍪 [V&T] 쿠키 파일 발견: {cookie_path}")

        for attempt, mode in enumerate(retry_strategies, 1):
            print(f"\n🔄 [V&T] 다운로드 시도 {attempt}/{len(retry_strategies)}: 모드 '{mode}'")

            # PhoneManager는 web 모드일 때 빈 설정({})을 반환해야 함
            phone_args = self.phone_manager.get_client_mode(mode)

            # 모드별 쿠키 사용 여부 결정
            # android/ios는 쿠키를 지원하지 않으므로 web일 때만 쿠키를 넣음
            current_cookie = cookie_path if mode == "web" else None

            ydl_opts = {
                'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
                'cookiefile': current_cookie,
                'extractor_args': phone_args,

                'noplaylist': True,  # 플레이리스트 무시 (영상 1개만)

                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ko'],
                'subtitlesformat': 'srt',

                # 에러 디버깅용
                'quiet': False,
                'no_warnings': False,
            }

            if self.has_ffmpeg:
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'ffmpeg_location': self.ffmpeg_path,
                    'download_ranges': lambda info, ydl: [{
                        'start_time': start_time,
                        'end_time': start_time + duration
                    }],
                    'force_keyframes_at_cuts': True,
                })
            else:
                ydl_opts.update({'format': 'best[ext=mp4]/best'})

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    base_name = os.path.splitext(filename)[0]

                    print(f"✅ [성공] '{mode}' 모드로 다운로드 완료!")

                    txt_path = self._convert_subtitle_to_txt(base_name)
                    return txt_path if txt_path else None

            except Exception as e:
                print(f"💥 [다운로드 에러] 모드 '{mode}' 실패")
                # print(f"   내용: {e}") # 너무 긴 에러 로그 생략 가능

                if attempt < len(retry_strategies):
                    time.sleep(2)
                else:
                    return None

    def _convert_subtitle_to_txt(self, base_name_with_path):
        search_pattern = f"{glob.escape(base_name_with_path)}*.srt"
        srt_files = glob.glob(search_pattern)

        if not srt_files:
            return None

        srt_path = srt_files[0]
        txt_path = base_name_with_path + ".txt"

        try:
            text_content = []
            with open(srt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                clean = line.strip()
                if clean.isdigit() or '-->' in clean or not clean: continue
                if text_content and text_content[-1] == clean: continue
                text_content.append(clean)

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(text_content))

            return txt_path
        except:
            return None