---
title: Library Management System
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 도서관 관리 시스템

FastAPI + SQLAlchemy MVC 패턴으로 구현한 도서관 관리 시스템입니다.

## 기능

### 관리자 모드
- 대시보드 (통계, 차트)
- 도서 관리 (등록/수정/삭제/검색)
- 회원 관리
- 대출 관리 및 반납 처리
- 연체 현황

### 대출자 모드
- 도서 검색 및 대출 신청
- 내 대출 현황 및 반납 신청

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy, Pydantic, SQLite
- **Frontend**: Vanilla JS, Chart.js
- **Architecture**: MVC Pattern