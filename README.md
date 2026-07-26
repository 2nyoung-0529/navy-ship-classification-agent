# Warship Agent

대한민국 해군 함정 정보를 **자연어**로 조회하는 AI 에이전트입니다.  
[Anthropic Claude](https://www.anthropic.com/)의 **Tool Use**로 함번·함명·함종 질의를 처리하고, CSV 기반 함정 데이터에서 답을 찾습니다.

> **면책:** 본 프로젝트는 공식 해군·국방부 자료가 아닙니다. 함정 정보는 제공된 데이터 기준이며, 실제 배치·운용 상태와 다를 수 있습니다.

---

## 주요 기능

- 함번(예: `DDH-975`), 함명(예: `충무공이순신`), 함종(예: `구축함`)으로 조회
- Claude가 질문 의도에 맞는 Tool을 선택해 **다단계 조회** 후 한국어로 답변
- CLI, REST API, Streamlit, Gradio 등 **여러 실행 방식** 지원
- 멀티턴 대화(이전 질문 맥락 유지)

---

## 빠른 시작

### 요구 사항

- Python 3.10+
- [Anthropic API 키](https://console.anthropic.com/)

### 1. 저장소 클론 및 설치

```bash
git clone https://github.com/2nyoung-0529/korean-navy-ship-classification-agent.git
cd korean-navy-ship-classification-agent

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. 환경 변수

```bash
cp .env.example .env
```

`.env` 파일에 API 키를 입력합니다.

```env
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. 함정 데이터 준비

`data/warships.csv`가 필요합니다. 저장소에 데이터가 포함되지 않은 경우, 아래 구조에 맞춰 파일을 `data/warships.csv`에 두세요.

| 컬럼 (필수) | 설명 |
|-------------|------|
| `함종` | 구축함, 호위함 등 |
| `함번 코드` | DDH, DDG, PKG 등 |
| `전체함번` | DDH-975 형식 |
| `함명` | 충무공이순신 등 |
| `함급` | 함급명 |
| `취역` | 취역일 |
| `소속` | 소속 전대·함대 |
| `운용상태` | 현역, 건조중 등 |

데이터 출처 예: 공개 군함 세부 정보(프로젝트 내부 기준 파일명: `군함세부정보_20260701`).  
범위: 대한민국 해군 **현역·건조 중 등 124척** 수준(데이터 파일 기준).

### 4. 실행

**CLI**

```bash
python client.py
```

**REST API**

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Streamlit UI** (별도 설치: `pip install streamlit`)

```bash
streamlit run app.py
```

**Gradio UI** (별도 설치: `pip install gradio`)

```bash
python app_gradio.py
```

---

## 사용 예시

### CLI

```
질문: DDH-975가 뭐야?

에이전트: DDH-975는 충무공이순신함입니다.
- 함종: 구축함 / 함급: 충무공이순신급
- 취역: 2003-12-02 / 소속: 제71기동전대
```

### API

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "현역 구축함 목록 알려줘"}'
```

**요청**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `message` | string | O | 사용자 질문 |
| `history` | array | X | 이전 대화 `[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]` |

**응답**

```json
{
  "reply": "..."
}
```

**엔드포인트**

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/` | 서비스 상태 |
| `GET` | `/health` | 헬스 체크 |
| `POST` | `/chat` | 에이전트 대화 |

---

## 아키텍처

```
사용자
  │
  ├─ client.py          (CLI)
  ├─ server.py          (FastAPI)
  ├─ app.py             (Streamlit)
  └─ app_gradio.py      (Gradio)
          │
          ▼
      agent.py                    Claude Tool Use 루프
          │  tool_use
          ▼
  tools/warship_tools.py
    ├─ search_by_hull_number
    ├─ search_by_name
    └─ list_by_type
          │
          ▼
      data/warships.csv
```

### Tool 목록

| Tool | 설명 | 예시 |
|------|------|------|
| `search_by_hull_number` | 함번·함번 코드 조회 | `DDH-975`, `PKG` |
| `search_by_name` | 함명 조회 | `세종대왕`, `충무공이순신` |
| `list_by_type` | 함종별 목록 | `구축함`, `호위함` |

기본 모델: `claude-opus-4-6` (`agent.py`에서 설정).

---

## 프로젝트 구조

```
.
├── agent.py              # WarshipAgent, Tool Use 루프, 시스템 프롬프트
├── client.py             # 대화형 CLI
├── server.py             # FastAPI 서버
├── app.py                # Streamlit 채팅 UI
├── app_gradio.py         # Gradio 채팅 UI
├── tools/
│   └── warship_tools.py  # Tool 스키마, CSV 검색, run_tool()
├── data/
│   └── warships.csv      # 함정 데이터 (로컬 준비 필요)
├── requirements.txt      # 핵심 의존성 (anthropic, fastapi, pandas 등)
├── .env.example
└── README.md
```

---

## 환경 변수

| 변수 | 필수 | 설명 |
|------|------|------|
| `ANTHROPIC_API_KEY` | O | Anthropic API 키 |

---

## 알려진 제한

- **퇴역함**은 데이터에 없어 조회할 수 없습니다.
- `운용상태`가 현역이 아닌 함(건조중, 진수 등)은 에이전트가 별도로 안내합니다.
- API 서버에는 **인증·Rate limit**이 없습니다. 공개 배포 시 별도 보안 설정이 필요합니다.
- Streamlit·Gradio는 `requirements.txt`에 포함되지 않았습니다.
- Tool Use 루프에 **최대 반복 상한**이 없어, 예외 상황에서 장시간 대기할 수 있습니다.

---

## 개발 참고

| 목적 | 수정 파일 |
|------|-----------|
| 조회 Tool 추가·변경 | `tools/warship_tools.py` |
| 답변 톤·규칙 | `agent.py`의 `SYSTEM_PROMPT` |
| HTTP API | `server.py` |
| 웹 UI | `app.py` 또는 `app_gradio.py` |

---

## 라이선스

라이선스 파일이 아직 없습니다. 공개 저장소에 올릴 경우 MIT 등 라이선스 추가를 권장합니다.  
함정 **원본 데이터**의 재배포 가능 여부는 출처 이용 조건을 따르세요.

---

## 기여

Issue·Pull Request 환영합니다. 데이터 경로(`data/warships.csv`)는 커밋하지 말고, 샘플 데이터나 문서로 대체하는 방식을 권장합니다.
