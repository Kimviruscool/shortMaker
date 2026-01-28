import yt_dlp
import os
import glob


class Downloader:
    def __init__(self):
        # 1. 결과물 저장 폴더
        self.output_folder = "Shorts_Result"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # 2. FFmpeg 경로 찾기 (프로젝트 최상위 폴더)
        # 현재 파일(VandT.py)의 상위 폴더(Download)의 상위 폴더(shortMaker)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        self.ffmpeg_path = os.path.join(project_root, "ffmpeg.exe")

        # FFmpeg가 실제로 있는지 확인
        if os.path.exists(self.ffmpeg_path):
            print(f"🔧 [V&T] FFmpeg 엔진 로드 완료: {self.ffmpeg_path}")
            self.has_ffmpeg = True
        else:
            print(f"⚠️ [V&T] 경고: ffmpeg.exe를 찾을 수 없습니다. (전체 다운로드 모드로 전환됩니다)")
            self.has_ffmpeg = False

    def process(self, url, start_time, duration=60):
        """
        FFmpeg를 사용하여 지정된 구간(start_time ~ +60초)만 잘라서 다운로드합니다.
        """
        # FFmpeg 유무에 따라 메시지가 달라짐
        if self.has_ffmpeg:
            print(f"⬇️ [V&T] 하이라이트 구간 다운로드 시작 ({start_time}초 ~ {start_time + duration}초)...")
        else:
            print(f"⬇️ [V&T] 전체 영상 다운로드 시작 (FFmpeg 없음)...")

        ydl_opts = {
            'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',

            # 자막 설정
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko'],
            'subtitlesformat': 'srt',

            'quiet': True,
            'no_warnings': True,

            # 안드로이드 모드 (접속 차단 방지)
            'extractor_args': {'youtube': {'player_client': ['android']}},
        }

        # ---------------------------------------------------------
        # [핵심] FFmpeg 설정 분기
        # ---------------------------------------------------------
        if self.has_ffmpeg:
            # 1. 고화질 + 자르기 모드
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',  # 최고 화질
                'ffmpeg_location': self.ffmpeg_path,  # FFmpeg 경로 지정
                'download_ranges': lambda info, ydl: [{  # 구간 자르기 설정
                    'start_time': start_time,
                    'end_time': start_time + duration
                }],
                'force_keyframes_at_cuts': True,  # 정확한 자르기(재인코딩)
            })
        else:
            # 2. 안전 모드 (전체 다운로드)
            ydl_opts.update({
                'format': 'best[ext=mp4]/best',  # 합쳐진 파일 우선
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # 파일명(확장자 제외) 추출
                base_name = os.path.splitext(os.path.basename(filename))[0]

                print(f"✅ [영상] 저장 완료!")

                # 자막 변환 실행
                self._convert_subtitle_to_txt(base_name)

                return True

        except Exception as e:
            print(f"❌ [오류] 다운로드 실패: {e}")
            return False

    def _convert_subtitle_to_txt(self, base_name):
        """
        .srt 파일을 .txt로 깔끔하게 변환
        """
        # 특수문자 등이 섞인 파일명을 위해 glob으로 검색
        search_pattern = os.path.join(self.output_folder, f"{glob.escape(base_name)}*.srt")
        srt_files = glob.glob(search_pattern)

        if not srt_files:
            return

        srt_path = srt_files[0]
        txt_path = srt_path.replace(".srt", ".txt")

        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            text_content = []
            for line in lines:
                line = line.strip()
                if line.isdigit() or '-->' in line or not line:
                    continue
                text_content.append(line)

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(text_content))

            print(f"✅ [자막] 텍스트 변환 완료")

        except Exception:
            pass