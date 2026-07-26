# 설계 문서

## 1. 문제 정의

### 왜 이 프로젝트인가

대한민국 해군 함정 정보는 공개 출처에서 구조화된 형태로 제공되지 않아, 일반 사용자가 "DDH-975가 뭔지", "현역 구축함이 몇 척인지" 같은 간단한 질문에도 직접 검색해야 한다. 이 프로젝트는 자연어 질문으로 함정 정보를 조회할 수 있는 에이전트를 구현한다.

### 왜 CSV + Tool Use인가 (RAG 안 한 이유)

| 방식 | 장점 | 단점 | 이 프로젝트의 선택 |
|---|---|---|---|
| RAG (벡터 검색) | 대용량 비정형 문서에 강함 | 구현 복잡, 정확도 불안정 | ❌ |
| 프롬프트에 전체 데이터 삽입 | 구현 간단 | 토큰 낭비, context 한계 | ❌ |
| **Tool Use + CSV** | 정확한 필터링, 토큰 효율, 설계 명확 | 데이터가 정형이어야 함 | ✅ |

함정 데이터는 함번·함명·함종이 명확히 구조화된 정형 데이터다. 벡터 유사도보다 정확한 필터링이 훨씬 적합하고, Tool Use로 Claude가 질문 의도에 맞는 쿼리를 스스로 선택하게 하면 자연어 처리와 정확한 조회를 동시에 달성할 수 있다.

---

## 2. 아키텍처

```
사용자 질문
     │
     ▼
 [인터페이스 레이어]
  ├─ client.py      (CLI, 멀티턴)
  ├─ server.py      (FastAPI REST API)
  └─ app_gradio.py  (Gradio 웹 UI)
          │
          ▼
      agent.py  ── Claude Tool Use 루프 (최대 5회)
          │
          │  tool_use 요청
          ▼
  tools/warship_tools.py
    ├─ search_by_hull_number  (함번 조회)
    ├─ search_by_name         (함명 조회)
    ├─ list_by_type           (함종 목록)
    ├─ list_ship_types        (함종 카탈로그)
    └─ search_by_class        (함급 조회)
          │
          ▼
      data/warships.csv  (현역·건조 중 137척)
      data/warships.sample.csv  (15척, repo 포함)
```

---

## 3. Tool 설계 원칙

### 왜 5개 Tool로 분리했나

하나의 `search` Tool에 파라미터를 몰아넣는 대신, 의도별로 Tool을 분리했다.

- **명확한 schema** — Claude가 잘못된 파라미터를 넘길 가능성이 줄어든다.
- **테스트 용이** — Tool 함수 각각을 독립적으로 단위 테스트할 수 있다.
- **확장 가능** — 새 조회 유형 추가 시 기존 Tool에 영향 없이 추가만 하면 된다.

### 운영을 고려한 결정들

| 결정 | 이유 |
|---|---|
| Tool loop 최대 5회 | 비용 방어, 무한 루프 방지 |
| 결과 상한 50척 | context 폭주 방지 |
| `MODEL`, `MAX_TOKENS` env 분리 | 배포 환경별 설정 유연성 |
| startup API key 검증 | fail-fast — 잘못된 설정을 즉시 감지 |
| history Pydantic 검증 | API 입력 방어, role 오남용 차단 |
| sample CSV fallback | clone 후 바로 실행 가능 |

---

## 4. 한계

- **퇴역함 없음** — 데이터 범위가 현역·건조 중으로 한정된다.
- **데이터 시점** — 2026-07-01 기준 스냅샷. 실시간 업데이트 없음.
- **Hallucination 방지** — Claude가 tool 결과 외 정보를 지어낼 수 있다. 시스템 프롬프트로 tool 결과 grounding을 유도하지만 완전히 막지는 못한다.
- **한국어 IME** — Gradio 입력창에서 한글 조합 중 Enter 시 일부 브라우저에서 마지막 글자가 깨질 수 있다. 전송 버튼 클릭 권장.
- **인증 없음** — API 서버에 rate limit·인증이 없어 공개 배포 시 별도 보안 설정 필요.

---

## 5. 개선 로드맵

| 우선순위 | 항목 | 설명 |
|---|---|---|
| 높음 | 스트리밍 응답 | FastAPI SSE + Gradio streaming으로 UX 개선 |
| 높음 | Live Demo | Hugging Face Spaces 배포 |
| 중간 | SQLite 전환 | CSV 대신 DB로 복잡한 쿼리 지원 |
| 중간 | 취역연도 필터 Tool | "1990년대 취역함" 같은 질문 처리 |
| 낮음 | Docker | `docker compose up` 한 줄 실행 |
| 낮음 | 관리자 UI | 데이터 수정·추가 인터페이스 |
