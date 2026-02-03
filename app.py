from flask import Flask, render_template, request, jsonify
from models import db, VideoTask
from Download.Link import LinkManager
from Download.Heatmap import HeatmapManager
from Download.VandT import Downloader
from AI.Connect import AIConnector
import os

app = Flask(__name__)

# MySQL 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/short?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 매니저 초기화
link_processor = LinkManager()
heatmap_processor = HeatmapManager()
downloader = Downloader()
ai_connector = AIConnector()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create-shorts', methods=['POST'])
def create_shorts():
    url = request.form.get('url')

    # 1단계: 링크 검증
    video_data = link_processor.process_url(url)
    if video_data['status'] == 'FAIL':
        return jsonify({"error": video_data['reason']})

    # 2단계: 히트맵 분석 (피크 타임 찾기)
    start_time = heatmap_processor.get_peak_time(url) or 0

    # 3단계: 다운로드 및 자막 추출
    txt_path = downloader.process(url, start_time)

    if txt_path:
        # 4단계: AI 분석 실행
        ai_success = ai_connector.process(txt_path)

        if not ai_success:
            return jsonify({"error": "AI 분석 중 오류가 발생했습니다."})

        # 분석된 파일(_AI.txt) 읽기 및 내용 파싱
        ai_txt_path = txt_path.replace(".txt", "_AI.txt")
        subtitles = ""
        narration = ""

        try:
            with open(ai_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # AI 출력 형식에 맞춰 내용 분리
                if "###SUBTITLES###" in content and "###NARRATION###" in content:
                    parts = content.split("###NARRATION###")
                    subtitles = parts[0].replace("###SUBTITLES###", "").strip()
                    narration = parts[1].strip()
                else:
                    subtitles = content  # 형식이 다를 경우 전체 저장
        except Exception as e:
            print(f"파일 읽기 오류: {e}")

        # 5단계: DB 저장
        new_task = VideoTask(
            video_url=url,
            video_id=video_data.get('id'),
            title=video_data['title'],
            start_time=start_time,
            ai_subtitles=subtitles,
            ai_narration=narration,
            status='completed'
        )
        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "message": "쇼츠 제작 및 DB 저장 완료!",
            "title": video_data['title'],
            "start_time": start_time
        })

    return jsonify({"error": "다운로드 단계에서 실패했습니다."})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)