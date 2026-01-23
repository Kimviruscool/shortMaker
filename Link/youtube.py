import yt_dlp
import sys


class VideoValidator:
    def __init__(self):
        # 검증용 옵션 (다운로드 X, 메타데이터만 확인)
        self.check_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # 핵심: 절대 다운로드하지 않음 (속도 빠름)
            'ignoreerrors': True,  # 에러가 나도 멈추지 않고 결과 반환
            'dump_single_json': True,

            # 403 차단 방지를 위한 최소한의 위장
            'extractor_args': {'youtube': {'player_client': ['android']}},
        }

    def check_video(self, url):
        """
        URL을 받아서 작업 가능한지(Alive) 상태를 진단서로 끊어줍니다.
        """
        print(f"🔍 [검증 시작] 링크 확인 중... ({url})")

        with yt_dlp.YoutubeDL(self.check_opts) as ydl:
            try:
                # 1. 메타데이터 추출 시도
                info = ydl.extract_info(url, download=False)

                # 2. 정보가 None이면 실패 (비공개, 삭제됨, 차단됨 등)
                if not info:
                    return {'status': 'FAIL', 'reason': '정보를 가져올 수 없음 (비공개/삭제/차단)'}

                # 3. 필요한 정보 확인
                video_id = info.get('id')
                title = info.get('title')
                duration = info.get('duration')
                is_live = info.get('is_live', False)

                # 자막 유무 확인 (자동 생성 자막 포함)
                subtitles = info.get('subtitles', {})
                auto_subs = info.get('automatic_captions', {})
                has_subs = len(subtitles) > 0 or len(auto_subs) > 0

                # 한국어 자막 여부 체크
                has_kor_sub = ('ko' in subtitles) or ('ko' in auto_subs)

                # 4. 검증 리포트 작성
                report = {
                    'status': 'PASS',
                    'id': video_id,
                    'title': title,
                    'duration': duration,
                    'is_live': is_live,
                    'has_subs': has_subs,
                    'has_kor_sub': has_kor_sub,
                    'url': url
                }

                # 5. 쇼츠(Shorts)인지 일반 영상인지 판단 (1분 미만 & 세로 비율 등)
                # (메타데이터에 정확한 플래그가 없을 때가 많아 시간으로 1차 추정)
                if duration and duration <= 60:
                    report['type'] = 'SHORTS'
                else:
                    report['type'] = 'VIDEO'

                return report

            except Exception as e:
                return {'status': 'ERROR', 'reason': str(e)}


# ================= 실행 로직 =================
if __name__ == "__main__":
    validator = VideoValidator()

    while True:
        url = input("\n👉 검증할 유튜브 링크 (종료: q): ").strip()
        if url.lower() in ['q', 'exit']: break
        if not url: continue

        result = validator.check_video(url)

        print("\n" + "=" * 40)
        if result['status'] == 'PASS':
            print(f"✅ [검증 통과] 추출 가능합니다!")
            print(f"   - 제목: {result['title']}")
            print(f"   - 타입: {result['type']}")
            print(f"   - 시간: {result['duration']}초")
            print(f"   - 자막: {'있음' if result['has_subs'] else '❌ 없음 (추출 불가)'}")
            print(f"   - 한글자막: {'⭕ 지원함' if result['has_kor_sub'] else '⚠️ 없음 (번역 필요)'}")
        else:
            print(f"🚫 [검증 실패] 작업을 진행할 수 없습니다.")
            print(f"   - 이유: {result['reason']}")
        print("=" * 40)