import yt_dlp
import os
import glob
import sys
import time

# ---------------------------------------------------------
# 1. 경로 설정 (Flask 환경 호환성 강화)
# ---------------------------------------------------------
# 현재 파일(VandT.py)의 위치: .../Download/VandT.py
current_file_path = os.path.abspath(__file__)
# 부모 폴더(Download): .../Download
download_dir = os.path.dirname(current_file_path)
# 프로젝트 루트(shortMaker): .../
project_root = os.path.dirname(download_dir)

# 모듈 경로 추가
if project_root not in sys.path:
    sys.path.append(project_root)

# Detour 모듈 불러오기
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
        # 1. 저장 폴더 설정 (프로젝트 루트 기준 절대 경로)
        self.output_folder = os.path.join(project_root, "Shorts_Result")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"📁 [V&T] 결과 폴더 생성: {self.output_folder}")

        # 2. FFmpeg 경로 설정 (프로젝트 루트 기준)
        self.ffmpeg_path = os.path.join(project_root, "ffmpeg.exe")
        self.has_ffmpeg = os.path.exists(self.ffmpeg_path)

        if self.has_ffmpeg:
            print(f"🔧 [V&T] FFmpeg 감지됨: {self.ffmpeg_path}")
        else:
            print(f"⚠️ [V&T] FFmpeg 파일을 찾을 수 없습니다. (경로: {self.ffmpeg_path})")
            print("   👉 전체 영상을 다운로드하게 되며 속도가 느릴 수 있습니다.")

        # 3. 매니저 초기화
        self.cookie_manager = CookieManager()
        self.phone_manager = PhoneManager()

    def process(self, url, start_time, duration=60):
        # 재시도 전략
        retry_strategies = ["android", "ios"]

        # 쿠키 경로 가져오기
        cookie_path = self.cookie_manager.get_cookie_path()
        if cookie_path:
            print(f"🍪 [V&T] 쿠키 파일 적용: {cookie_path}")
        else:
            print("⚠️ [V&T] 쿠키 파일 없이 진행합니다.")

        for attempt, mode in enumerate(retry_strategies, 1):
            print(f"\n🔄 [V&T] 다운로드 시도 {attempt}/{len(retry_strategies)}: 모드 '{mode}'")

            # 폰 설정 가져오기
            phone_args = self.phone_manager.get_client_mode(mode)

            # yt-dlp 옵션 설정
            ydl_opts = {
                'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),  # 절대 경로 사용
                'cookiefile': cookie_path,
                'extractor_args': phone_args,

                # 자막 관련 설정
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ko'],
                'subtitlesformat': 'srt',

                # 로그 관련
                'quiet': False,  # 디버깅을 위해 켬 (에러 확인용)
                'no_warnings': False,
            }

            # FFmpeg 설정 (구간 추출)
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
                # FFmpeg 없으면 전체 다운로드
                ydl_opts.update({'format': 'best[ext=mp4]/best'})

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                    # 확장자를 제외한 파일명 추출 (경로 포함)
                    base_name = os.path.splitext(filename)[0]

                    print(f"✅ [성공] '{mode}' 모드로 다운로드 완료!")

                    # 자막 변환 시도
                    txt_path = self._convert_subtitle_to_txt(base_name)

                    if txt_path:
                        return txt_path
                    else:
                        print("⚠️ [주의] 영상은 받았으나 자막(TXT) 생성에 실패했습니다.")
                        # 자막이 없더라도 영상 다운로드가 성공했다면 여기서 멈출지,
                        # 아니면 None을 리턴할지 결정해야 합니다.
                        # 현재 로직상 AI 분석을 위해 None을 리턴합니다.
                        return None

            except Exception as e:
                print(f"💥 [다운로드 에러] 모드 '{mode}' 실패.")
                print(f"   👉 에러 내용: {e}")  # 상세 에러 출력

                if attempt < len(retry_strategies):
                    print("   👉 2초 후 다음 모드로 시도합니다...")
                    time.sleep(2)
                else:
                    print("❌ [최종 실패] 모든 다운로드 시도가 막혔습니다.")
                    return None

    def _convert_subtitle_to_txt(self, base_name_with_path):
        """
        다운로드된 .srt 파일을 찾아 .txt로 변환합니다.
        base_name_with_path: 경로가 포함된 파일명 (확장자 제외)
        """
        # glob 패턴 매칭을 위해 특수문자 이스케이프 처리
        # base_name_with_path 자체가 절대 경로이므로 join 불필요
        search_pattern = f"{glob.escape(base_name_with_path)}*.srt"

        print(f"🔍 [자막 검색] 패턴: {search_pattern}")
        srt_files = glob.glob(search_pattern)

        if not srt_files:
            print("❌ [자막] .srt 파일을 찾을 수 없습니다.")
            return None

        # 가장 첫 번째 발견된 자막 파일 사용
        srt_path = srt_files[0]
        txt_path = base_name_with_path + ".txt"

        try:
            text_content = []
            with open(srt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # SRT 포맷 파싱 (타임스탬프 제거하고 텍스트만 추출)
            for line in lines:
                clean_line = line.strip()
                # 숫자만 있거나, 타임스탬프(-->)가 포함된 줄은 건너뜀
                if clean_line.isdigit(): continue
                if '-->' in clean_line: continue
                if not clean_line: continue

                # 중복 대사 제거 (선택사항)
                if text_content and text_content[-1] == clean_line:
                    continue

                text_content.append(clean_line)

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(text_content))

            print(f"✅ [자막] 텍스트 변환 완료: {os.path.basename(txt_path)}")
            return txt_path

        except Exception as e:
            print(f"❌ [자막] 변환 중 에러 발생: {e}")
            return None