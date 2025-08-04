-- 1. 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS hyundai_faq_db
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. 사용할 데이터베이스 선택
USE hyundai_faq_db;

-- 3. 카테고리 테이블
CREATE TABLE faq_category (
  name VARCHAR(100) PRIMARY KEY NOT NULL COMMENT 'FAQ 카테고리 이름'
);

-- 4. FAQ 본문 테이블
CREATE TABLE faq (
  id INT PRIMARY KEY AUTO_INCREMENT,
  category_id VARCHAR(50),
  question TEXT NOT NULL COMMENT '질문 내용',
  answer TEXT NOT NULL COMMENT '답변 내용',
  FOREIGN KEY (category_id) REFERENCES faq_category(name)
    ON DELETE SET NULL ON UPDATE CASCADE
);

-- 5. TOP5 faq
CREATE TABLE Top_5 (
  id INT PRIMARY KEY AUTO_INCREMENT,
  faq_id INT NOT NULL,
  top_order INT,
  FOREIGN KEY (faq_id) REFERENCES faq(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
-- 예시로 데이터를 확인하는 용도
-- SELECT t.rank, f.question, f.answer
-- FROM Top_5 t
-- JOIN faq f ON t.faq_id = f.id
-- ORDER BY t.rank;


-- 예: 자주 묻는 1위 질문은 faq의 3번 질문이다
-- INSERT INTO Top_5 (faq_id, rank) VALUES (3, 1)

show tables;
desc Top_5;