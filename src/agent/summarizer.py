from utils.helpers import call_llm, RESEARCH_TASKS
class Summarizer:

    def reply(self, text, messages=None):
        """
        调用LLM总结text内容。

        参数:
        text(str): 待总结内容。
        messages(List[Dict[str, str]]): 对话历史（可选）
        返回:
        str: 对该内容的详细解释。
        """
        system_prompt = RESEARCH_TASKS["literature_summary"]["system_prompt"]
        summary = call_llm(text, prompt=system_prompt, messages=messages)
        return summary