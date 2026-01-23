# downloader.py
import yt_dlp
import os
import re
import json


class VideoDownloader:
    def __init__(self, output_folder="downloads"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        self.output_folder = output_folder

        self.ydl_opts = {
            'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',
            'format': 'best[ext=mp4]',  # 단일 파일 최고화질 (ffmpeg 의존성 최소화)

            # 자막 설정
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko'],
            'subtitlesformat': 'srt',

            'quiet': True,
            'no_warnings': True,
            'cookiesfrombrowser': ('chrome',),

        }

    def _srt_to_json(self, srt_path):
        """SRT 파일을 n8n 스타일 JSON으로 변환"""
        if not os.path.exists(srt_path): return None

        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 정규식: "순번\n시작 --> 종료\n대사"
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
            text = re.sub(r'<[^>]+>', '', text)  # 태그 제거

            start = time_to_sec(start_str)
            end = time_to_sec(end_str)

            transcript_data.append({
                "start": start,
                "dur": round(end - start, 3),
                "text": text
            })

        # JSON 저장
        json_path = srt_path.replace('.srt', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        return json_path

    def process(self, url):
        """다운로드 실행 및 변환"""
        print(f"⬇️ [다운로드] 작업 시작... ({url})")

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                # 1. 다운로드 수행
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # 확장자 보정 (.mkv 등으로 받아질 경우 대비)
                base, ext = os.path.splitext(filename)
                if not os.path.exists(filename):
                    for e in ['.mp4', '.mkv', '.webm']:
                        if os.path.exists(base + e):
                            filename = base + e
                            break

                print(f"   ✅ 영상 저장: {filename}")

                # 2. 자막 변환
                srt_path = f"{base}.ko.srt"
                json_path = None

                if os.path.exists(srt_path):
                    json_path = self._srt_to_json(srt_path)
                    print(f"   ✅ 대사 추출: {json_path}")
                else:
                    print("   ⚠️ 자막 파일이 없어 대사 추출 생략")

                return True

            except Exception as e:
                print(f"❌ 다운로드 중 오류: {e}")
                return False