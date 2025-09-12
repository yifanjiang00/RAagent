from utils.helpers import call_llm, RESEARCH_TASKS

class OutlineGenerator:
    def reply(self, topic,messages=None):
        """
        根据主题生成详细的提纲

        参数:
        topic (str): 需要生成提纲的主题

        返回:
        str: 结构化提纲
        """
        system_prompt = RESEARCH_TASKS["outline_generation"]["system_prompt"]
        outline = call_llm(topic, prompt=system_prompt, messages=messages)
        return outline