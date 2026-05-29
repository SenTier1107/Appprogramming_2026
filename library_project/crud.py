from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from models import (
    DBBook, DBMember, DBLoan,
    BookCreate, BookUpdate,
    MemberCreate, MemberUpdate,
    LoanCreate, LoanReturn, LoanExtend,
    GRADE_CONFIG,
)


# ──────────────────────────────────────────────
# Book CRUD
# ──────────────────────────────────────────────

def create_book(db: Session, book: BookCreate) -> DBBook:
    db_book = DBBook(
        title=book.title, author=book.author,
        publisher=book.publisher, isbn=book.isbn,
        total_stock=book.total_stock,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_books(db: Session, skip: int = 0, limit: int = 200) -> List[DBBook]:
    return db.query(DBBook).offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int) -> Optional[DBBook]:
    return db.query(DBBook).filter(DBBook.id == book_id).first()


def update_book(db: Session, book_id: int, book_data: BookUpdate) -> Optional[DBBook]:
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    for field, value in book_data.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int) -> bool:
    db_book = get_book(db, book_id)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True


# ──────────────────────────────────────────────
# Member CRUD
# ──────────────────────────────────────────────

def create_member(db: Session, member: MemberCreate) -> DBMember:
    db_member = DBMember(
        name=member.name, email=member.email,
        phone=member.phone, grade=member.grade,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def get_members(db: Session, skip: int = 0, limit: int = 200) -> List[DBMember]:
    return db.query(DBMember).offset(skip).limit(limit).all()


def get_member(db: Session, member_id: int) -> Optional[DBMember]:
    return db.query(DBMember).filter(DBMember.id == member_id).first()


def update_member(db: Session, member_id: int, member_data: MemberUpdate) -> Optional[DBMember]:
    db_member = get_member(db, member_id)
    if not db_member:
        return None
    for field, value in member_data.model_dump(exclude_unset=True).items():
        setattr(db_member, field, value)
    db.commit()
    db.refresh(db_member)
    return db_member


def delete_member(db: Session, member_id: int) -> bool:
    db_member = get_member(db, member_id)
    if not db_member:
        return False
    db.delete(db_member)
    db.commit()
    return True


# ──────────────────────────────────────────────
# Loan CRUD
# ──────────────────────────────────────────────

def create_loan(db: Session, loan: LoanCreate):
    """
    대출 처리
    - 재고 기반: available_stock > 0 이어야 대출 가능
    - 등급 기반: 현재 대출 중인 수 < max_loans 이어야 함
    반환값: (DBLoan, None) 성공 / (None, 에러메시지) 실패
    """
    db_book = get_book(db, loan.book_id)
    if not db_book:
        return None, "책을 찾을 수 없습니다."
    if db_book.available_stock <= 0:
        return None, f"모든 재고({db_book.total_stock}권)가 대출 중입니다."

    db_member = get_member(db, loan.member_id)
    if not db_member:
        return None, "회원을 찾을 수 없습니다."

    active = db_member.active_loan_count
    if active >= db_member.max_loans:
        return None, (
            f"{db_member.grade} 등급은 최대 {db_member.max_loans}권까지 대출 가능합니다. "
            f"현재 {active}권 대출 중입니다."
        )

    db_loan = DBLoan(
        book_id=loan.book_id, member_id=loan.member_id,
        loan_date=loan.loan_date, due_date=loan.due_date,
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan, None


def get_loans(db: Session, skip: int = 0, limit: int = 300) -> List[DBLoan]:
    return db.query(DBLoan).offset(skip).limit(limit).all()


def get_loan(db: Session, loan_id: int) -> Optional[DBLoan]:
    return db.query(DBLoan).filter(DBLoan.id == loan_id).first()


def return_loan(db: Session, loan_id: int, return_data: LoanReturn):
    db_loan = get_loan(db, loan_id)
    if not db_loan or db_loan.return_date is not None:
        return None, "대출 기록이 없거나 이미 반납된 항목입니다."
    db_loan.return_date = return_data.return_date
    db.commit()
    db.refresh(db_loan)
    return db_loan, None


def extend_loan(db: Session, loan_id: int, extend_data: LoanExtend):
    """
    대출 연장
    - 이미 반납된 경우 불가
    - 등급별 max_extend_days 초과 불가 (누적 연장일 기준)
    """
    db_loan = get_loan(db, loan_id)
    if not db_loan:
        return None, "대출 기록을 찾을 수 없습니다."
    if db_loan.return_date is not None:
        return None, "이미 반납된 대출입니다."

    max_days = db_loan.member.max_extend_days
    # 지금까지 연장한 총 일수 = extend_count 를 날짜로 저장하지 않고
    # due_date - 원래 due_date 차이로 계산 (extend_count * 평균 대신 직접 누적)
    # 여기서는 extend_count 를 "누적 연장일수"로 사용
    already = db_loan.extend_count
    if already + extend_data.extend_days > max_days:
        remaining = max_days - already
        return None, (
            f"{db_loan.member.grade} 등급은 최대 {max_days}일 연장 가능합니다. "
            f"잔여 연장 가능일: {remaining}일"
        )

    db_loan.due_date = db_loan.due_date + timedelta(days=extend_data.extend_days)
    db_loan.extend_count += extend_data.extend_days
    db.commit()
    db.refresh(db_loan)
    return db_loan, None


def get_active_loans(db: Session) -> List[DBLoan]:
    return db.query(DBLoan).filter(DBLoan.return_date == None).all()


def get_overdue_loans(db: Session, today: date = None) -> List[DBLoan]:
    if today is None:
        today = date.today()
    return (
        db.query(DBLoan)
        .filter(DBLoan.return_date == None, DBLoan.due_date < today)
        .all()
    )