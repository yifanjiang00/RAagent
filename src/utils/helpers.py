def format_output(data):
    """
    Formats the output data for better readability.
    
    Parameters:
    data (dict or list): The data to be formatted.

    Returns:
    str: A formatted string representation of the data.
    """
    if isinstance(data, dict):
        return "\n".join(f"{key}: {value}" for key, value in data.items())
    elif isinstance(data, list):
        return "\n".join(str(item) for item in data)
    else:
        return str(data)
    
import os
from openai import OpenAI

if not api_key:
    raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置！")

base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
client = OpenAI(api_key=api_key, base_url=base_url)

def call_llm(question, prompt=None, messages=None, model="qwen-plus") -> str:
    """
    调用大语言模型API生成回答

     Args:
         question: 用户提问
         prompt: 系统提示词（可选）
         messages: 已有的对话历史（可选）
         model: 模型名称，默认 qwen-plus

     Returns:
         模型生成的回答字符串
     """
    try:
        messages = messages if messages else []
        if prompt:
            messages.append({"role": "system", "content": prompt})
        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(model=model, messages=messages)
        answer = str(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM调用中发生错误：{e}")
        answer = "抱歉，出错了"
    messages.append({"role": "agent", "content": answer})

    return answer