# AI , TELEGRAM CONNECT

import os
import openai


class AIConnector:
    def __init__(self):
        # 🚨 중요: 여기에 본인의 OpenAI API 키를 입력하세요! 🚨
        # (실제 배포 시에는 환경변수나 설정 파일을 이용하는 것이 안전합니다.)
        self.api_key = "sk-YOUR_OPENAI_API_KEY_HERE"

        if not self.api_key or self.api_key == "sk-YOUR_OPENAI_API_KEY_HERE":
            print("⚠️ [AI] 경고: API 키가 설정되지 않았습니다. Connect.py 파일을 열어 키를 입력해주세요.")
            self.client = None
        else:
            # 최신 버전(1.x.x) 클라이언트 초기화
            self.client = openai.OpenAI(api_key=self.api_key)
            print("🤖 [AI] 엔진 초기화 완료")

        # 📝 AI에게 지시할 강력한 프롬프트 (수정 가능)
        self.system_prompt = """
당신은 유튜브 쇼츠 전문 콘텐츠 디렉터이자 전문 작가입니다.
제공된 원본 영상의 자막 텍스트를 분석하여, 다음 두 가지 결과물을 작성해주세요.

---
요구사항 1: [다듬어진 자막]
원본의 의미를 완벽하게 유지하되, 오타를 수정하고 문맥을 자연스럽게 다듬어주세요.
쇼츠 특성에 맞게 호흡이 짧고 임팩트 있는 문장으로 구성해주세요.

요구사항 2: [나레이션 대본]
이 영상의 내용을 바탕으로, 시청자의 흥미를 유발할 수 있는 매력적인 나레이션 대본을 새로 작성해주세요.
(예: 초반 후킹 멘트, 감탄사, 질문 던지기, 요약 등 활용)
---

출력 형식은 반드시 아래 구조를 지켜주세요:
###SUBTITLES###
(여기에 다듬어진 자막 내용을 적어주세요)
###NARRATION###
(여기에 나레이션 대본을 적어주세요)
"""

    def process(self, input_txt_path):
        """
        텍스트 파일 경로를 받아 AI 처리 후, 결과 파일을 생성합니다.
        """
        if not self.client:
            print("🚫 [AI] API 키가 없어 작업을 중단합니다.")
            return False

        if not input_txt_path or not os.path.exists(input_txt_path):
            print(f"🚫 [AI] 입력 파일이 없습니다: {input_txt_path}")
            return False

        print(f"🤖 [AI] 텍스트 분석 및 생성 시작... (파일명: {os.path.basename(input_txt_path)})")

        # 1. 원본 텍스트 읽기
        try:
            with open(input_txt_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except Exception as e:
            print(f"❌ [AI] 파일 읽기 실패: {e}")
            return False

        # 2. AI에게 요청 보내기 (GPT-4o-mini 또는 GPT-3.5-turbo 사용 권장)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 가성비 좋은 최신 모델 (변경 가능)
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"원본 텍스트:\n{raw_text}"}
                ],
                temperature=0.7  # 창의성 조절 (0.0 ~ 1.0)
            )
            ai_result_text = response.choices[0].message.content

        except Exception as e:
            print(f"💥 [AI] API 호출 중 오류 발생: {e}")
            return False

        # 3. 결과 파일 저장 (원본이름_AI.txt)
        base, ext = os.path.splitext(input_txt_path)
        output_txt_path = f"{base}_AI{ext}"

        try:
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(ai_result_text)
            print(f"✨ [AI] 결과 생성 완료! 저장 위치: {os.path.basename(output_txt_path)}")
            return True
        except Exception as e:
            print(f"❌ [AI] 결과 파일 저장 실패: {e}")
            return False