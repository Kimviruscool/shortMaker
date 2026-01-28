# 같은 폴더(Download)에 있는 Validation 파일을 불러옵니다.
from Download.Validation import UrlValidator

class LinkManager:
    def __init__(self):
        self.validator = UrlValidator()

    def process_url(self, raw_url):
        """
        사용자가 입력한 URL을 받아 검증하고, 핵심 정보를 정리해서 반환합니다.
        """
        # 1. 검증 요청
        is_valid, data = self.validator.check(raw_url)

        if not is_valid:
            # 실패 시: status FAIL 리턴
            return {
                "status": "FAIL",
                "reason": data  # 에러 메시지
            }

        # 2. 데이터 정제 (우리가 필요한 것만 뽑기)
        # yt-dlp가 주는 정보가 너무 많으므로, 핵심만 추려냅니다.
        video_data = {
            "status": "PASS",
            "id": data.get('id'),
            "title": data.get('title', '제목 없음'),
            "url": data.get('webpage_url', raw_url), # 정규화된 URL
            "duration": data.get('duration', 0),
            "uploader": data.get('uploader', '알 수 없음')
        }

        return video_data