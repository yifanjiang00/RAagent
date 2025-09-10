from utils.helpers import call_llm

class Explainer:
    def reply(self, concept, messages=None):
        """
        详细解释特定的专业术语及其背景知识。
        
        参数:
        concept (str): 需要解释的专业术语。
        
        返回:
        str: 对该术语的详细解释和相关背景知识。
        """
        prompt = "你是一个专业知识解释助手。请清晰、全面地解释用户询问的专业概念，包括定义、背景、相关理论、应用场景和实际例子。使用易于理解的语言。使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"
        explanation = call_llm(concept, prompt=prompt)
        return explanation