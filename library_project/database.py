from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. 데이터베이스 엔진 생성 (SQLite 사용)
SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 전용 옵션
)

# 2. 세션 팩토리 생성
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 3. 모든 모델의 기반 클래스
Base = declarative_base()


# 4. 의존성 주입용 DB 세션 제공 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
