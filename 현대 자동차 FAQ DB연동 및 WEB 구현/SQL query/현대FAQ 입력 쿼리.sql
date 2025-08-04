-- "현대자동차_카테고리별" 테이블에서 null row 삭제
DELETE
FROM 현대자동차_카테고리별
WHERE 카테고리 IS NULL;
-- 확인
SELECT *
FROM 현대자동차_카테고리별;

-- 테이블 faq_category
-- category 항목 확인 및 테이블 "faq_category"
SELECT DISTINCT 카테고리
FROM 현대자동차_카테고리별;

INSERT INTO faq_category (name)
SELECT DISTINCT 카테고리
FROM 현대자동차_카테고리별;

-- 테이블 faq
-- 필요한 행 조회 및 삽입
SELECT 카테고리, 제목, 내용
FROM 현대자동차_카테고리별;

INSERT INTO faq (category_id, question, answer)
SELECT 카테고리, 제목, 내용
FROM 현대자동차_카테고리별;