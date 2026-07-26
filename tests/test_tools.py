"""
Tool 함수 단위 테스트 — API 키 불필요, sample CSV 사용
"""
import os

# sample CSV 강제 사용
os.environ["WARSHIPS_CSV"] = str(
    __import__("pathlib").Path(__file__).parent.parent / "data" / "warships.sample.csv"
)

# 모듈 import는 env 설정 후
import tools.warship_tools as wt

# 캐시 초기화 (env 변경 반영)
wt._df = None


# ── search_by_hull_number ─────────────────────────────────────────────────

def test_hull_exact_match():
    result = wt.search_by_hull_number("DDH-975")
    assert result["found"] is True
    assert result["count"] == 1
    assert result["ships"][0]["함명"] == "충무공이순신"


def test_hull_prefix_match():
    result = wt.search_by_hull_number("DDH")
    assert result["found"] is True
    assert result["count"] >= 1


def test_hull_not_found():
    result = wt.search_by_hull_number("XXX-999")
    assert result["found"] is False
    assert "찾을 수 없습니다" in result["message"]


# ── search_by_name ────────────────────────────────────────────────────────

def test_name_exact_match():
    result = wt.search_by_name("충무공이순신")
    assert result["found"] is True
    assert result["ships"][0]["함번"] == "DDH-975"


def test_name_partial_match():
    result = wt.search_by_name("세종")
    assert result["found"] is True
    assert any("세종" in s["함명"] for s in result["ships"])


def test_name_not_found():
    result = wt.search_by_name("존재하지않는함정")
    assert result["found"] is False


# ── list_by_type ──────────────────────────────────────────────────────────

def test_list_by_type_found():
    result = wt.list_by_type("구축함")
    assert result["found"] is True
    assert result["count"] >= 1
    assert all(s["함종"] == "구축함" for s in result["ships"])


def test_list_by_type_not_found():
    result = wt.list_by_type("우주선")
    assert result["found"] is False


# ── list_ship_types ───────────────────────────────────────────────────────

def test_list_ship_types():
    result = wt.list_ship_types()
    assert result["found"] is True
    assert result["total_types"] >= 1
    assert isinstance(result["types"], list)
    assert "함종" in result["types"][0]
    assert "척수" in result["types"][0]


# ── search_by_class ───────────────────────────────────────────────────────

def test_search_by_class_found():
    result = wt.search_by_class("세종대왕급")
    assert result["found"] is True
    assert result["count"] >= 1


def test_search_by_class_not_found():
    result = wt.search_by_class("없는급")
    assert result["found"] is False


# ── run_tool dispatcher ───────────────────────────────────────────────────

def test_run_tool_unknown():
    result = wt.run_tool("nonexistent_tool", {})
    assert "error" in result


def test_result_limit(monkeypatch):
    """결과 상한(RESULT_LIMIT) 초과 시 truncated 플래그 확인"""
    import pandas as pd
    # 60행짜리 가짜 DataFrame
    fake = pd.DataFrame({
        "함종": ["구축함"] * 60,
        "전체함번": [f"DDH-{i}" for i in range(60)],
        "함명": [f"함정{i}" for i in range(60)],
        "함급": ["테스트급"] * 60,
        "취역": ["-"] * 60,
        "소속": ["-"] * 60,
        "운용상태": ["현역"] * 60,
    })
    result = wt._format_rows(fake)
    assert result["count"] == wt.RESULT_LIMIT
    assert result.get("truncated") is True
    assert result["total"] == 60
