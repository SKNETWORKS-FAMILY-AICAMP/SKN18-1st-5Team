# 사용할 데이터 베이스
create database car;
use car;

drop table city_data;

CREATE TABLE gender (
    gender_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    gender_name VARCHAR(10) NOT NULL UNIQUE COMMENT '성별 (예: 남성, 여성)'
);

CREATE TABLE city (
    city_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(50) NOT NULL UNIQUE COMMENT '도시 이름'
);

CREATE TABLE district (
    district_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_name VARCHAR(50) NOT NULL COMMENT '군구 이름',
    UNIQUE (district_name)
);

CREATE TABLE car_type (
    car_type_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    car_type_name VARCHAR(50) NOT NULL UNIQUE COMMENT '차량 종류'
);

CREATE TABLE year (
    year_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    year_value INT NOT NULL UNIQUE COMMENT '연도'
);



CREATE TABLE integrated_statistics (
    stat_id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '통계 ID',
    gender_id INT UNSIGNED DEFAULT NULL COMMENT '성별 ID',
    city_id INT UNSIGNED NULL COMMENT '도시 ID',
    district_id INT UNSIGNED DEFAULT NULL COMMENT '군구 ID',
    car_type_id INT UNSIGNED DEFAULT NULL COMMENT '차량 종류 ID',
    year_id INT UNSIGNED NOT NULL COMMENT '연도 ID',
    count INT NULL COMMENT '등록 대수',
    new_count int unsigned comment '신차 등록 수',
    PRIMARY KEY (stat_id),
    FOREIGN KEY (gender_id) REFERENCES gender(gender_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id),
    FOREIGN KEY (district_id) REFERENCES district(district_id),
    FOREIGN KEY (car_type_id) REFERENCES car_type(car_type_id),
    FOREIGN KEY (year_id) REFERENCES year(year_id)    
);




select *from district;
drop table city_district ;
drop table integrated_statistics;
select *from integrated_statistics ;

# city_data
-- 시 삽입
INSERT IGNORE INTO city (city_name)
SELECT DISTINCT city_data_city FROM city_data;
-- 차량 종류 삽입
INSERT IGNORE INTO car_type (car_type_name)
SELECT DISTINCT city_data_car_type FROM city_data;

-- 연도 삽입
INSERT IGNORE INTO year (year_value)
SELECT DISTINCT city_data_year FROM city_data;

-- 성별
INSERT IGNORE INTO gender (gender_name)
SELECT DISTINCT sex_city_sex FROM sex_city_data;

-- 군구
INSERT IGNORE INTO district (district_name)
SELECT DISTINCT city_district_district
FROM city_district;

-- 시별 data 삽입
desc integrated_statistics;

INSERT INTO integrated_statistics (
	city_id, car_type_id, year_id, count
)
SELECT
    c.city_id,
    ct.car_type_id,
    y.year_id,
    cd.city_data_count
FROM city_data cd
JOIN city c ON cd.city_data_city = c.city_name
JOIN car_type ct ON cd.city_data_car_type = ct.car_type_name
JOIN year y ON cd.city_data_year = y.year_value;

-- 군구 data 삽입
INSERT INTO integrated_statistics (
    gender_id, city_id, district_id, car_type_id, year_id, count
)
SELECT
    NULL AS gender_id,
    c.city_id,
    d.district_id,
    ct.car_type_id,
    y.year_id,
    cd.city_district_count
FROM city_district cd
JOIN city c ON cd.city_district_city = c.city_name
JOIN district d ON cd.city_district_district = d.district_name
JOIN car_type ct ON cd.city_district_car_type = ct.car_type_name
JOIN year y ON cd.city_district_year = y.year_value;

-- gender data 삽입
INSERT INTO integrated_statistics (
    gender_id, city_id, district_id, car_type_id, year_id, count
)
SELECT
    g.gender_id,
    c.city_id,
    NULL AS district_id,
    NULL AS car_type_id,
    y.year_id,
    sc.sex_city_count
FROM sex_city_data sc
JOIN gender g ON sc.sex_city_sex = g.gender_name
JOIN city c ON sc.sex_city_city = c.city_name
JOIN year y ON sc.sex_city_year = y.year_value;

INSERT INTO integrated_statistics (
     year_id, new_count
)
SELECT
  	y.year_id,
  	c.new_count
FROM new_car c
JOIN year y ON c.year = y.year_value;

###############현대 대시보드 테이블####################
-- 현대 판매실적 데이터 테이블 생성
CREATE TABLE hyundai_sale(
	hyundai_sale_ID INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT "현대판매ID",
	year_id INT UNSIGNED NOT NULL COMMENT "연도ID",
	car_name VARCHAR(30) NULL COMMENT "차량이름",
	domestic_count INT NOT NULL COMMENT "해외 판매대수",
	export_count INT NOT NULL COMMENT "국내판매 대수",
	total_count INT NOT NULL COMMENT "총 판매대수",
	PRIMARY KEY (hyundai_sale_ID),
	FOREIGN KEY (year_id) REFERENCES year(year_id)
);

-- 현대 csv와 year id 값 넣기
INSERT INTO hyundai_sale(
    year_id, car_name, domestic_count, export_count, total_count
)
SELECT
    y.year_id,
    hy.car_name,
    hy.Domestic_count,
    hy.Export_count,
    hy.Total_Sales
FROM 현대 hy
JOIN year y ON hy.year = y.year_value;

############FAQ제작#############################

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

-- "현대자동차_카테고리별" 테이블에서 null row 삭제
DELETE
FROM 현대자동차_카테고리별
WHERE 카테고리 IS NULL;

INSERT INTO faq_category (name)
SELECT DISTINCT 카테고리
FROM 현대자동차_카테고리별;


INSERT INTO faq (category_id, question, answer)
SELECT 카테고리, 제목, 내용
FROM 현대자동차_카테고리별;



