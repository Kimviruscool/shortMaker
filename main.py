import sys
import os

# -----------------------------------------------------------
# 1. 환경 설정 및 모듈 경로 잡기
# -----------------------------------------------------------
# 현재 파일(main.py)이 있는 위치를 기준으로 경로를 설정합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 폴더 구조에 맞춘 모듈 임포트
# (대소문자 정확히 매칭: Link, downloads, utils)
try:
    from Link.youtube import VideoValidator  # Link 폴더
    from downloads.downloads import VideoDownloader  # downloads 폴더
    from utils.heatmap_helper import get_heatmap_peak  # utils 폴더
    from login_helper import update_cookies_file  # 같은 폴더
except ImportError as e:
    print(f"❌ 모듈 임포트 오류: {e}")
    print("   폴더 구조가 정확한지(Link, downloads, utils) 확인해주세요.")
    sys.exit(1)


def run_workflow():
    print("=" * 60)
    print("🔥 유튜브 쇼츠 AI: 히트맵 기반 하이라이트 추출기 v3.0")
    print("=" * 60)

    # -----------------------------------------------------------
    # [Step 1] 로그인 인증 파일(cookies.txt) 체크
    # -----------------------------------------------------------
    cookie_path = os.path.join(current_dir, "cookies.txt")

    if not os.path.exists(cookie_path):
        print("\n⚠️  로그인 정보(cookies.txt)가 없습니다.")
        print("🚀  최초 1회 로그인을 위해 브라우저를 실행합니다...")

        try:
            update_cookies_file(cookie_path)  # 셀레니움 실행
            print("\n✅  인증 완료! 쿠키 파일이 생성되었습니다.")
        except Exception as e:
            print(f"\n❌ 로그인 도구 실행 실패: {e}")
            return
    else:
        print(f"\n✅  로그인 정보 확인됨 ({cookie_path})")

    # -----------------------------------------------------------
    # [Step 2] 도구 초기화 (Validator & Downloader)
    # -----------------------------------------------------------
    validator = VideoValidator()
    # 다운로더 인스턴스 생성 (FFmpeg 자동 감지 로직 포함됨)
    downloader = VideoDownloader(output_folder="Shorts_Result")

    # -----------------------------------------------------------
    # [Step 3] 메인 루프 (무한 반복)
    # -----------------------------------------------------------
    while True:
        url = input("\n👉 유튜브 링크 입력 (종료: q): ").strip()

        # 종료 조건
        if url.lower() in ['q', 'exit', 'quit']:
            print("👋 프로그램을 종료합니다.")
            break

        if not url: continue

        # 1. 링크 유효성 검사
        check = validator.validate(url)
        if check['status'] != 'PASS':
            print(f"🚫 작업 불가: {check.get('reason')}")
            continue

        print(f"✅ 검증 통과! ({check['title']})")

        # 2. 히트맵 분석 (가장 많이 본 구간 찾기)
        print("🔍 가장 핫한 구간(Heatmap)을 분석 중입니다...")
        peak_time = get_heatmap_peak(check['url'])

        start_time = 0
        duration = 60  # 기본 쇼츠 길이 (60초)

        if peak_time is not None:
            # Case A: 히트맵 데이터가 있는 경우
            print(f"🔥 발견! 시청자가 가장 많이 본 구간: {peak_time // 60}분 {peak_time % 60}초")
            print(f"   -> 해당 시점부터 {duration}초간 다운로드합니다.")
            start_time = peak_time
        else:
            # Case B: 히트맵 데이터가 없는 경우 (수동 입력)
            print("⚠️ 이 영상은 히트맵 데이터가 없습니다 (신규 영상 또는 조회수 부족).")
            print("   [옵션] 1. 숫자 입력 (예: 90 -> 1분 30초부터 시작)")
            print("   [옵션] 2. 그냥 엔터 (기본값: 인트로 건너뛰고 30초부터 시작)")

            user_input = input("👉 시작 시간(초)을 입력하세요: ").strip()

            if user_input.isdigit():
                start_time = int(user_input)
                print(f"👌 {start_time}초부터 다운로드합니다.")
            else:
                start_time = 30
                print("👌 기본 설정: 30초부터 60초간 다운로드합니다.")

        # 3. 다운로드 및 변환 실행
        # (downloads.py에서 mp4 변환 및 잘라내기를 수행함)
        success = downloader.process(check['url'], start_time=start_time, duration=duration)

        if success:
            print(f"\n✨ 작업 완료! 'Shorts_Result' 폴더를 확인하세요.")
        else:
            print("\n💥 작업 실패! 위 에러 메시지를 확인하세요.")


if __name__ == "__main__":
    run_workflow()