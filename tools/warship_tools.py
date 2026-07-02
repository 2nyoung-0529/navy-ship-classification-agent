import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "warships.csv"

_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
    return _df


# ── Tool 정의 (Claude API schema) ──────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "search_by_hull_number",
        "description": (
            "함번(예: DDH-975, PKG-711)으로 현역 함정을 조회합니다. "
            "함번 코드만(예: DDH) 입력하면 해당 코드의 함정 목록을 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "hull_number": {
                    "type": "string",
                    "description": "조회할 함번 또는 함번 코드 (예: DDH-975, PKG, FF-815)",
                }
            },
            "required": ["hull_number"],
        },
    },
    {
        "name": "search_by_name",
        "description": "함명(함정 이름)으로 현역 함정을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "조회할 함명 (예: 충무공이순신, 광개토대왕)",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "list_by_type",
        "description": "함종으로 현역 함정 목록을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ship_type": {
                    "type": "string",
                    "description": "조회할 함종 (예: 구축함, 호위함, 고속함, 잠수함구조함)",
                }
            },
            "required": ["ship_type"],
        },
    },
]


# ── Tool 실행 함수 ─────────────────────────────────────────────────────────

def search_by_hull_number(hull_number: str) -> dict:
    df = _load()
    q = hull_number.strip().upper()

    # 전체 함번 정확히 일치 (예: DDH-975)
    exact = df[df["전체함번"].str.upper() == q]
    if not exact.empty:
        return _format_rows(exact)

    # 함번 코드 접두어 일치 (예: DDH)
    prefix = df[df["함번 코드"].str.upper() == q]
    if not prefix.empty:
        return _format_rows(prefix)

    # 부분 일치
    partial = df[df["전체함번"].str.upper().str.contains(q, na=False)]
    if not partial.empty:
        return _format_rows(partial)

    return {"found": False, "message": f"'{hull_number}'에 해당하는 현역 함정을 찾을 수 없습니다."}


def search_by_name(name: str) -> dict:
    df = _load()
    q = name.strip()

    exact = df[df["함명"] == q]
    if not exact.empty:
        return _format_rows(exact)

    partial = df[df["함명"].str.contains(q, na=False)]
    if not partial.empty:
        return _format_rows(partial)

    return {"found": False, "message": f"'{name}'에 해당하는 현역 함정을 찾을 수 없습니다."}


def list_by_type(ship_type: str) -> dict:
    df = _load()
    q = ship_type.strip()

    result = df[df["함종"].str.contains(q, na=False)]
    if not result.empty:
        return _format_rows(result)

    return {"found": False, "message": f"'{ship_type}' 함종의 현역 함정을 찾을 수 없습니다."}


# ── 공통 포맷터 ────────────────────────────────────────────────────────────

def _format_rows(df: pd.DataFrame) -> dict:
    ships = []
    for _, row in df.iterrows():
        ships.append({
            "함종": row["함종"],
            "함번": row["전체함번"],
            "함명": row["함명"],
            "함급": row["함급"],
            "취역": row["취역"],
            "소속": row["소속"],
            "운용상태": row["운용상태"],
        })
    return {"found": True, "count": len(ships), "ships": ships}


# ── Tool 디스패처 ──────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> dict:
    if name == "search_by_hull_number":
        return search_by_hull_number(**inputs)
    elif name == "search_by_name":
        return search_by_name(**inputs)
    elif name == "list_by_type":
        return list_by_type(**inputs)
    else:
        return {"error": f"알 수 없는 tool: {name}"}
