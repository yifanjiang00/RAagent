from utils.helpers import call_llm

class IntentAnalyzer:
    def __init__(self):
        self.intent_prompt = """你是一个智能对话意图分析器。请分析用户输入的意图，并返回最匹配的类别。
        可选的类别有：
        - concept_explanation: 当用户询问概念解释、定义、含义时
        - viewpoint_comparison: 当用户要求对比、比较不同观点或事物时
        - outline_generation: 当用户要求生成大纲、提纲或结构时
        - literature_summary: 当用户要求摘要、总结文献内容时
        - information_retrieval: 当用户询问一般信息、资料检索时
        
        请只返回类别名称，不要返回其他内容。"""

    def analyze(self, query: str) -> str:
        """使用LLM分析用户查询意图"""
        try:
            # 使用LLM进行更精确的意图识别
            intent = call_llm(
                f"用户查询: {query}",
                prompt=self.intent_prompt,
                model="qwen-plus"  # 使用更强大的模型进行意图分析
            ).strip()
            
            # 确保返回的是有效的意图类别
            valid_intents = [
                "concept_explanation", 
                "viewpoint_comparison", 
                "outline_generation", 
                "literature_summary", 
                "information_retrieval"
            ]
            
            if intent in valid_intents:
                return intent
            else:
                # 如果LLM返回了无效类别，回退到基于关键词的方法
                return self._keyword_based_analysis(query)
                
        except Exception as e:
            print(f"意图分析出错: {e}")
            # 出错时回退到基于关键词的方法
            return self._keyword_based_analysis(query)
    
    def _keyword_based_analysis(self, query: str) -> str:
        """基于关键词的意图分析（备用方法）"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["解释", "什么是", "含义", "定义", "说明", "介绍"]):
            return "concept_explanation"
        elif any(word in query_lower for word in ["对比", "比较", "区别", "差异", "不同点", "vs", " versus"]):
            return "viewpoint_comparison"
        elif any(word in query_lower for word in ["大纲", "结构", "提纲", "框架", "目录", "章节"]):
            return "outline_generation"
        elif any(word in query_lower for word in ["摘要", "总结", "概括", "文献", "论文", "文章"]):
            return "literature_summary"
        else:
            return "information_retrieval"