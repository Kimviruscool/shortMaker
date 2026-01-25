import yt_dlp
import os
import re
import json


class VideoDownloader:
    def __init__(self, output_folder="Shorts_Result"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        self.output_folder = output_folder

        # FFmpeg 경로 찾는 코드 삭제함 (필요 없음)
        # ------------------------------------------------------------

        # 📂 프로젝트 루트 경로 (쿠키 파일 찾기용)
        current_file_path = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(current_file_path))

    def _srt_to_json(self, srt_path):
        # 자막 변환 로직 (기존과 동일)
        if not os.path.exists(srt_path): return None
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)',
                             re.DOTALL)
        matches = pattern.findall(content)
        transcript_data = []

        def time_to_sec(t_str):
            h, m, s = t_str.replace(',', '.').split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)

        for match in matches:
            _, start_str, end_str, text = match
            text = text.replace('\n', ' ').strip()
            text = re.sub(r'<[^>]+>', '', text)
            start = time_to_sec(start_str)
            end = time_to_sec(end_str)
            transcript_data.append({"start": start, "dur": round(end - start, 3), "text": text})
        json_path = srt_path.replace('.srt', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        return json_path

    def process(self, url, start_time=0, duration=60):
        # 🚨 [중요] FFmpeg가 없으므로 '구간 자르기(start_time)'를 무시합니다.
        print(f"⬇️ [다운로드] FFmpeg 없이 전체 영상 다운로드 시작...")
        print(f"   (참고: 자르기 기능은 작동하지 않습니다)")

        ydl_opts = {
            'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',

            # 🚨 [핵심 설정]
            # 1. 'best': 합쳐져 있는 파일 중 제일 좋은 거 (보통 720p)
            # 2. [ext=mp4]: 그 중에서 MP4인 것만 (WebM 피하기 위해)
            'format': 'best[ext=mp4]/best',

            # 자르기 옵션(download_ranges) 삭제함 -> 에러 원인 제거

            # 자막 설정
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko'],
            'subtitlesformat': 'srt',

            'quiet': True,
            'no_warnings': True,
            'cookiefile': os.path.join(self.project_root, 'cookies.txt'),
            'extractor_args': {'youtube': {'player_client': ['web']}},
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # 파일 확장자 확인
                base, ext = os.path.splitext(filename)

                # 혹시 mkv나 webm으로 받아졌을 경우를 대비해 파일 찾기
                final_filename = filename
                if not os.path.exists(final_filename):
                    for e in ['.mp4', '.mkv', '.webm']:
                        if os.path.exists(base + e):
                            final_filename = base + e
                            break

                print(f"   ✅ 영상 저장 완료: {final_filename}")

                srt_path = f"{base}.ko.srt"
                json_path = None

                if os.path.exists(srt_path):
                    json_path = self._srt_to_json(srt_path)
                    print(f"   ✅ 대사 추출: {json_path}")
                else:
                    # 유사 파일 찾기
                    for file in os.listdir(self.output_folder):
                        if file.endswith(".ko.srt") and base in os.path.join(self.output_folder, file):
                            json_path = self._srt_to_json(os.path.join(self.output_folder, file))
                            print(f"   ✅ 대사 추출(재검색): {json_path}")
                            break
                return True

            except Exception as e:
                print(f"❌ 다운로드 오류: {e}")
                return False