import os
from pathlib import Path

import pandas as pd

_BASE = Path(__file__).parent.parent / "data"
_FULL_CSV = _BASE / "warships.csv"
_SAMPLE_CSV = _BASE / "warships.sample.csv"

RESULT_LIMIT = 50  # context 폭주 방지

_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    global _df
    if _df is None:
        # env 또는 full CSV 우선, 없으면 sample로 fallback
        custom = os.environ.get("WARSHIPS_CSV")
        if custom:
            path = Path(custom)
        elif _FULL_CSV.exists():
            path = _FULL_CSV
        else:
            path = _SAMPLE_CSV
        _df = pd.read_csv(path, dtype=str).fillna("")
    return _df


# ── Tool 정의 (Claude API schema) ──────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "search_by_hull_number",
        "description": (
            "함번(예: DDH-975, PKG-711)으로 함정을 조회합니다. "
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
        "description": "함명(함정 이름)으로 함정을 조회합니다.",
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
        "description": "함종으로 함정 목록을 조회합니다.",
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
    {
        "name": "list_ship_types",
        "description": "데이터에 존재하는 모든 함종 목록과 척수를 반환합니다. '어떤 함종 있어?' 같은 탐색 질문에 사용합니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "search_by_class",
        "description": "함급(예: 세종대왕급, 충무공이순신급)으로 함정을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ship_class": {
                    "type": "string",
                    "description": "조회할 함급 (예: 세종대왕급, 충무공이순신급, 인천급)",
                }
            },
            "required": ["ship_class"],
        },
    },
]


# ── Tool 실행 함수 ─────────────────────────────────────────────────────────

def search_by_hull_number(hull_number: str) -> dict:
    df = _load()
    q = hull_number.strip().upper()

    exact = df[df["전체함번"].str.upper() == q]
    if not exact.empty:
        return _format_rows(exact)

    prefix = df[df["함번 코드"].str.upper() == q]
    if not prefix.empty:
        return _format_rows(prefix)

    partial = df[df["전체함번"].str.upper().str.contains(q, na=False)]
    if not partial.empty:
        return _format_rows(partial)

    return {"found": False, "message": f"'{hull_number}'에 해당하는 함정을 찾을 수 없습니다."}


def search_by_name(name: str) -> dict:
    df = _load()
    q = name.strip()

    exact = df[df["함명"] == q]
    if not exact.empty:
        return _format_rows(exact)

    partial = df[df["함명"].str.contains(q, na=False)]
    if not partial.empty:
        return _format_rows(partial)

    return {"found": False, "message": f"'{name}'에 해당하는 함정을 찾을 수 없습니다."}


def list_by_type(ship_type: str) -> dict:
    df = _load()
    q = ship_type.strip()

    result = df[df["함종"].str.contains(q, na=False)]
    if not result.empty:
        return _format_rows(result)

    return {"found": False, "message": f"'{ship_type}' 함종의 함정을 찾을 수 없습니다."}


def list_ship_types() -> dict:
    df = _load()
    counts = df["함종"].value_counts().to_dict()
    types = [{"함종": k, "척수": v} for k, v in sorted(counts.items())]
    return {"found": True, "total_types": len(types), "types": types}


def search_by_class(ship_class: str) -> dict:
    df = _load()
    q = ship_class.strip()

    exact = df[df["함급"] == q]
    if not exact.empty:
        return _format_rows(exact)

    partial = df[df["함급"].str.contains(q, na=False)]
    if not partial.empty:
        return _format_rows(partial)

    return {"found": False, "message": f"'{ship_class}' 함급의 함정을 찾을 수 없습니다."}


# ── 공통 포맷터 ────────────────────────────────────────────────────────────

def _format_rows(df: pd.DataFrame) -> dict:
    ships = []
    for _, row in df.head(RESULT_LIMIT).iterrows():
        ships.append({
            "함종": row["함종"],
            "함번": row["전체함번"],
            "함명": row["함명"],
            "함급": row["함급"],
            "취역": row["취역"],
            "소속": row["소속"],
            "운용상태": row["운용상태"],
        })
    total = len(df)
    result = {"found": True, "count": len(ships), "ships": ships}
    if total > RESULT_LIMIT:
        result["truncated"] = True
        result["total"] = total
    return result


# ── Tool 디스패처 ──────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> dict:
    if name == "search_by_hull_number":
        return search_by_hull_number(**inputs)
    elif name == "search_by_name":
        return search_by_name(**inputs)
    elif name == "list_by_type":
        return list_by_type(**inputs)
    elif name == "list_ship_types":
        return list_ship_types()
    elif name == "search_by_class":
        return search_by_class(**inputs)
    else:
        return {"error": f"알 수 없는 tool: {name}"}
