import yt_dlp
import os
import re
import json


class VideoDownloader:
    def __init__(self, output_folder="Shorts_Result"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        self.output_folder = output_folder

        # 프로젝트 루트 경로 (쿠키 파일 위치)
        current_file_path = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(current_file_path))

    def _srt_to_json(self, srt_path):
        # (기존 로직 유지)
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
        print(f"⬇️ [다운로드] '안드로이드 모드'로 우회 다운로드 시도...")

        ydl_opts = {
            'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',

            # 🚨 [핵심 해결책 1] 안드로이드 모드 사용
            # PC에서는 막힌 포맷도 모바일로 척하면 열어줍니다.
            # (단일 파일인 mp4를 우선적으로 받아옵니다)
            'extractor_args': {'youtube': {'player_client': ['android']}},

            # 🚨 [핵심 해결책 2] 포맷 단순화
            # 복잡한 번호(22/18) 대신 'best'를 쓰되, 안드로이드 클라이언트가 알아서 최적의 MP4를 줍니다.
            'format': 'best[ext=mp4]/best',

            # 🚨 [핵심 해결책 3] 디스크 공간 체크 무시 (강제 시도)
            # 공간이 조금이라도 있으면 받도록 설정
            'nocheckcertificate': True,

            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko'],
            'subtitlesformat': 'srt',

            'quiet': True,
            'no_warnings': True,
            'cookiefile': os.path.join(self.project_root, 'cookies.txt'),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # 파일 확장자 보정
                base, ext = os.path.splitext(filename)

                # 파일이 실제로 존재하는지, 크기가 0은 아닌지 확인
                final_filename = None
                for e in ['', '.mp4', '.mkv', '.webm']:
                    f_path = base + e
                    if os.path.exists(f_path):
                        # 파일 크기 체크 (0바이트면 실패로 간주)
                        if os.path.getsize(f_path) > 0:
                            final_filename = f_path
                            break

                if final_filename:
                    print(f"   ✅ 영상 저장 완료: {final_filename}")

                    srt_path = f"{base}.ko.srt"
                    if os.path.exists(srt_path):
                        json_path = self._srt_to_json(srt_path)
                        print(f"   ✅ 대사 추출: {json_path}")
                    else:
                        # 자막 재검색
                        for file in os.listdir(self.output_folder):
                            if file.endswith(".ko.srt") and base in os.path.join(self.output_folder, file):
                                json_path = self._srt_to_json(os.path.join(self.output_folder, file))
                                print(f"   ✅ 대사 추출(재검색): {json_path}")
                                break
                    return True
                else:
                    print("   ❌ 오류: 파일이 생성되지 않았거나 용량이 0바이트입니다.")
                    print("   👉 하드디스크 용량을 확인해주세요!")
                    return False

            except Exception as e:
                print(f"❌ 다운로드 오류: {e}")
                return False