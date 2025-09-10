from utils.helpers import call_llm

class OutlineGenerator:
    def generate_outline(self, topic):
        """
        根据主题生成详细的提纲
        
        参数:
        topic (str): 需要生成提纲的主题
        
        返回:
        str: 结构化提纲
        """
        prompt = f"""为以下主题创建一个详细的内容提纲：{topic}
        提纲应该包括：
        1. 引言部分
        2. 主要章节和子章节
        3. 每个章节的关键点
        4. 结论部分
        请使用清晰的层次结构表示。"""
        
        outline = call_llm(prompt)
        return outline