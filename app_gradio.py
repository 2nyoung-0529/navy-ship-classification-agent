import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from agent import WarshipAgent

agent = WarshipAgent()


def chat(user_message: str, history: list):
    if not user_message.strip():
        return "", history

    # Gradio 6.x history: [{"role": "user", "content": ...}, ...]
    api_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history
    ]

    reply = agent.chat(user_message, api_history or None)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    return "", history


with gr.Blocks(title="해군 함정 조회 에이전트") as demo:
    gr.Markdown("# 🚢 대한민국 해군 함정 조회")
    gr.Markdown("함번·함명·함종으로 현역 및 건조 중 함정을 조회합니다. (퇴역함 제외)")

    chatbot = gr.Chatbot(
        height=500,
        show_label=False,
    )

    with gr.Row():
        txt = gr.Textbox(
            placeholder="예: 전차상륙함 목록 알려줘 / DDG-997 함선명이 뭐야?",
            show_label=False,
            scale=5,
        )
        btn = gr.Button("전송", scale=1, variant="primary")

    gr.Examples(
        examples=[
            ["현역 구축함 목록 알려줘"],
            ["DDH-975가 뭐야?"],
            ["세종대왕함 함번이 뭐야?"],
            ["전차상륙함 현역으로 몇 척이야?"],
            ["DDG-997 함선명이 뭐야?"],
        ],
        inputs=[txt],
        label="예시 질문",
    )

    txt.submit(chat, [txt, chatbot], [txt, chatbot])
    btn.click(chat, [txt, chatbot], [txt, chatbot])

if __name__ == "__main__":
    demo.launch()
