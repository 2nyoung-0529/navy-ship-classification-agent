# 🚢 Korean Navy Ship Classification Agent

![CI](https://github.com/2nyoung-0529/korean-navy-ship-classification-agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude-orange?logo=anthropic)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?logo=fastapi)
![pandas](https://img.shields.io/badge/pandas-CSV-lightgrey?logo=pandas)
![License](https://img.shields.io/badge/license-MIT-blue)

**자연어 → Tool Use → CSV** 패턴으로 구현한 Claude 에이전트 데모.  
함번·함명·함종을 자연어로 질문하면 대한민국 해군 현역·건조 중 함정 정보를 조회합니다.

> **면책:** 공식 해군·국방부 자료가 아닙니다. 데이터 기준 시점: 2026-07-01.

---

## 이 프로젝트에서 한 일

- **Claude Tool Use 설계** — 함번·함명·함종·함급·함종목록 5개 Tool schema 설계 및 dispatcher 구현
- **멀티턴 history 처리** — 대화 맥락을 유지하며 연속 질문 처리
- **운영 방어 코드** — tool loop 상한(5회), 결과 상한(50척), startup API key 검증, Pydantic 입력 검증
- **다중 인터페이스** — CLI / FastAPI REST API / Gradio 웹 UI 동시 지원
- **테스트 17개 + CI** — API 키 없이 실행 가능한 단위·통합 테스트, GitHub Actions 연동

---

## 예시 질문

| 질문 | 사용 Tool |
|---|---|
| `DDH-975가 뭐야?` | `search_by_hull_number` |
| `충무공이순신함 함번이 뭐야?` | `search_by_name` |
| `현역 구축함 목록 알려줘` | `list_by_type` |
| `세종대왕급 몇 척이야?` | `search_by_class` |
| `어떤 함종이 있어?` | `list_ship_types` |
| `DDG-997 함선명이 뭐야?` | `search_by_hull_number` → 건조중 안내 |

---

## 빠른 시작

### 요구 사항

- Python 3.10+
- [Anthropic API 키](https://console.anthropic.com/)

### 1. 설치

```bash
git clone https://github.com/2nyoung-0529/korean-navy-ship-classification-agent.git
cd korean-navy-ship-classification-agent

pip install -r requirements.txt
```

### 2. 환경 변수

```bash
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY=sk-ant-... 입력
```

### 3. 실행

**Gradio 웹 UI (추천)**

```bash
python app_gradio.py
# http://localhost:7860
```

**CLI**

```bash
python client.py
```

**REST API**

```bash
uvicorn server:app --reload
# http://localhost:8000/docs
```

> `data/warships.sample.csv` (15척)가 기본 포함되어 있어 전체 데이터 없이도 바로 실행됩니다.  
> 전체 137척은 `data/warships.csv`를 별도로 준비하면 자동으로 사용됩니다.

---

## 아키텍처

```
사용자
  │
  ├─ client.py       (CLI)
  ├─ server.py       (FastAPI)
  └─ app_gradio.py   (Gradio)
          │
          ▼
      agent.py            Claude Tool Use 루프 (최대 5회)
          │
          ▼
  tools/warship_tools.py
    ├─ search_by_hull_number
    ├─ search_by_name
    ├─ list_by_type
    ├─ list_ship_types
    └─ search_by_class
          │
          ▼
      data/warships.csv (또는 warships.sample.csv)
```

→ 설계 배경: [docs/DESIGN.md](docs/DESIGN.md)

---

## API 명세

### `POST /chat`

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "현역 구축함 목록 알려줘"}'
```

| 필드 | 타입 | 필수 |
|---|---|---|
| `message` | string | O |
| `history` | `[{"role": "user"\|"assistant", "content": "..."}]` | X |

```json
{ "reply": "..." }
```

| Method | Path | 설명 |
|---|---|---|
| GET | `/` | 상태 확인 |
| GET | `/health` | 헬스 체크 |
| POST | `/chat` | 에이전트 대화 |

---

## 테스트

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

API 키 없이 실행 가능합니다 (sample CSV + mock 사용).

---

## 프로젝트 구조

```
.
├── agent.py              # WarshipAgent, Tool Use 루프
├── client.py             # 대화형 CLI
├── server.py             # FastAPI 서버
├── app_gradio.py         # Gradio 웹 UI
├── tools/
│   └── warship_tools.py  # Tool 스키마·함수·dispatcher
├── data/
│   ├── warships.sample.csv   # 15척 샘플 (repo 포함)
│   └── warships.csv          # 전체 137척 (로컬 준비)
├── tests/
│   ├── test_tools.py
│   └── test_server.py
├── docs/
│   └── DESIGN.md
├── archive/
│   └── app_streamlit.py  # (legacy)
├── .github/workflows/ci.yml
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

---

## 환경 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | O | — | Anthropic API 키 |
| `WARSHIP_MODEL` | X | `claude-opus-4-6` | 사용할 Claude 모델 |
| `WARSHIP_MAX_TOKENS` | X | `1024` | 응답 최대 토큰 |
| `WARSHIP_MAX_TOOL_LOOPS` | X | `5` | Tool 루프 상한 |
| `WARSHIPS_CSV` | X | `data/warships.csv` | 데이터 파일 경로 |

---

## 알려진 제한

- 퇴역함은 데이터에 없어 조회 불가
- 데이터 기준 시점: 2026-07-01 (실시간 업데이트 없음)
- API 서버에 인증·Rate limit 없음 (공개 배포 시 별도 설정 필요)

---

## License

[MIT](LICENSE)
