import json
import os

import anthropic
from dotenv import load_dotenv

from tools.warship_tools import TOOL_SCHEMAS, run_tool

load_dotenv()

MODEL = os.environ.get("WARSHIP_MODEL", "claude-opus-4-6")
MAX_TOKENS = int(os.environ.get("WARSHIP_MAX_TOKENS", "1024"))
MAX_TOOL_LOOPS = int(os.environ.get("WARSHIP_MAX_TOOL_LOOPS", "5"))

SYSTEM_PROMPT = """당신은 대한민국 해군 함정 정보를 안내하는 전문 에이전트입니다.

역할:
- 함번(예: DDH-975, PKG-711)으로 함정을 조회합니다.
- 함명(예: 충무공이순신)으로 함정을 조회합니다.
- 함종(예: 구축함, 호위함)으로 함정 목록을 조회합니다.
- 함급(예: 세종대왕급)으로 함정을 조회합니다.
- 보유한 함종 목록을 안내합니다.

안내 원칙:
- 퇴역함은 데이터에 없으므로 안내할 수 없습니다.
- 운용상태가 '현역'이 아닌 경우(건조중, 진수, 계획 등) 반드시 현역 함정이 아님을 먼저 밝히고, 함번과 함명은 안내합니다.
- 질문이 모호하면 tool을 먼저 조회한 뒤 결과를 바탕으로 답변하세요.
- 결과가 여러 척이면 표 형태로 정리해서 보여주세요.
- 한국어로 답변하세요."""


class WarshipAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다. "
                ".env 파일을 확인하세요."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = MODEL

    def chat(self, user_message: str, history: list[dict] | None = None) -> str:
        messages = (history or []) + [{"role": "user", "content": user_message}]

        for _ in range(MAX_TOOL_LOOPS):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                return _extract_text(response)

            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if not tool_uses:
                return _extract_text(response)

            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_use in tool_uses:
                result = run_tool(tool_use.name, tool_use.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

            messages.append({"role": "user", "content": tool_results})

        return "요청 처리 중 반복 한계에 도달했습니다. 질문을 더 구체적으로 입력해 주세요."


def _extract_text(response) -> str:
    texts = [b.text for b in response.content if hasattr(b, "text")]
    return "\n".join(texts)
