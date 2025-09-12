from utils.helpers import call_llm, RESEARCH_TASKS

class Retriever:
    def reply(self, topic, messages=None):
        """
        从网络检索相关内容。

        参数:
        topic (str): 需要检索的主题。
        messages(List[Dict[str, str]]): 对话历史（可选）

        返回:
        str: 关于该主题的网络内容。
        """
        system_prompt = RESEARCH_TASKS["information_retrieval"]["system_prompt"]
        retriever = call_llm(topic, prompt=system_prompt, messages=messages)
        return retriever