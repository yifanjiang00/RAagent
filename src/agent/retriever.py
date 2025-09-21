from utils.helpers import call_llm, RESEARCH_TASKS
import serpapi
import os
from typing import Dict, List, Any
import json


class Retriever:
    def __init__(self):
        # 从环境变量获取SerpAPI密钥
        self.serpapi_key = os.getenv("SERP_API_KEY")
        if not self.serpapi_key:
            print("警告: SERP_API_KEY 环境变量未设置，Google Scholar搜索功能将不可用")

    def search_google_scholar(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        使用SerpAPI搜索Google Scholar
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        if not self.serpapi_key:
            return []
            
        try:
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": self.serpapi_key,
                "num": str(num_results),
            }
            
            search = serpapi.search(params)
            results = search.as_dict()
            
            # 提取有机搜索结果
            organic_results = results.get("organic_results", [])
            return organic_results
            
        except Exception as e:
            print(f"Google Scholar搜索错误: {e}")
            return []
    
    def format_scholar_results(self, results: List[Dict[str, Any]]) -> str:
        """
        将Google Scholar搜索结果格式化为Markdown
        
        Args:
            results: 搜索结果列表
            
        Returns:
            str: 格式化的Markdown文本
        """
        if not results:
            return "未找到相关学术文献。"
        
        formatted_lines = ["## 📚 Google Scholar 学术搜索结果", ""]
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "无标题")
            link = result.get("link", "#")
            snippet = result.get("snippet", "无摘要")
            
            # 提取出版物信息
            publication_info = result.get("publication_info", {})
            summary = publication_info.get("summary", "无出版物信息") if publication_info else "无出版物信息"
            
            # 提取被引用次数
            inline_links = result.get("inline_links", {})
            cited_by = inline_links.get("cited_by", {})
            citation_count = cited_by.get("total", "0") if cited_by else "0"
            
            # 提取年份
            year = "年份未知"
            if summary and "20" in summary:
                # 尝试从摘要中提取年份
                import re
                year_match = re.search(r'20\d{2}', summary)
                if year_match:
                    year = year_match.group(0)
            
            formatted_lines.append(f"{i}. **{title}**")
            formatted_lines.append(f"   - **链接**: [{link}]({link})")
            formatted_lines.append(f"   - **年份**: {year}")
            formatted_lines.append(f"   - **被引量**: {citation_count}")
            formatted_lines.append(f"   - **出版物**: {summary}")
            formatted_lines.append(f"   - **摘要**: {snippet}")
            formatted_lines.append("")
        
        # 添加搜索统计信息（如果有）
        search_info = results[0].get("search_parameters", {}) if results else {}
        if search_info and "engine" in search_info:
            formatted_lines.append(f"*搜索参数: {search_info.get('engine', '未知')} - {search_info.get('q', '未知查询')}*")
        
        return "\n".join(formatted_lines)
    
    def extract_keywords(self, query: str, messages=None) -> str:
        """
        使用LLM从用户查询中提取搜索关键词
        
        Args:
            query: 用户查询
            messages: 对话历史
            
        Returns:
            str: 提取的关键词
        """
        prompt = """你是一个学术研究助手。请从用户的查询中提取最适合在Google Scholar中搜索的关键词。
        请只返回关键词，不要返回其他解释或说明。
        
        示例:
        用户输入: "我想了解深度学习在医疗影像分析中的应用"
        输出: "深度学习 医疗影像分析"
        
        用户输入: "机器学习的最新发展趋势是什么"
        输出: "机器学习 发展趋势"
        
        用户输入: "请帮我找一些关于自然语言处理的文献"
        输出: "自然语言处理"
        """
        
        try:
            keywords = call_llm(query, prompt=prompt, messages=messages)
            return keywords.strip()
        except Exception as e:
            print(f"关键词提取错误: {e}")
            # 如果LLM提取失败，回退到使用原始查询
            return query

    def reply(self, topic, messages=None):
        """
        从网络检索相关内容，包括Google Scholar搜索结果和LLM生成的内容。

        参数:
        topic (str): 需要检索的主题。
        messages(List[Dict[str, str]]): 对话历史（可选）

        返回:
        str: 关于该主题的网络内容，包括Google Scholar搜索结果和LLM分析。
        """
        # 1. 提取搜索关键词
        search_keywords = self.extract_keywords(topic, messages)
        print(f"提取的搜索关键词: {search_keywords}")
        
        # 2. 搜索Google Scholar
        scholar_results = self.search_google_scholar(search_keywords)
        scholar_formatted = self.format_scholar_results(scholar_results)
        
        # 3. 使用LLM生成分析内容
        system_prompt = RESEARCH_TASKS["information_retrieval"]["system_prompt"]
        
        # 构建LLM查询，包含Google Scholar搜索结果
        llm_query = f"""
        用户的研究查询是："{topic}"

        我已经从Google Scholar获取了一些相关的学术文献，结果如下：
        {scholar_formatted}

        请你作为专业的研究助手：
        1. 综合分析上述搜索结果的核心观点和发现。
        2. 提炼出与该主题最相关的关键概念、理论和方法。
        3. 指出这些研究中的趋势、共识或争议。
        4. 如果搜索结果不足或不相关，请基于你的知识补充相关信息。
        5. 使用Markdown格式组织内容，确保结构清晰。
        """
        
        # 调用LLM进行总结分析
        llm_analysis = call_llm(llm_query, prompt=system_prompt, messages=messages)
        
        # 4. 组合搜索结果和LLM分析
        if scholar_results:
            final_response = f"{scholar_formatted}\n\n## 🤖 AI综合分析\n{llm_analysis}"
        else:
            final_response = f"## ⚠️ 注意: 无法访问Google Scholar\n{llm_analysis}"
        
        return final_response