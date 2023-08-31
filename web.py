import gradio as gr
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from typing import Optional, Tuple
from chains.slot_memory import SlotMemory
from chains.prompt import CHAT_PROMPT
from configs.params import ModelParams

model_config = ModelParams()

chain: ConversationChain


def initial_chain():
    llm = ChatOpenAI(temperature=model_config.temperature, openai_api_key=model_config.openai_api_key)
    memory = SlotMemory(llm=llm)
    global chain
    chain = ConversationChain(llm=llm, memory=memory, prompt=CHAT_PROMPT)


def clear_session():
    initial_chain()
    return [], []


def slot_format(slot_dict):
    result = f"name: {slot_dict['name']}\norigin: {slot_dict['origin']}\ndestination: {slot_dict['destination']}\ndeparture_time: {slot_dict['departure_time']}\n"
    return result


def predict(command, history: Optional[Tuple[str, str]]):
    history = history or []
    response = chain.run(input=command)
    current_slot = chain.memory.current_slots
    history.append((command, response))
    return history, history, '', slot_format(current_slot)


if __name__ == "__main__":
    title = """
    # Dialogue Slot Filling Demo
    """
    with gr.Blocks() as demo:
        gr.Markdown(title)

        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot()
                user_input = gr.Textbox(show_label=False, placeholder="Input...", container=False)
                with gr.Row():
                    submitBtn = gr.Button("🚀Submit", variant="primary")
                    emptyBtn = gr.Button("🧹Clear History")
            slot_show = gr.Textbox(label="current_slot", lines=20, interactive=False, scale=1)

        initial_chain()
        state = gr.State([])

        submitBtn.click(fn=predict, inputs=[user_input, state], outputs=[chatbot, state, user_input, slot_show])
        emptyBtn.click(fn=clear_session, inputs=[], outputs=[chatbot, state])

    demo.queue().launch(share=False, inbrowser=True, server_name="0.0.0.0", server_port=8000)
