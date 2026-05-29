from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import date

from database import Base

# ──────────────────────────────────────────────
# 등급 정의 (GRADE_CONFIG)
# ──────────────────────────────────────────────
GRADE_CONFIG = {
    "브론즈": {"max_loans": 1, "max_extend_days": 3,  "label": "브론즈"},
    "실버":   {"max_loans": 2, "max_extend_days": 7,  "label": "실버"},
    "골드":   {"max_loans": 3, "max_extend_days": 14, "label": "골드"},
}
GRADES = list(GRADE_CONFIG.keys())  # ["브론즈", "실버", "골드"]

# ──────────────────────────────────────────────
# SQLAlchemy 모델
# ──────────────────────────────────────────────

class DBBook(Base):
    """책 테이블 — 재고(total_stock) 기반 관리"""
    __tablename__ = "books"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String, nullable=False)
    author       = Column(String, nullable=False)
    publisher    = Column(String)
    isbn         = Column(String, unique=True)
    total_stock  = Column(Integer, default=1)   # 총 재고 수량
    # is_available은 계산 프로퍼티로 대체 (available_stock > 0)

    loans = relationship("DBLoan", back_populates="book")

    @property
    def loaned_count(self):
        """현재 대출 중인 수량"""
        return sum(1 for l in self.loans if l.return_date is None)

    @property
    def available_stock(self):
        """대출 가능한 재고"""
        return self.total_stock - self.loaned_count

    @property
    def is_available(self):
        return self.available_stock > 0


class DBMember(Base):
    """회원 테이블 — 등급(grade) 추가"""
    __tablename__ = "members"

    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    grade = Column(String, default="브론즈")   # 브론즈 / 실버 / 골드

    loans = relationship("DBLoan", back_populates="member")

    @property
    def active_loan_count(self):
        return sum(1 for l in self.loans if l.return_date is None)

    @property
    def max_loans(self):
        return GRADE_CONFIG.get(self.grade, GRADE_CONFIG["브론즈"])["max_loans"]

    @property
    def max_extend_days(self):
        return GRADE_CONFIG.get(self.grade, GRADE_CONFIG["브론즈"])["max_extend_days"]


class DBLoan(Base):
    """대출 테이블 — 연장 횟수 추가"""
    __tablename__ = "loans"

    id           = Column(Integer, primary_key=True, index=True)
    book_id      = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id    = Column(Integer, ForeignKey("members.id"), nullable=False)
    loan_date    = Column(Date, nullable=False)
    due_date     = Column(Date, nullable=False)
    return_date  = Column(Date, nullable=True)
    extend_count = Column(Integer, default=0)   # 연장 횟수

    book   = relationship("DBBook",   back_populates="loans")
    member = relationship("DBMember", back_populates="loans")


# ──────────────────────────────────────────────
# Pydantic 스키마
# ──────────────────────────────────────────────

# ── Book ──
class BookCreate(BaseModel):
    title:       str
    author:      str
    publisher:   Optional[str] = None
    isbn:        Optional[str] = None
    total_stock: int = 1

class BookUpdate(BaseModel):
    title:       Optional[str] = None
    author:      Optional[str] = None
    publisher:   Optional[str] = None
    isbn:        Optional[str] = None
    total_stock: Optional[int] = None

class BookResponse(BaseModel):
    id:              int
    title:           str
    author:          str
    publisher:       Optional[str]
    isbn:            Optional[str]
    total_stock:     int
    available_stock: int
    is_available:    bool

    class Config:
        from_attributes = True

# ── Member ──
class MemberCreate(BaseModel):
    name:  str
    email: str
    phone: Optional[str] = None
    grade: str = "브론즈"

class MemberUpdate(BaseModel):
    name:  Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    grade: Optional[str] = None

class MemberResponse(BaseModel):
    id:               int
    name:             str
    email:            str
    phone:            Optional[str]
    grade:            str
    max_loans:        int
    max_extend_days:  int
    active_loan_count: int

    class Config:
        from_attributes = True

# ── Loan ──
class LoanCreate(BaseModel):
    book_id:   int
    member_id: int
    loan_date: date
    due_date:  date

class LoanReturn(BaseModel):
    return_date: date

class LoanExtend(BaseModel):
    extend_days: int  # 연장할 일수

class LoanResponse(BaseModel):
    id:           int
    book_id:      int
    member_id:    int
    loan_date:    date
    due_date:     date
    return_date:  Optional[date]
    extend_count: int
    book:         BookResponse
    member:       MemberResponse

    class Config:
        from_attributes = True