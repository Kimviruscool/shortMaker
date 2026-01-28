import yt_dlp


class HeatmapManager:
    def get_peak_time(self, url):
        """
        영상의 히트맵 데이터를 분석하여 시청자가 가장 많이 본 시점(초)을 반환합니다.
        데이터가 없으면 None을 반환합니다.
        """
        # 히트맵 데이터는 'extract_flat'으로는 안 나오고, 전체 정보를 긁어야 나옵니다.
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # yt-dlp가 제공하는 'heatmap' 필드 확인
                # 구조: [{'start_time': 0.0, 'end_time': 1.0, 'value': 0.5}, ...]
                heatmap_data = info.get('heatmap')

                if not heatmap_data:
                    return None  # 히트맵 없음 (신규 영상 등)

                # 'value'가 가장 높은 항목 찾기 (가장 핫한 구간)
                best_part = max(heatmap_data, key=lambda x: x.get('value', 0))

                # 해당 구간의 시작 시간 반환
                return best_part.get('start_time', 0)

        except Exception as e:
            # 에러 발생 시에도 그냥 수동 입력으로 넘기기 위해 None 반환
            print(f"⚠️ 히트맵 분석 중 오류 발생: {e}")
            return None