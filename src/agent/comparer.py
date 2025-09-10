from utils.helpers import call_llm

class Comparer:
    def compare_views(self, topic):
        """
        比较关于某个主题的不同观点
        
        参数:
        topic (str): 需要比较的主题
        
        返回:
        str: 不同观点的比较分析
        """
        prompt = f"""请比较关于"{topic}"的不同观点或学派。
        请列出至少两种不同的观点，分析它们的异同点，
        并尽可能提供支持每种观点的理由和证据。"""
        
        comparison = call_llm(prompt)
        return comparison