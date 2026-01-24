import yt_dlp
import os
import re
import json
import sys


class VideoDownloader:
    def __init__(self, output_folder="Shorts_Result"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        self.output_folder = output_folder

        # ------------------------------------------------------------
        # 🔧 FFmpeg 위치 찾기 (절대 경로)
        # ------------------------------------------------------------
        current_file_path = os.path.abspath(__file__)
        downloads_dir = os.path.dirname(current_file_path)
        project_root = os.path.dirname(downloads_dir)

        ffmpeg_binary_path = os.path.join(project_root, "ffmpeg.exe")

        if not os.path.exists(ffmpeg_binary_path):
            print(f"⚠️ [경고] FFmpeg 파일을 찾을 수 없습니다: {ffmpeg_binary_path}")
        else:
            print(f"🔧 FFmpeg 감지됨: {ffmpeg_binary_path}")

        # ------------------------------------------------------------
        # 다운로드 옵션 설정
        # ------------------------------------------------------------
        self.ydl_opts_base = {
            'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',

            # 🚨 [수정 완료] 이제 FFmpeg가 있으므로, '최고화질(분리형)'을 요청합니다.
            # 이 설정이 있어야 'Requested format is not available' 에러가 사라집니다.
            'format': 'bestvideo+bestaudio/best',

            # FFmpeg 위치 지정
            'ffmpeg_location': ffmpeg_binary_path,

            # 합치기 및 mp4 변환 설정
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],

            # 자막 및 기타 설정
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko'],
            'subtitlesformat': 'srt',
            'quiet': True,
            'no_warnings': True,
            'cookiefile': os.path.join(project_root, 'cookies.txt'),
            'extractor_args': {'youtube': {'player_client': ['web']}},
        }

    def _srt_to_json(self, srt_path):
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
        print(f"⬇️ [다운로드] {start_time}초 ~ {start_time + duration}초 구간 추출 중...")

        opts = self.ydl_opts_base.copy()
        opts['download_ranges'] = lambda info, ydl: [{
            'start_time': start_time,
            'end_time': start_time + duration
        }]
        opts['force_keyframes_at_cuts'] = True

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                base, ext = os.path.splitext(filename)
                final_filename = f"{base}.mp4"

                if os.path.exists(final_filename):
                    print(f"   ✅ 영상 저장: {final_filename}")
                elif os.path.exists(filename):
                    print(f"   ✅ 영상 저장: {filename}")

                srt_path = f"{base}.ko.srt"
                json_path = None

                if os.path.exists(srt_path):
                    json_path = self._srt_to_json(srt_path)
                    print(f"   ✅ 대사 추출: {json_path}")
                else:
                    # 폴더 내 검색 (파일명 불일치 대비)
                    for file in os.listdir(self.output_folder):
                        if file.endswith(".ko.srt") and base in os.path.join(self.output_folder, file):
                            json_path = self._srt_to_json(os.path.join(self.output_folder, file))
                            print(f"   ✅ 대사 추출(재검색): {json_path}")
                            break
                    if not json_path:
                        print("   ⚠️ 자막 파일이 생성되지 않았습니다.")

                return True

            except Exception as e:
                print(f"❌ 다운로드 오류: {e}")
                return False