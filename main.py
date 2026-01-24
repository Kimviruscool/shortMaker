import sys
import os

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Link.youtube import VideoValidator
from downloads.downloads import VideoDownloader
from login_helper import update_cookies_file
# 🆕 히트맵 분석기 import
from utils.heatmap_helper import get_heatmap_peak


def run_workflow():
    print("=" * 60)
    print("🔥 유튜브 쇼츠 AI: 히트맵 기반 하이라이트 추출기")
    print("=" * 60)

    # 1. 로그인 인증 확인
    cookie_path = "cookies.txt"
    if not os.path.exists(cookie_path):
        print("🚀 최초 1회 로그인을 진행합니다...")
        update_cookies_file(cookie_path)

    validator = VideoValidator()
    downloader = VideoDownloader(output_folder="Shorts_Result")

    while True:
        url = input("\n👉 유튜브 링크 입력 (종료: q): ").strip()
        if url.lower() in ['q', 'exit']: break
        if not url: continue

        # 2. 링크 검증
        check = validator.validate(url)
        if check['status'] != 'PASS':
            print(f"🚫 불가능: {check.get('reason')}")
            continue

        print(f"✅ 검증 통과! ({check['title']})")

        # 3. 🔥 히트맵 분석 시작
        print("🔍 가장 핫한 구간(Heatmap)을 분석 중입니다...")
        peak_time = get_heatmap_peak(check['url'])

        start_time = 0
        duration = 60  # 기본 60초 (쇼츠 길이)

        if peak_time is not None:
            # Case A: 히트맵 데이터 있음
            print(f"🔥 발견! 시청자가 가장 많이 본 구간: {peak_time // 60}분 {peak_time % 60}초")
            print(f"   -> 해당 시점부터 {duration}초간 다운로드합니다.")
            start_time = peak_time
        else:
            # Case B: 히트맵 데이터 없음 (Fallback)
            print("⚠️ 이 영상은 히트맵 데이터가 없습니다 (신규 영상 또는 조회수 부족).")
            print("   [옵션] 1. 직접 시간 입력 (예: 1분 30초 -> 90)")
            print("   [옵션] 2. 그냥 엔터 (인트로 건너뛰고 30초부터 시작)")

            user_input = input("👉 시작 시간(초)을 입력하세요: ").strip()

            if user_input.isdigit():
                start_time = int(user_input)
                print(f"👌 {start_time}초부터 다운로드합니다.")
            else:
                start_time = 30  # 기본값: 30초부터 시작
                print("👌 기본 설정: 30초부터 60초간 다운로드합니다.")

        # 4. 구간 다운로드 실행
        success = downloader.process(check['url'], start_time=start_time, duration=duration)

        if success:
            print(f"\n✨ 하이라이트 추출 완료! (용량 절약 성공)")
        else:
            print("\n💥 실패! 쿠키 만료 여부를 확인하세요.")


if __name__ == "__main__":
    run_workflow()