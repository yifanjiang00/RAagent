from utils.helpers import call_llm
import json

class Planner:
    def __init__(self):
        self.prompt = """你是一个智能科研助手的子模块，工作是辅助大语言模型高质量完成任务。请按照用户的意图(intent)和具体提问内容(query)拆解任务，制定工作计划。
        你有以下几个工具可以使用，它们的回复均为纯字符串。请设计调用链，我将根据你的要求进行调用。
        注意：只有最后一个任务的输出将作为最终答案回复给用户！
        注意：你必须严格按照规定的格式输出，[]外无任何字符，不得输出任何无关内容和多余的字符！
        1. Retriever: 调用LLM从网络检索相关内容。
            参数:
            topic (str): 需要检索的主题。
            messages(List[Dict[str, str]]): 对话历史（可选）
            返回:
            str: 关于该主题的网络内容。
        2. Summarizer: 调用LLM总结text内容。
            参数:
            text(str): 待总结内容。
            messages(List[Dict[str, str]]): 对话历史（可选）
            返回:
            str: 对该内容的详细解释。
        3. Comparer: 调用LLM检索相关主题的不同观点并进行比较。
            参数:
            text(str): 待比较的主题。
            messages(List[Dict[str, str]]): 对话历史（可选）
            返回:
            str: 对相关主题观点的详细比较。
        4. Explainer: 调用LLM详细解释特定的专业术语及其背景知识。
            参数:
            concept (str): 需要解释的专业术语。
            messages(List[Dict[str, str]]): 对话历史（可选）
            返回:
            str: 对该术语的详细解释和相关背景知识。
        5. OutlineGenerator: 调用LLM根据主题生成详细的提纲
            参数:
            topic (str): 需要生成提纲的主题
            messages(List[Dict[str, str]]): 对话历史（可选）
            返回:
            str: 结构化提纲
        你必须严格遵守的返回格式：列表，其中每条指令为形如{"name": 工具名称, "content": 第一参数}的字典。
        第一参数content可以为str字符串或由0开始的int索引，当它为字符串时将直接作为工具的输入，当它为索引时将使用第int条指令的输出作为工具的输入。
        一定不要返回空列表。
        在输出前，务必检查是否符合输出格式，以及工具名称是否在可用工具内，否则可能导致程序崩溃！
        """
    def reply(self, question, messages=None):
        tasks = call_llm(question, self.prompt, messages=messages)
        """ 可在命令行查看规划流程 """
        print("任务规划：",tasks)
        tasks = json.loads(tasks)

        return tasks
