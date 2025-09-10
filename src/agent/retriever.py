from utils.helpers import call_llm

class Retriever:

    def reply(self, topic, messages=None):
        # This method will implement the logic to retrieve information from the web
        # based on the provided topic. For now, it will return a placeholder response.
        prompt = "你是一个专业的研究助手。请根据用户的研究主题，提供全面、准确的信息检索结果。包括关键概念、最新发展、相关理论和应用领域。使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"
        retriever = call_llm(topic, prompt=prompt)
        return retriever