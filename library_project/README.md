---
title: 도서관 관리 시스템
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📚 도서관 관리 시스템 (Library Management System)

FastAPI와 SQLAlchemy를 활용한 MVC 패턴 기반 도서관 관리 웹 애플리케이션입니다.

## 과제 개요

본 프로젝트는 **FastAPI MVC 설계 가이드** 수업 실습 과제로, 도서관을 배경으로 FastAPI와 SQLAlchemy의 작동 원리를 학습하기 위해 제작되었습니다.

각 파일이 도서관을 짓고 운영하는 역할 분담을 하듯, MVC 패턴에 따라 책임을 분리하여 구현하였습니다.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | FastAPI, SQLAlchemy (ORM), Pydantic |
| Database | SQLite |
| Frontend | Vanilla JS, Chart.js |
| 배포 | Hugging Face Spaces (Docker) |

---

## 프로젝트 구조

```
my_library_project/
├── database.py       # DB 엔진, 세션, Base 클래스 (인프라 레이어)
├── models.py         # SQLAlchemy 모델 + Pydantic 스키마 (모델 레이어)
├── crud.py           # CRUD 비즈니스 로직 (뷰 레이어)
├── main.py           # FastAPI 앱 + API 엔드포인트 (컨트롤러 레이어)
├── seed.py           # Faker 기반 샘플 데이터 생성
├── static/
│   └── index.html    # 프론트엔드 대시보드 UI
├── Dockerfile        # Hugging Face Spaces 배포용
└── requirements.txt
```

---

## MVC 구조 설명

### database.py — 도서관 설계도 (인프라)
데이터베이스와의 물리적 연결을 담당합니다.
- `engine` : DB와의 연결 통로 (도서관 건물)
- `SessionLocal` : 요청마다 독립적인 세션 생성 (입장권 발급기)
- `Base` : 모든 모델의 기반 클래스 (책장 템플릿)
- `get_db()` : 의존성 주입용 세션 제공 함수

### models.py — 데이터 구조 정의 (모델)
데이터의 형태를 정의합니다.
- **SQLAlchemy 모델** : DB 테이블과 매핑되는 클래스 (`DBBook`, `DBMember`, `DBLoan`)
- **Pydantic 스키마** : 입력 검증 및 응답 직렬화 (`BookCreate`, `MemberResponse` 등)

### crud.py — 비즈니스 로직 (사서)
순수한 데이터 처리 로직만 담당합니다.
- 도서 / 회원 / 대출의 Create, Read, Update, Delete
- 등급별 대출 한도 검증
- 재고 기반 대출 가능 여부 확인
- 대출 연장 로직 (누적 연장일 제한)

### main.py — API 엔드포인트 (안내 데스크)
클라이언트와의 소통 창구입니다.
- FastAPI 앱 초기화 및 라우터 설정
- `Depends(get_db)`를 통한 의존성 주입
- `@app.on_event("startup")`으로 테이블 자동 생성

---

## 데이터베이스 테이블

### books (도서)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본키 |
| title | String | 제목 |
| author | String | 저자 |
| publisher | String | 출판사 |
| isbn | String | ISBN (고유값) |
| total_stock | Integer | 총 재고 수량 |

### members (회원)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본키 |
| name | String | 이름 |
| email | String | 이메일 (고유값) |
| phone | String | 전화번호 |
| grade | String | 등급 (브론즈/실버/골드) |

### loans (대출)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본키 |
| book_id | Integer | 도서 외래키 |
| member_id | Integer | 회원 외래키 |
| loan_date | Date | 대출일 |
| due_date | Date | 반납 예정일 |
| return_date | Date | 실제 반납일 (NULL = 미반납) |
| extend_count | Integer | 누적 연장일수 |

---

## 회원 등급 시스템

| 등급 | 최대 대출 권수 | 최대 연장일 |
|------|-------------|-----------|
| 브론즈 | 1권 | 3일 |
| 실버 | 2권 | 7일 |
| 골드 | 3권 | 14일 |

---

## API 엔드포인트

### Books
| Method | URL | 설명 |
|--------|-----|------|
| POST | `/books/` | 도서 등록 |
| GET | `/books/` | 전체 도서 조회 |
| GET | `/books/{id}` | 단건 조회 |
| PUT | `/books/{id}` | 도서 수정 |
| DELETE | `/books/{id}` | 도서 삭제 |

### Members
| Method | URL | 설명 |
|--------|-----|------|
| POST | `/members/` | 회원 등록 |
| GET | `/members/` | 전체 회원 조회 |
| GET | `/members/{id}` | 단건 조회 |
| PUT | `/members/{id}` | 회원 수정 |
| DELETE | `/members/{id}` | 회원 삭제 |

### Loans
| Method | URL | 설명 |
|--------|-----|------|
| POST | `/loans/` | 대출 처리 |
| GET | `/loans/` | 전체 대출 조회 |
| GET | `/loans/active` | 대출 중 목록 |
| GET | `/loans/overdue` | 연체 목록 |
| PATCH | `/loans/{id}/return` | 반납 처리 |
| PATCH | `/loans/{id}/extend` | 대출 연장 |

---

## 요청 처리 흐름

```
클라이언트 (Web Browser)
    │  POST /loans/ {"book_id": 1, "member_id": 2}
    ▼
main.py (컨트롤러)
    │  Pydantic LoanCreate 스키마로 데이터 검증
    │  Depends(get_db)로 DB 세션 주입
    ▼
crud.py (비즈니스 로직)
    │  회원 등급 대출 한도 확인
    │  도서 재고 확인
    │  DBLoan 객체 생성 → db.add() → db.commit()
    ▼
database.py (세션)
    │  SessionLocal → yield db → finally db.close()
    ▼
library.db (SQLite)
    │  데이터 영구 저장
    ▼
JSON Response (LoanResponse 스키마로 직렬화)
```

---

## 주요 기능

### 관리자 모드
- 대시보드 — 통계 카드, 도넛 차트, 많이 빌린 책 TOP 5, 최근 대출 현황
- 도서 관리 — 등록/수정/삭제, 제목·저자·출판사·대출가능여부 필터, 재고 수량 관리
- 회원 관리 — 등록/수정/삭제, 등급 관리, 현재 대출 현황 표시
- 대출 관리 — 대출 등록, 반납 처리, 대출 연장, 상태 필터
- 연체 현황 — 연체 목록 및 연체 일수 표시

### 대출자 모드
- 도서 검색 — 키워드/출판사/대출가능여부 필터, 재고 현황 표시
- 대출 신청 — 등급별 한도 초과 시 버튼 자동 비활성화
- 내 대출 현황 — 대출 중인 책 목록, 연장 신청, 반납 신청

---

## 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 샘플 데이터 생성
python seed.py

# 4. 서버 실행
uvicorn main:app --reload
```

- 대시보드: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

---

## 배포

- Hugging Face Spaces (Docker)
- https://sentier2006-library-project.hf.space
