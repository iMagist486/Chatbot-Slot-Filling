# Dialogue-Slot-Filling

[中文](README_CN.md) | [English](README.md)

### ✨ Overview

This project is a demo achieving entity extraction in dialogues, which can be used in AI assistant by combining with other actions.

The LLM is using OpenAI API.

Using booking flight as example.



### 📑 Implementation

inspiring by  [ujhrkzy/llm-slot-filling](https://github.com/ujhrkzy/llm-slot-filling), this project uses the `ConversationChain` and `ConversationBufferMemory` from Langchain. 

`SlotMemory` is a module to do entity extraction, store slot values and check information completeness, which based on `ConversationBufferMemory`.

`Prompt` and slot key in the `SlotMemory` can be modified according to task  in other various scenarios.



### 🔥 Screenshot

![demo](doc/demo.png)

The current_slot box displays the value of each slot, provides a more intuitive way to observe the performance.



### ❤️ Acknowledgments

1. [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
2. [ujhrkzy/llm-slot-filling](https://github.com/ujhrkzy/llm-slot-filling)