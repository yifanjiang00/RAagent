from utils.helpers import call_llm
class Summarizer:

    def reply(self, text, messages=None):
        # 这里可以使用自然语言处理库（如nltk或spaCy）来提取摘要
        # 目前返回文本的前几句话作为示例摘要
        prompt = "你是一个专业的学术研究助手。请对用户提供的文献内容进行摘要和分析，提炼关键观点、研究方法和结论。使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"
        summarizer = call_llm(text, prompt=prompt)
        return summarizer