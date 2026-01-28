import sys
import os

# 모듈 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 모듈 불러오기
try:
    from Download.Link import LinkManager
    from Download.Heatmap import HeatmapManager
    from Download.VandT import Downloader  # <--- 1. 여기가 추가되어야 합니다!
except ImportError as e:
    print(f"❌ 설정 오류: {e}")
    sys.exit(1)


def run():
    print("=" * 60)
    print("🎬 ShortMaker v1.2 (Full Workflow)")  # <--- 버전 업!
    print("=" * 60)

    # 1. 매니저들 초기화
    link_processor = LinkManager()
    heatmap_processor = HeatmapManager()
    downloader = Downloader()  # <--- 2. 다운로더 준비!

    while True:
        user_input = input("\n👉 유튜브 링크 입력 (종료: q): ").strip()

        if user_input.lower() in ['q', 'quit', 'exit']:
            print("👋 프로그램을 종료합니다.")
            break

        if not user_input: continue

        # ---------------------------------------------------------
        # [Step 1] 링크 검증
        # ---------------------------------------------------------
        print("\n🔍 [1단계] 링크 분석 중...")
        video_data = link_processor.process_url(user_input)

        if video_data['status'] == 'FAIL':
            print(f"🚫 {video_data['reason']}")
            continue

        print(f"✅ 확인됨: {video_data['title']}")

        # ---------------------------------------------------------
        # [Step 2] 시간 분석 (히트맵 or 수동)
        # ---------------------------------------------------------
        print("\n🔥 [2단계] 하이라이트 구간 분석...")
        peak_time = heatmap_processor.get_peak_time(video_data['url'])

        start_time = 0
        duration = 60  # 기본 60초

        if peak_time is not None:
            m, s = divmod(int(peak_time), 60)
            print(f"   🚀 히트맵 발견! 가장 핫한 구간: {m}분 {s}초")
            start_time = peak_time
        else:
            print("   ⚠️ 히트맵 없음. 시간을 직접 입력해주세요.")
            while True:
                t = input("   👉 시작 시간(초) 입력 (예: 90): ").strip()
                if t.isdigit():
                    start_time = int(t)
                    break
                else:
                    print("   ❌ 숫자만 입력하세요.")

        # ---------------------------------------------------------
        # [Step 3] 다운로드 (Video & Text) - 여기가 핵심!
        # ---------------------------------------------------------
        print(f"\n💾 [3단계] 다운로드 및 저장 시작 (시작: {start_time}초)")

        # 3. 실제로 다운로드를 수행하는 부분
        success = downloader.process(
            url=video_data['url'],
            start_time=start_time,
            duration=duration
        )

        if success:
            print("\n✨ 모든 작업이 완료되었습니다! 'Shorts_Result' 폴더를 확인하세요.")
        else:
            print("\n💥 작업 중 오류가 발생했습니다.")


if __name__ == "__main__":
    run()