# FastAPI + Jinja2 — 클래식 음악 플레이리스트

> 앱 프로그래밍 수업 12주차 실습  
> FastAPI에서 HTML 페이지를 반환하는 방법을 3단계로 나눠서 구현했습니다.  
> 단계가 올라갈수록 Python 코드와 HTML/CSS/JS가 점점 분리되는 구조를 익히는 게 핵심입니다.

---

## 왜 3단계로 나뉘나요?

FastAPI는 기본적으로 JSON을 반환하는 프레임워크입니다. 그런데 브라우저에 예쁜 화면을 보여주려면 HTML을 반환해야 하고, 여기서 "HTML을 어디에 작성하느냐"에 따라 코드 품질이 크게 달라집니다.

```
Step 1 → HTML을 Python 함수 안에 문자열로 직접 씀
           문제: HTML이 바뀔 때마다 Python 코드를 열어야 함

Step 2 → Jinja2 Template 객체로 변수를 HTML에 주입
           문제: HTML이 여전히 Python 코드 안에 있음 (관심사가 섞임)

Step 3 → HTML은 templates/ 폴더, CSS는 static/ 폴더로 완전히 분리
           Python은 데이터 준비만, 화면은 외부 파일이 담당 
```

---

##  배운 개념

### HTMLResponse

FastAPI는 기본적으로 모든 응답을 JSON으로 처리합니다. HTML을 반환하려면 `response_class=HTMLResponse`를 명시해줘야 브라우저가 HTML로 해석합니다. 이게 없으면 HTML 코드가 그냥 문자열로 보입니다.

```python
@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>안녕하세요</h1>"
```

### Jinja2 Template (인라인 방식, Step 2)

`Template(html_str).render(변수=값)` 형태로 Python 코드 안에서 HTML에 변수를 주입합니다. 매 요청마다 랜덤으로 곡이 바뀌는 `/now-playing` 페이지에서 사용했습니다.

```python
from jinja2 import Template

html = "<h1>지금 재생 중: {{ piece }}</h1>"
return Template(html).render(piece="교향곡 5번")
```

### Jinja2Templates (외부 파일 방식, Step 3)

`templates/` 폴더 안의 `.html` 파일을 불러와서 렌더링합니다. Python 코드는 데이터만 `context` 딕셔너리에 담아 넘기고, 실제 HTML 조립은 템플릿 파일이 합니다. `TemplateResponse`는 반드시 `request=request`를 첫 번째 인자로 전달해야 합니다.

```python
templates = Jinja2Templates(directory="templates")

@app.get("/playlist", response_class=HTMLResponse)
def playlist(request: Request):
    context = {"pieces": PLAYLIST, "featured_id": 3}
    return templates.TemplateResponse(request=request, name="playlist.html", context=context)
```

### StaticFiles

CSS, JS 같은 정적 파일은 `app.mount()`로 `/static` 경로에 연결합니다. 이렇게 하면 템플릿에서 `/static/style.css`처럼 경로로 바로 참조할 수 있습니다.

```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Jinja2 문법 정리

```html
{{ piece.title }}                           변수 출력

{% if piece.duration >= 25 %}               조건문
  <p>긴 곡이에요!</p>
{% endif %}

{% for piece in pieces %}                   반복문
  <li>{{ piece.title }}</li>
{% endfor %}

{% extends "base.html" %}                   템플릿 상속 — base.html의 틀을 가져옴

{% block content %}                         블록 영역 — 자식 템플릿이 이 안을 채움
  <h1>여기가 페이지 본문</h1>
{% endblock %}
```

---

##  각 파일이 하는 일

### `main.py`
서버의 핵심 파일입니다. 어떤 URL로 접속했을 때 어떤 함수를 실행할지 정의(라우팅)하고, 템플릿에 넘길 데이터를 준비합니다. Step 1~3이 모두 이 파일 안에 들어있습니다.

### `templates/base.html`
모든 페이지의 공통 틀입니다. `<nav>` 메뉴, CSS 링크, JS 링크가 여기 있습니다. 다른 템플릿들이 `{% extends "base.html" %}`로 이 파일을 상속받아서 공통 레이아웃을 재사용합니다. 메뉴를 수정하고 싶으면 이 파일 하나만 고치면 됩니다.

### `templates/playlist.html`
`/playlist` 페이지의 본문입니다. `base.html`을 상속받고, `{% for %}`로 곡 목록을 반복 출력합니다. `{% if piece.id == featured_id %}`로 오늘의 추천 곡에만 뱃지를 붙입니다.

### `templates/piece.html`
`/piece/{id}` 페이지의 본문입니다. 곡 상세 정보를 보여주고, 해당 id의 곡이 없을 때는 `{% if piece %}`로 분기해서 404 메시지를 표시합니다.

### `static/style.css`
전체 페이지의 디자인을 담당합니다. 크림색 배경과 골드 포인트 컬러로 클래식 음악 분위기를 표현했습니다. Python 코드와 완전히 분리되어 있어서 디자인만 바꾸고 싶을 때 이 파일만 수정하면 됩니다.

### `static/script.js`
페이지의 동적 기능을 담당합니다. 현재는 곡 제목을 클릭하면 클립보드에 복사하는 기능이 구현되어 있습니다.

---

##  실행 방법

```bash
pip install fastapi uvicorn jinja2

uvicorn main:app --reload
```

| 주소 | 단계 | 설명 |
|------|------|------|
| http://localhost:8000/ | Step 1 | HTML 문자열 직접 반환 |
| http://localhost:8000/now-playing | Step 2 | Jinja2 인라인 템플릿, 랜덤 곡 표시 |
| http://localhost:8000/playlist | Step 3 | 외부 템플릿 완성형, 전체 플레이리스트 |
| http://localhost:8000/piece/1 | Step 3 | 곡 상세 페이지 (id: 1~5) |
| http://localhost:8000/docs | — | Swagger 자동 문서 |
