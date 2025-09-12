from utils.helpers import call_llm, RESEARCH_TASKS
class Summarizer:

    def reply(self, text, messages=None):
        # 这里可以使用自然语言处理库（如nltk或spaCy）来提取摘要
        # 目前返回文本的前几句话作为示例摘要
        system_prompt = RESEARCH_TASKS["literature_summary"]["system_prompt"]
        summary = call_llm(text, prompt=system_prompt, messages=messages)
        return summary