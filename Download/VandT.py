import yt_dlp
import os
import glob
import sys
import time

# ---------------------------------------------------------
# 1. Detour 모듈 불러오기
# ---------------------------------------------------------
current_file_path = os.path.abspath(__file__)
download_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(download_dir)
sys.path.append(project_root)

try:
    from Detour.Cookie import CookieManager
    from Detour.Phone import PhoneManager
except ImportError:
    class CookieManager:
        def get_cookie_path(self): return None


    class PhoneManager:
        def get_client_mode(self, mode): return {}


class Downloader:
    def __init__(self):
        # 저장 폴더
        self.output_folder = "Shorts_Result"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # FFmpeg 경로
        self.ffmpeg_path = os.path.join(project_root, "ffmpeg.exe")
        self.has_ffmpeg = os.path.exists(self.ffmpeg_path)

        if self.has_ffmpeg:
            print(f"🔧 [V&T] FFmpeg 로드 완료")
        else:
            print(f"⚠️ [V&T] FFmpeg 없음 (전체 다운로드 모드)")

        # Detour 매니저 초기화
        self.cookie_manager = CookieManager()
        self.phone_manager = PhoneManager()

    def process(self, url, start_time, duration=60):
        # ---------------------------------------------------------
        # [재시도 전략] Android 1회 -> 실패시 -> iOS 1회
        # ---------------------------------------------------------
        retry_strategies = ["android", "ios"]

        # 쿠키는 공통으로 사용 (없으면 봇 실행됨)
        cookie_path = self.cookie_manager.get_cookie_path()

        for attempt, mode in enumerate(retry_strategies, 1):
            print(f"\n🔄 [V&T] 다운로드 시도 {attempt}/{len(retry_strategies)}: 모드 '{mode}'")

            # 1. 현재 모드에 맞는 '폰 설정' 가져오기
            phone_args = self.phone_manager.get_client_mode(mode)

            # 2. 옵션 설정
            ydl_opts = {
                'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',
                'cookiefile': cookie_path,  # 쿠키 적용
                'extractor_args': phone_args,  # 폰 모드 적용 (Android/iOS)

                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ko'],
                'subtitlesformat': 'srt',
                'quiet': True,
                'no_warnings': True,
            }

            # FFmpeg 설정
            if self.has_ffmpeg:
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best',
                    'ffmpeg_location': self.ffmpeg_path,
                    'download_ranges': lambda info, ydl: [{
                        'start_time': start_time,
                        'end_time': start_time + duration
                    }],
                    'force_keyframes_at_cuts': True,
                })
            else:
                ydl_opts.update({'format': 'best[ext=mp4]/best'})

            # 3. 다운로드 실행 (Try-Except)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    base_name = os.path.splitext(os.path.basename(filename))[0]

                    print(f"✅ [성공] '{mode}' 모드로 다운로드 완료!")
                    self._convert_subtitle_to_txt(base_name)
                    return True  # 성공하면 즉시 함수 종료

            except Exception as e:
                print(f"💥 [실패] '{mode}' 모드 차단됨 또는 오류: {e}")
                if attempt < len(retry_strategies):
                    print("   👉 다음 모드로 우회 시도합니다...")
                    time.sleep(2)  # 잠시 대기
                else:
                    print("❌ [최종 실패] 모든 우회 수단이 막혔습니다.")
                    return False

    def _convert_subtitle_to_txt(self, base_name):
        # (기존 자막 변환 코드와 동일)
        search_pattern = os.path.join(self.output_folder, f"{glob.escape(base_name)}*.srt")
        srt_files = glob.glob(search_pattern)
        if not srt_files: return
        try:
            with open(srt_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
            text_content = []
            for line in lines:
                l = line.strip()
                if l.isdigit() or '-->' in l or not l: continue
                text_content.append(l)
            txt_path = srt_files[0].replace(".srt", ".txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(text_content))
            print(f"✅ [자막] 변환 완료")
        except:
            pass