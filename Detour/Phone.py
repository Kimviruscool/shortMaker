#차단방지용

class PhoneManager:
    def get_client_mode(self, mode="android"):
        """
        요청받은 모드(android 또는 ios)에 맞춰
        유튜브 서버를 속이는(Spoofing) 설정을 반환합니다.
        """
        if mode == "android":
            # 안드로이드 앱으로 위장 (가장 호환성 좋음)
            return {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        elif mode == "ios":
            # 아이폰 앱으로 위장 (안드로이드가 막혔을 때 대안)
            return {
                'youtube': {
                    'player_client': ['ios', 'web']
                }
            }
        else:
            # 기본값
            return {}