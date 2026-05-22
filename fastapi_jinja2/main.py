"""
Week 12 실습 - FastAPI + Jinja2 통합 (클래식 음악 플레이리스트 웹 서비스)

수업 핵심 구조:
  요청 → FastAPI → 데이터 생성
       → templates/playlist.html ({{ }} 변수 치환)
                ↓ extends
           templates/base.html
                ↓ link/script
           static/style.css
           static/script.js

Step 1 (/) → HTML 문자열 직접 반환
Step 2 (/now-playing) → Jinja2 인라인 템플릿 (HTML이 Python 안에)
Step 3 (/playlist) → 외부 템플릿 파일 + 정적 파일 완전 분리 (완성형)

실행: uvicorn main:app --reload
"""

import os
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Template

app = FastAPI()

# 정적 파일 마운트 (CSS, JS)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 외부 템플릿 폴더 지정
templates = Jinja2Templates(directory="templates")


# ──────────────────────────────────────────────────────────────
# Step 1. HTML 문자열 직접 반환
# 단순하지만 HTML이 Python 코드 안에 섞여 있어 유지보수 어려움
# ──────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head><meta charset="UTF-8"><title>Classical Music API</title></head>
    <body style="font-family: serif; padding: 2rem; background: #faf8f3;">
        <h1>🎼 Classical Music API</h1>
        <ul>
            <li><a href="/now-playing">지금 연주 중 (Step 2)</a></li>
            <li><a href="/playlist">플레이리스트 (Step 3 - 완성형)</a></li>
        </ul>
    </body>
    </html>
    """


# ──────────────────────────────────────────────────────────────
# Step 2. Jinja2 인라인 템플릿 (HTML이 여전히 Python 안에)
# Template(html_str).render(변수=값) 형태
# ──────────────────────────────────────────────────────────────
PIECES = [
    "교향곡 5번 다단조 — 베토벤",
    "피아노 협주곡 21번 — 모차르트",
    "사계 봄 — 비발디",
    "피아노 소나타 14번 월광 — 베토벤",
    "현악 세레나데 — 차이콥스키",
    "볼레로 — 라벨",
]

@app.get("/now-playing", response_class=HTMLResponse)
def now_playing():
    piece = random.choice(PIECES)

    html_template = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8"><title>Now Playing</title>
        <style>
            body {
                height: 100vh;
                display: flex; flex-direction: column;
                justify-content: center; align-items: center;
                background: #1c1510; color: #f0e6d3;
                font-family: serif;
            }
            .piece { font-size: 2rem; margin: 1rem 0; text-align: center; }
        </style>
    </head>
    <body>
        <p>🎼 지금 연주 중</p>
        <div class="piece">{{ piece }}</div>
        <a href="/playlist" style="color:#aaa; margin-top:2rem;">전체 플레이리스트 →</a>
    </body>
    </html>
    """
    return Template(html_template).render(piece=piece)


# ──────────────────────────────────────────────────────────────
# Step 3. 외부 템플릿 + 정적 파일 완전 분리 (완성형)
# Python은 데이터만, HTML/CSS/JS는 각각 외부 파일로 분리
# ──────────────────────────────────────────────────────────────
PLAYLIST = [
    {"id": 1, "title": "교향곡 5번 다단조",      "composer": "베토벤",    "period": "고전주의", "duration": 33},
    {"id": 2, "title": "피아노 협주곡 21번",      "composer": "모차르트",  "period": "고전주의", "duration": 30},
    {"id": 3, "title": "사계 — 봄",               "composer": "비발디",    "period": "바로크",   "duration": 11},
    {"id": 4, "title": "피아노 소나타 14번 월광", "composer": "베토벤",    "period": "고전주의", "duration": 17},
    {"id": 5, "title": "현악 세레나데",           "composer": "차이콥스키","period": "낭만주의", "duration": 29},
]

@app.get("/playlist", response_class=HTMLResponse)
def playlist(request: Request):
    context = {
        "playlist_name": "클래식 명곡 플레이리스트",
        "pieces": PLAYLIST,
        "featured_id": random.randint(1, 5),   # 매 요청마다 다른 곡 추천
    }
    return templates.TemplateResponse(
        request=request, name="playlist.html", context=context
    )


@app.get("/piece/{piece_id}", response_class=HTMLResponse)
def piece_detail(request: Request, piece_id: int):
    piece = next((p for p in PLAYLIST if p["id"] == piece_id), None)
    context = {"piece": piece, "piece_id": piece_id}
    return templates.TemplateResponse(
        request=request, name="piece.html", context=context
    )
