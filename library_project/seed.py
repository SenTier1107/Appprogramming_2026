"""seed.py — 등급/재고 반영 더미 데이터 생성"""
from faker import Faker
from datetime import date, timedelta
import random

from database import Base, engine, get_db
from models import BookCreate, MemberCreate, LoanCreate, LoanReturn, GRADES
import crud

fake = Faker("ko_KR")

BOOK_TITLES = [
    "파이썬 완벽 가이드","파이썬 코딩의 기술","전문가를 위한 파이썬",
    "자바 ORM 표준 JPA 프로그래밍","이펙티브 자바","모던 자바 인 액션",
    "러스트 프로그래밍","고언어로 만드는 클라우드 네이티브",
    "타입스크립트 프로그래밍","자바스크립트 완벽 가이드",
    "FastAPI 실전 입문","Django 마스터 클래스",
    "Node.js 교과서","리액트를 다루는 기술",
    "Vue.js 프로젝트 투입 일주일 전","Next.js로 배우는 리액트",
    "REST API 디자인 패턴","GraphQL 실전 가이드",
    "데이터베이스 설계의 정석","SQL 레벨업",
    "PostgreSQL 완벽 가이드","MongoDB 인 액션",
    "Redis 실전 활용","Real MySQL 8.0",
    "클린 코드","클린 아키텍처",
    "리팩터링 2판","객체지향의 사실과 오해",
    "도메인 주도 설계","마이크로서비스 패턴",
    "소프트웨어 아키텍처 101","함수형 프로그래밍",
    "혼자 공부하는 머신러닝","딥러닝 첫걸음",
    "핸즈온 머신러닝","파이토치로 시작하는 딥러닝",
    "강화학습 입문","자연어 처리 쿡북",
    "데이터 과학을 위한 통계","컴퓨터 비전과 딥러닝",
    "알고리즘 문제 풀이 전략","알고리즘 도감",
    "코딩 인터뷰 완전 분석","운영체제 아주 쉬운 세 가지 이야기",
    "컴퓨터 네트워크 하향식 접근","리눅스 명령어 사전",
    "도커 & 쿠버네티스","쿠버네티스 완벽 가이드",
    "사이트 신뢰성 엔지니어링","데브옵스 핸드북",
    "프로그래머의 뇌","더 나은 프로그래머 되는 법",
    "개발자 원칙","소프트 스킬","해커와 화가","실용주의 프로그래머",
    "테스트 주도 개발","단위 테스트의 기술",
    "데이터 파이프라인 핵심 가이드","아파치 카프카",
    "스파크 완벽 가이드","데이터 중심 애플리케이션 설계",
]
PUBLISHERS = ["한빛미디어","인사이트","O'Reilly Korea","길벗","위키북스","제이펍","에이콘출판","프리렉"]


def seed(num_books=60, num_members=30, num_loans=100):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("테이블 초기화 완료\n")

    db = next(get_db())

    # ── 책 등록 (재고 1~3권 랜덤) ──
    books = []
    titles = random.sample(BOOK_TITLES, min(num_books, len(BOOK_TITLES)))
    for title in titles:
        stock = random.choices([1, 2, 3], weights=[50, 30, 20])[0]
        book = crud.create_book(db, BookCreate(
            title=title, author=fake.name(),
            publisher=random.choice(PUBLISHERS),
            isbn=fake.isbn13(), total_stock=stock,
        ))
        books.append(book)
        print(f"  책: [{book.id:03d}] {book.title} (재고 {stock}권)")

    print(f"\n책 {len(books)}권 등록 완료\n")

    # ── 회원 등록 (등급 랜덤) ──
    members = []
    for _ in range(num_members):
        grade = random.choices(GRADES, weights=[50, 30, 20])[0]
        member = crud.create_member(db, MemberCreate(
            name=fake.name(), email=fake.unique.email(),
            phone=fake.phone_number(), grade=grade,
        ))
        members.append(member)
        print(f"  회원: [{member.id:03d}] {member.name} / {grade}")

    print(f"\n회원 {len(members)}명 등록 완료\n")

    # ── 대출 처리 ──
    loan_count = 0
    for _ in range(num_loans):
        book   = random.choice(books)
        member = random.choice(members)

        # DB에서 최신 상태 반영
        db.expire(book); db.expire(member)
        db.refresh(book); db.refresh(member)

        loan_date = date.today() - timedelta(days=random.randint(1, 60))
        due_date  = loan_date + timedelta(days=14)

        loan, err = crud.create_loan(db, LoanCreate(
            book_id=book.id, member_id=member.id,
            loan_date=loan_date, due_date=due_date,
        ))
        if not loan:
            continue

        if random.random() < 0.65:
            ret = loan_date + timedelta(days=random.randint(1, 20))
            crud.return_loan(db, loan.id, LoanReturn(return_date=ret))
            status = f"반납완료({ret})"
        else:
            status = "대출중"

        print(f"  대출: {book.title[:18]:<18} -> {member.name}({member.grade}) [{status}]")
        loan_count += 1

    print(f"\n대출 {loan_count}건 등록 완료\n")

    active  = crud.get_active_loans(db)
    overdue = crud.get_overdue_loans(db)
    print("=" * 52)
    print(f"  총 책        : {len(books)}권")
    print(f"  총 회원      : {len(members)}명")
    print(f"  총 대출 이력 : {loan_count}건")
    print(f"  현재 대출중  : {len(active)}건")
    print(f"  연체         : {len(overdue)}건")
    print("=" * 52)
    print("\n완료! uvicorn main:app --reload")
    db.close()


if __name__ == "__main__":
    seed()