from utils.helpers import call_llm, RESEARCH_TASKS

class Comparer:
    def reply(self, topic, messages=None):
        """
        检索相关主题的不同观点并进行比较。

        参数:
        text(str): 待比较的主题。
        messages(List[Dict[str, str]]): 对话历史（可选）
        返回:
        str: 对相关主题观点的详细比较。
        """
        system_prompt = RESEARCH_TASKS["viewpoint_comparison"]["system_prompt"]
        comparison = call_llm(topic, prompt=system_prompt, messages=messages)
        return comparison