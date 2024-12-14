from openai import OpenAI
import os
from backend.myproject.myapp.csv_loader import get_comments_by_bvid
from typing import List

class CommentAnalyzer:
    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
    def get_summary_prompt(self, comments: List[str]) -> str:
        """
        生成用于总结评论的prompt
        
        Args:
            comments: 评论列表
            
        Returns:
            str: 格式化后的prompt
        """
        # 将评论列表合并为字符串
        comments_text = "\n".join(comments)
        
        prompt_template = """请帮我总结以下评论的主要观点。请以简洁、客观的方式进行总结，
突出关键信息和共同主题。

评论内容：
{comments}

请按照以下格式进行总结：
1. 主要观点：
2. 情感倾向：（正面/负面/中性）
3. 关键词：
4. 简要总结：（100字以内）
"""
        return prompt_template.format(comments=comments_text)

    def analyze_comments(self, bvid: str) -> str:
        """
        分析指定视频的评论
        
        Args:
            bvid: 视频的BVID
            
        Returns:
            str: AI的分析结果
        """
        # 获取评论
        comments = get_comments_by_bvid(bvid)
        if not comments:
            return "没有找到评论数据"
        
        # 生成prompt
        prompt = self.get_summary_prompt(comments)
        
        try:
            # 调用API获取回复
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant specialized in analyzing comments.'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            # 返回AI的回复
            return completion.choices[0].message.content
            
        except Exception as e:
            return f"分析过程中发生错误: {str(e)}"

# def main():
#     """主函数用于测试"""
#     analyzer = CommentAnalyzer()
    
#     # 测试视频BVID
#     test_bvid = "BV1Zi4y1H7a7"
    
#     print(f"正在分析视频 {test_bvid} 的评论...")
#     result = analyzer.analyze_comments(test_bvid)
#     print("\n分析结果：")
#     print(result)

# if __name__ == "__main__":
#     main() 