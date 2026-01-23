# validator.py
import yt_dlp


class VideoValidator:
    def __init__(self):
        # 검증용 옵션 (다운로드 X, 메타데이터만 확인)
        self.check_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # 핵심: 다운로드 안 함 (속도 빠름, 차단 방지)
            'ignoreerrors': True,  # 에러 나도 멈추지 않음

            # 403 차단 방지 (모바일 앱 위장)
            'extractor_args': {'youtube': {'player_client': ['android']}},
            # 필요시 쿠키 사용 (주석 해제)
            # 'cookiesfrombrowser': ('chrome',), 
        }

    def validate(self, url):
        """
        URL을 받아 상태를 진단하고 리포트를 반환합니다.
        """
        print(f"🔍 [검증] 링크 유효성 확인 중... ({url})")

        with yt_dlp.YoutubeDL(self.check_opts) as ydl:
            try:
                # 1. 메타데이터 추출
                info = ydl.extract_info(url, download=False)

                # 2. 정보가 없으면 실패
                if not info:
                    return {'status': 'FAIL', 'reason': '정보 추출 불가 (비공개/삭제됨)'}

                # 3. 상세 정보 확인
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)

                # 자막 확인 (수동 or 자동)
                subs = info.get('subtitles', {})
                auto_subs = info.get('automatic_captions', {})
                has_kor_sub = ('ko' in subs) or ('ko' in auto_subs)

                # 4. 결과 리포트
                report = {
                    'status': 'PASS',
                    'url': url,
                    'title': title,
                    'duration': duration,
                    'has_kor_sub': has_kor_sub
                }

                # (추가 조건) 만약 자막이 필수라면 여기서 FAIL 처리 가능
                # if not has_kor_sub:
                #    report['status'] = 'FAIL'
                #    report['reason'] = '한국어 자막 없음'

                return report

            except Exception as e:
                return {'status': 'ERROR', 'reason': str(e)}