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

api_key = os.getenv("DASHSCOPE_API_KEY")
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
        # 初始化消息列表
        chat_messages = []
        
        # 添加系统提示（如果有）
        if prompt:
            chat_messages.append({"role": "system", "content": prompt})
        
        # 添加历史消息（如果有）
        if messages:
            chat_messages.extend(messages)
        
        # 添加当前问题
        chat_messages.append({"role": "user", "content": question})
        
        # 调用API
        response = client.chat.completions.create(
            model=model, 
            messages=chat_messages
        )
        answer = str(response.choices[0].message.content)
        
        return answer
    except Exception as e:
        print(f"LLM调用中发生错误：{e}")
        return "抱歉，处理您的请求时出现了错误。请稍后再试。"


# 提示词合集
retrieval_prompt = """你是一个专业的研究助手。结合历史信息中提供的帮助完成以下任务。请根据用户的研究主题，提供全面、准确的信息检索结果。
包括关键概念、最新发展、相关理论和应用领域。使用Markdown格式组织内容，包括标题、列表、代码块等。
确保信息结构清晰，分点说明。"""

explanation_prompt = """你是一个专业知识解释助手。结合历史信息中提供的帮助完成以下任务。请清晰、全面地解释用户询问的专业概念，包括定义、背景、相关理论、应用场景和实际例子。
使用易于理解的语言。使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"""

comparison_prompt = """你是一个专业的分析助手。结合历史信息中提供的帮助完成以下任务。请对用户提供的不同观点或理论进行全面的对比分析，包括各自的优点、缺点、适用场景和学术支持。提供平衡、客观的分析。
使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"""

outline_prompt = """你是一个专业的学术写作助手。结合历史信息中提供的帮助完成以下任务。请根据用户的研究主题，生成一个结构合理、内容全面的论文或报告大纲。
包括引言、文献综述、方法论、结果分析、结论等部分。使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"""

summary_prompt = """你是一个专业的学术研究助手。结合历史信息中提供的帮助完成以下任务。请对用户提供的文献内容进行摘要和分析，提炼关键观点、研究方法和结论。
使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"""

RESEARCH_TASKS = {
    "information_retrieval": {
        "name": "信息检索",  # 默认类型
        "system_prompt": retrieval_prompt
    },
    "concept_explanation": {
        "name": "概念解释",
        "system_prompt": explanation_prompt
    },
    "viewpoint_comparison": {
        "name": "观点对比",
        "system_prompt": comparison_prompt
    },
    "outline_generation": {
        "name": "大纲生成",
        "system_prompt": outline_prompt
    },
    "literature_summary": {
        "name": "文献摘要",
        "system_prompt": summary_prompt
    }
}
