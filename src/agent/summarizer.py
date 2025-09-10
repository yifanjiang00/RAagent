class Summarizer:
    def reply(self, text, messages=None):
        # 这里可以使用自然语言处理库（如nltk或spaCy）来提取摘要
        # 目前返回文本的前几句话作为示例摘要
        sentences = text.split('. ')
        summary = '. '.join(sentences[:2]) + '.' if sentences else ''
        return summary