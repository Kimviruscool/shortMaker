import yt_dlp

class UrlValidator:
    def check(self, url):
        """
        URL 유효성 및 영상 존재 여부를 확인합니다.
        Return: (성공여부 Bool, 정보 Dict 또는 에러메시지 Str)
        """
        # 1. 1차 필터: 주소 문자열 검사
        if "youtube.com" not in url and "youtu.be" not in url:
            return False, "유튜브 링크가 아닙니다. (youtube.com 또는 youtu.be 포함 필수)"

        # 2. 2차 필터: 실제 데이터 조회 (다운로드 X, 메타데이터만)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extract_flat': True,  # 영상 전체 정보를 받지 않고 빠르게 체크
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    return False, "영상 정보를 가져올 수 없습니다."

                # 검증 성공 시 원본 정보(info) 반환
                return True, info

        except Exception as e:
            return False, f"접근 불가능한 영상입니다. ({str(e)})"