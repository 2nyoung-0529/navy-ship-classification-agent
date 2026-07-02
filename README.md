# Warship Agent

대한민국 해군 현역 함정 정보를 조회하는 AI 에이전트입니다.  
Claude의 Tool Use 기능을 활용해 함번·함명·함종 질의를 자연어로 처리합니다.

## 아키텍처

```
사용자 질문
     │
     ▼
 agent.py  ──────────────────────────────────────────────
  (Claude claude-opus-4-6)                                │
     │  tool_use 요청                                     │
     ▼                                                    │
tools/warship_tools.py                                    │
  ├─ search_by_hull_number  (함번 조회)                   │
  ├─ search_by_name         (함명 조회)                   │
  └─ list_by_type           (함종 목록)                   │
     │  결과 반환                                         │
     ▼                                                    │
 agent.py  → 최종 답변 생성 ──────────────────────────────┘
     │
     ▼
server.py (FastAPI /chat)  또는  client.py (CLI)
```

## 사용 가능한 Tool

| Tool | 설명 | 예시 입력 |
|---|---|---|
| `search_by_hull_number` | 함번으로 조회 | `DDH-975`, `PKG` |
| `search_by_name` | 함명으로 조회 | `충무공이순신`, `세종대왕` |
| `list_by_type` | 함종 목록 조회 | `구축함`, `호위함`, `고속함` |

## 데이터

- 출처: 군함세부정보_20260701
- 범위: 대한민국 해군 **현역 함정 124척**
- 컬럼: 함종, 함번, 함명, 함급, 취역일, 소속, 운용상태

## 설치 및 실행

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 입력
```

### 3-A. CLI로 실행

```bash
python client.py
```

```
==================================================
  대한민국 해군 현역 함정 조회 에이전트
  종료: 'exit' 또는 'quit' 입력
==================================================

질문: DDH-975가 뭐야?
에이전트: DDH-975는 **충무공이순신**함입니다.
- 함종: 구축함 / 함급: 충무공이순신급
- 취역: 2003-12-02 / 소속: 제71기동전대
```

### 3-B. API 서버로 실행

```bash
uvicorn server:app --reload
```

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "현역 구축함 목록 알려줘"}'
```

## 프로젝트 구조

```
warship_agent/
├── data/
│   └── warships.csv        # 현역 함정 124척 데이터
├── tools/
│   └── warship_tools.py    # Tool 함수 및 Claude schema 정의
├── agent.py                # Claude Tool Use 루프
├── server.py               # FastAPI 서버
├── client.py               # CLI 테스트 클라이언트
└── requirements.txt
```
