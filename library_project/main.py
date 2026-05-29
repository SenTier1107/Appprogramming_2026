from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import Base, engine, get_db
import crud
from models import (
    BookCreate, BookUpdate, BookResponse,
    MemberCreate, MemberUpdate, MemberResponse,
    LoanCreate, LoanReturn, LoanExtend, LoanResponse,
)

app = FastAPI(
    title="도서관 관리 시스템",
    description="FastAPI MVC 패턴 — 등급별 대출 제한 / 연장 / 재고 관리",
    version="2.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("static/index.html")

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("테이블 생성 완료")


# ── Books ──────────────────────────────────────
@app.post("/books/", response_model=BookResponse, tags=["Books"])
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, book)

@app.get("/books/", response_model=List[BookResponse], tags=["Books"])
def get_books(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_books(db, skip=skip, limit=limit)

@app.get("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")
    return book

@app.put("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db)):
    book = crud.update_book(db, book_id, book_data)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")
    return book

@app.delete("/books/{book_id}", tags=["Books"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    if not crud.delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")
    return {"message": f"book_id={book_id} 삭제 완료"}


# ── Members ────────────────────────────────────
@app.post("/members/", response_model=MemberResponse, tags=["Members"])
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    return crud.create_member(db, member)

@app.get("/members/", response_model=List[MemberResponse], tags=["Members"])
def get_members(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_members(db, skip=skip, limit=limit)

@app.get("/members/{member_id}", response_model=MemberResponse, tags=["Members"])
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = crud.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return member

@app.put("/members/{member_id}", response_model=MemberResponse, tags=["Members"])
def update_member(member_id: int, member_data: MemberUpdate, db: Session = Depends(get_db)):
    member = crud.update_member(db, member_id, member_data)
    if not member:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return member

@app.delete("/members/{member_id}", tags=["Members"])
def delete_member(member_id: int, db: Session = Depends(get_db)):
    if not crud.delete_member(db, member_id):
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return {"message": f"member_id={member_id} 삭제 완료"}


# ── Loans ──────────────────────────────────────
@app.post("/loans/", response_model=LoanResponse, tags=["Loans"])
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    result, err = crud.create_loan(db, loan)
    if not result:
        raise HTTPException(status_code=400, detail=err)
    return result

@app.get("/loans/", response_model=List[LoanResponse], tags=["Loans"])
def get_loans(skip: int = 0, limit: int = 300, db: Session = Depends(get_db)):
    return crud.get_loans(db, skip=skip, limit=limit)

@app.get("/loans/active", response_model=List[LoanResponse], tags=["Loans"])
def get_active_loans(db: Session = Depends(get_db)):
    return crud.get_active_loans(db)

@app.get("/loans/overdue", response_model=List[LoanResponse], tags=["Loans"])
def get_overdue_loans(db: Session = Depends(get_db)):
    return crud.get_overdue_loans(db, today=date.today())

@app.get("/loans/{loan_id}", response_model=LoanResponse, tags=["Loans"])
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="대출 기록을 찾을 수 없습니다.")
    return loan

@app.patch("/loans/{loan_id}/return", response_model=LoanResponse, tags=["Loans"])
def return_loan(loan_id: int, return_data: LoanReturn, db: Session = Depends(get_db)):
    result, err = crud.return_loan(db, loan_id, return_data)
    if not result:
        raise HTTPException(status_code=400, detail=err)
    return result

@app.patch("/loans/{loan_id}/extend", response_model=LoanResponse, tags=["Loans"])
def extend_loan(loan_id: int, extend_data: LoanExtend, db: Session = Depends(get_db)):
    """대출 연장 — 등급별 최대 연장일 제한"""
    result, err = crud.extend_loan(db, loan_id, extend_data)
    if not result:
        raise HTTPException(status_code=400, detail=err)
    return result