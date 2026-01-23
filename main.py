# main.py
from Link.youtube import VideoValidator
from downloads.downloads import VideoDownloader


def run_workflow():
    # 1. 모듈 초기화 (도구 준비)
    validator = VideoValidator()
    downloader = VideoDownloader(output_folder="Shorts_Data")

    print("=" * 50)
    print("🎬 유튜브 쇼츠 자동화 워크플로우 v1.0")
    print("=" * 50)

    while True:
        # [Step 0] 링크 입력
        url = input("\n👉 유튜브 링크 입력 (종료: q): ").strip()
        if url.lower() in ['q', 'exit']:
            print("👋 프로그램을 종료합니다.")
            break
        if not url: continue

        # [Step 1] 유효성 검사 (Validator)
        check_result = validator.validate(url)

        if check_result['status'] == 'PASS':
            print(f"✅ 검증 통과! ({check_result['title']})")
            print(f"   - 자막 지원 여부: {'⭕' if check_result['has_kor_sub'] else '❌'}")

            # [Step 2] 다운로드 및 추출 (Downloader)
            # 검증된 링크를 그대로 넘겨줍니다.
            success = downloader.process(check_result['url'])

            if success:
                print("\n✨ 모든 작업이 성공적으로 완료되었습니다!")
                print("   (Shorts_Data 폴더를 확인하세요)")
            else:
                print("\n💥 작업 실패: 다운로드 중 문제가 발생했습니다.")

        else:
            print(f"🚫 작업 불가: {check_result.get('reason')}")


if __name__ == "__main__":
    run_workflow()