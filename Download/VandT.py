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
                # ... (앞부분 import 및 클래스 선언 동일) ...

                # 3. 다운로드 실행 (Try-Except)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        base_name = os.path.splitext(os.path.basename(filename))[0]

                        print(f"✅ [성공] '{mode}' 모드로 다운로드 완료!")

                        # 🚨 수정된 부분: 텍스트 파일 경로를 받아서 반환합니다.
                        txt_path = self._convert_subtitle_to_txt(base_name)

                        if txt_path:
                            return txt_path  # 성공 시 파일 경로 반환
                        else:
                            # 영상은 받았는데 자막이 없는 경우도 성공으로 칠지 결정 필요
                            # 일단은 텍스트가 없으면 다음 단계 진행이 안 되니 False로 둡니다.
                            print("❌ [실패] 영상은 받았으나 텍스트 추출에 실패했습니다.")
                            return None

                except Exception as e:
                    print(f"💥 [실패] '{mode}' 모드 차단됨 또는 오류: {e}")
                    if attempt < len(retry_strategies):
                        print("   👉 다음 모드로 우회 시도합니다...")
                        time.sleep(2)
                    else:
                        print("❌ [최종 실패] 모든 우회 수단이 막혔습니다.")
                        return None  # 최종 실패 시 None 반환

            def _convert_subtitle_to_txt(self, base_name):
                # ... (검색 로직 동일) ...
                search_pattern = os.path.join(self.output_folder, f"{glob.escape(base_name)}*.srt")
                srt_files = glob.glob(search_pattern)
                if not srt_files: return None  # None 반환

                # ... (변환 로직 동일) ...
                try:
                    # ... (파일 읽기/쓰기 동일) ...
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write("\n".join(text_content))

                    print(f"✅ [자막] 변환 완료: {os.path.basename(txt_path)}")
                    return txt_path  # 🚨 중요: 생성된 .txt 파일의 절대 경로를 반환

                except:
                    return None