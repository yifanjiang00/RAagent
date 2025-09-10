from utils.helpers import call_llm

class Summarizer:
    def summarize_text(self, text):
        """
        使用LLM生成文本摘要
        
        参数:
        text (str): 需要摘要的文本
        
        返回:
        str: 文本摘要
        """
        if not text or len(text.strip()) < 50:
            return "文本过短，无法生成有意义的摘要。"
        
        prompt = f"""请为以下文本生成一个简洁的摘要：
        
        {text}
        
        要求：
        1. 提取关键信息
        2. 保持原意不变
        3. 长度控制在原文的200字左右
        4. 语言流畅自然"""
        
        summary = call_llm(prompt)
        return summary