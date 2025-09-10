from utils.helpers import call_llm


class OutlineGenerator:
    def reply(self, topic,messages=None):
        """
        根据主题生成详细的提纲

        参数:
        topic (str): 需要生成提纲的主题

        返回:
        str: 结构化提纲
        """
        prompt = "你是一个专业的学术写作助手。请根据用户的研究主题，生成一个结构合理、内容全面的论文或报告大纲。包括引言、文献综述、方法论、结果分析、结论等部分。使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"


        outline = call_llm(topic, prompt=prompt)
        return outline