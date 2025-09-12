from utils.helpers import call_llm, RESEARCH_TASKS

class Explainer:
    def reply(self, concept, messages=None):
        """
        详细解释特定的专业术语及其背景知识。
        
        参数:
        concept (str): 需要解释的专业术语。
        messages(List[Dict[str, str]]): 对话历史（可选）
        返回:
        str: 对该术语的详细解释和相关背景知识。
        """
        system_prompt = RESEARCH_TASKS["concept_explanation"]["system_prompt"]
        explanation = call_llm(concept, prompt=system_prompt, messages=messages)
        return explanation