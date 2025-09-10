from utils.helpers import call_llm

class Comparer:
    def reply(self, topic, messages=None):
        # This method will retrieve different viewpoints on the given topic
        # and compare them for the user.
        prompt = "你是一个专业的分析助手。请对用户提供的不同观点或理论进行全面的对比分析，包括各自的优点、缺点、适用场景和学术支持。提供平衡、客观的分析。使用Markdown格式组织内容，包括标题、列表、代码块等。确保信息结构清晰，分点说明。"
        explanation = call_llm(topic, prompt=prompt)
        return explanation