import requests
import re
import json


def get_heatmap_peak(video_url):
    """
    유튜브 영상의 히트맵(가장 많이 본 구간) 데이터를 분석하여
    가장 인기 있는 시간(초 단위)을 반환합니다.

    Returns:
        int: 피크 시간(초). 데이터가 없으면 None 반환.
    """
    try:
        # 봇 탐지 회피용 헤더
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        response = requests.get(video_url, headers=headers, timeout=10)
        html = response.text

        # HTML 내부에 숨겨진 'heatMarkers' JSON 데이터 찾기
        # (유튜브 데이터 구조는 복잡해서 정규식으로 낚아채는 게 가장 빠릅니다)
        match = re.search(r'\"heatMarkers\":\s*(\[[^\]]+\])', html)

        if not match:
            return None  # 히트맵 데이터 없음

        heatmap_json = json.loads(match.group(1))

        max_score = -1
        peak_time = 0

        # 데이터 구조: [{'heatMarkerRenderer': {'timeRangeStartMillis': 0, 'heatMarkerIntensityScoreNormalized': 0.5}}, ...]
        for item in heatmap_json:
            renderer = item.get('heatMarkerRenderer', {})
            score = renderer.get('heatMarkerIntensityScoreNormalized', 0)
            time_ms = renderer.get('timeRangeStartMillis', 0)

            if score > max_score:
                max_score = score
                peak_time = time_ms / 1000  # 밀리초 -> 초 변환

        return int(peak_time)

    except Exception as e:
        print(f"⚠️ 히트맵 분석 중 오류: {e}")
        return None