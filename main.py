import sys
import os

# 모듈 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 모듈 불러오기
try:
    from Download.Link import LinkManager
    from Download.Heatmap import HeatmapManager  # <-- 새로 추가됨
except ImportError as e:
    print(f"❌ 설정 오류: {e}")
    sys.exit(1)


def run():
    print("=" * 60)
    print("🎬 ShortMaker v1.1 (Heatmap Added)")
    print("=" * 60)

    # 매니저들 초기화
    link_processor = LinkManager()
    heatmap_processor = HeatmapManager()  # <-- 히트맵 매니저 생성

    while True:
        user_input = input("\n👉 유튜브 링크 입력 (종료: q): ").strip()

        if user_input.lower() in ['q', 'quit', 'exit']:
            print("👋 프로그램을 종료합니다.")
            break

        if not user_input: continue

        # ---------------------------------------------------------
        # [Step 1] 링크 분석 (Link.py)
        # ---------------------------------------------------------
        print("🔍 1. 링크 분석 중...")
        video_data = link_processor.process_url(user_input)

        if video_data['status'] == 'FAIL':
            print(f"🚫 [실패] {video_data['reason']}")
            continue

        print(f"✅ [확인] {video_data['title']}")

        # ---------------------------------------------------------
        # [Step 2] 히트맵 분석 (Heatmap.py)
        # ---------------------------------------------------------
        print("🔥 2. 가장 핫한 구간 찾는 중...")
        peak_time = heatmap_processor.get_peak_time(video_data['url'])

        final_start_time = 0  # V&T로 넘겨줄 최종 시간

        if peak_time is not None:
            # Case A: 히트맵 데이터가 있는 경우
            m = int(peak_time // 60)
            s = int(peak_time % 60)
            print(f"   🚀 발견! 시청자가 가장 많이 본 구간: {m}분 {s}초")
            final_start_time = peak_time
        else:
            # Case B: 히트맵 데이터가 없는 경우 (수동 입력)
            print("   ⚠️ 히트맵 데이터가 없습니다 (신규 영상 또는 데이터 부족).")
            print("   👉 직접 시작 시간을 입력해주세요.")

            while True:
                time_input = input("      시작 시간(초) 입력 (예: 90): ").strip()
                if time_input.isdigit():
                    final_start_time = int(time_input)
                    print(f"   👌 {final_start_time}초로 설정되었습니다.")
                    break
                else:
                    print("      ❌ 숫자만 입력해주세요.")

        # ---------------------------------------------------------
        # [Step 3] 다음 단계 준비 (V&T)
        # ---------------------------------------------------------
        print("-" * 40)
        print(f"💾 [저장 예정 정보]")
        print(f"   - 영상 URL: {video_data['url']}")
        print(f"   - 시작 시간: {final_start_time}초")
        print(f"   - 길이: 60초 (기본값)")
        print("   -> 이제 이 정보를 'V&T' 모듈로 넘겨서 다운로드하면 됩니다.")
        print("-" * 40)


if __name__ == "__main__":
    run()