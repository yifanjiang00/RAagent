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
        prompt = "请详细解释以下专业术语，并补充相关背景知识："
        explanation = call_llm(concept, prompt=prompt)
        return explanation