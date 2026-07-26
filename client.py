"""
CLI 테스트 클라이언트
사용법: python client.py
"""
from agent import WarshipAgent


def main():
    agent = WarshipAgent()
    history: list[dict] = []

    print("=" * 50)
    print("  대한민국 해군 현역 함정 조회 에이전트")
    print("  종료: 'exit' 또는 'quit' 입력")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("질문: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("종료합니다.")
            break

        reply = agent.chat(user_input, history if history else None)

        # 멀티턴을 위해 history 업데이트
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})

        print(f"\n에이전트: {reply}\n")


if __name__ == "__main__":
    main()
