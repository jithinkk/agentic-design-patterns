from shared.llm.hf_llm import HFLLM

llm = HFLLM()


def call_model(state):
    messages = state["messages"]

    response_text = llm.invoke(messages)

    return {
        "messages": messages + [
            {"role": "assistant", "content": response_text}
        ]
    }