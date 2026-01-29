import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Download.Link import LinkManager
    from Download.Heatmap import HeatmapManager
    from Download.VandT import Downloader
    # 1. AI Connector 추가!
    from AI.Connect import AIConnector
except ImportError as e:
    print(f"❌ 설정 오류: {e}")
    sys.exit(1)


def run():
    print("=" * 60)
    print("🎬 ShortMaker v1.4 (AI Powered)")  # 버전 업!
    print("=" * 60)

    # 매니저들 초기화
    link_processor = LinkManager()
    heatmap_processor = HeatmapManager()
    downloader = Downloader()
    ai_connector = AIConnector()  # 2. AI 매니저 초기화

    while True:
        # ... (링크 입력 및 검증 부분 동일) ...
        # ... (히트맵 분석 부분 동일) ...

        # ---------------------------------------------------------
        # [Step 3] 다운로드 (Video & Text)
        # ---------------------------------------------------------
        print(f"\n💾 [3단계] 다운로드 및 저장 시작 (시작: {start_time}초)")

        # 3. process가 이제 성공 시 '파일 경로'를 반환합니다.
        generated_txt_path = downloader.process(
            url=video_data['url'],
            start_time=start_time,
            duration=duration
        )

        if generated_txt_path:
            print("\n✨ 다운로드 완료! 이어서 AI 분석을 시작합니다.")

            # ---------------------------------------------------------
            # [Step 4] AI 연결 및 콘텐츠 생성
            # ---------------------------------------------------------
            print(f"\n🧠 [4단계] AI 콘텐츠 생성 (자막 다듬기 + 나레이션)")

            # 4. 다운로드된 텍스트 경로를 AI에게 전달
            ai_success = ai_connector.process(generated_txt_path)

            if ai_success:
                print("\n🎉 모든 작업이 성공적으로 끝났습니다! 'Shorts_Result' 폴더를 확인하세요.")
            else:
                print("\n⚠️ 다운로드는 성공했으나, AI 분석 중 문제가 발생했습니다.")

        else:
            print("\n💥 다운로드 단계에서 실패하여 AI 분석을 진행할 수 없습니다.")


if __name__ == "__main__":
    run()