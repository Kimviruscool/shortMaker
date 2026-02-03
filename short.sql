CREATE DATABASE IF NOT EXISTS short;
USE short;

-- 쇼츠 제작 작업 정보를 저장하는 테이블
CREATE TABLE IF NOT EXISTS video_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '고유 번호',
    video_url VARCHAR(500) NOT NULL COMMENT '원본 유튜브 링크',
    video_id VARCHAR(50) COMMENT '유튜브 영상 ID',
    title VARCHAR(255) COMMENT '영상 제목',
    start_time INT DEFAULT 0 COMMENT '추출 시작 시점(초)',
    duration INT DEFAULT 60 COMMENT '추출 길이(초)',
    
    -- AI 생성 콘텐츠
    ai_subtitles TEXT COMMENT 'AI가 다듬은 자막 내용',
    ai_narration TEXT COMMENT 'AI가 생성한 나레이션 대본',
    
    -- 상태 및 시간 관리
    status VARCHAR(20) DEFAULT 'pending' COMMENT '상태: pending, processing, completed, failed',
    error_message TEXT COMMENT '실패 시 에러 내용',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성 일시',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 일시'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;