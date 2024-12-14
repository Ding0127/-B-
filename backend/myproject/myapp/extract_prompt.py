from openai import OpenAI
import os
from .excecute_sql import SQLExecutor
from typing import List
from .sql_prompt import SQLQueryGenerator


class CommentQA:
    def __init__(self):
        """初始化 OpenAI 客户端、SQL 执行器和 SQL 生成器"""
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.sql_executor = SQLExecutor()
        self.sql_generator = SQLQueryGenerator()  # 添加 SQL 生成器

    def extract_messages(self, bvid: str, user_question: str) -> tuple[List[str], dict]:
        """
        从数据库中提取评论消息

        Args:
            bvid (str): 视频的BVID
            user_question (str): 用户问题

        Returns:
            tuple[List[str], dict]: 评论消息列表和SQL查询信息
        """
        try:
            # 使用 SQLQueryGenerator 生成 SQL 查询
            query = self.sql_generator.generate_sql_query(bvid, user_question)

            # 打印 SQL 查询语句
            print("\nSQL查询语句：")
            print("=" * 50)
            print(query)
            print("=" * 50)

            # 执行查询并获取结果
            results = self.sql_executor.execute_query(bvid, query)

            # 打印查询结果
            print("\nSQL查询结果：")
            print("=" * 50)
            for result in results:
                print(result)
            print("=" * 50)

            messages = [result["message"] for result in results if result["message"]]

            # 打印提取的消息
            print("\n提取的评论消息：")
            print("=" * 50)
            for msg in messages:
                print(f"- {msg}")
            print("=" * 50)

            # 收集SQL相关信息
            sql_info = {"query": query, "count": len(results)}

            return messages, sql_info
        except Exception as e:
            print(f"提取消息时发生错误: {str(e)}")
            return [], {"query": "", "count": 0}

    def generate_qa_prompt(
        self, user_question: str, messages: List[str], sql_info: dict
    ) -> str:
        """
        生成问答prompt

        Args:
            user_question (str): 用户问题
            messages (List[str]): 评论消息列表
            sql_info (dict): SQL查询相关信息

        Returns:
            str: 生成的prompt
        """
        comments_text = "\n".join(messages)

        prompt_template = """基于以下信息，请回答用户问题(以下评论内容是根据用户问题从数据库中提取的相关评论)。请提供详细且有见地的回答，并尽可能引用具体的评论内容作为支持。如果评论内容中没有相关信息，请回答没有找到相关信息。

SQL查询信息：
查询语句：{sql_query}

提取的评论内容：
{comments}

用户问题：{question}

请严格按照以下格式回答，每个部分请空一行：

1. 直接回答：
（简要回答用户问题）

2. 详细分析：
（基于评论的具体分析）

3. 支持证据：
- （引用相关评论1）
- （引用相关评论2）
- （引用相关评论3）

4. 总结建议：
（如果适用）
"""
        return prompt_template.format(
            sql_query=sql_info["query"],
            result_count=sql_info["count"],
            comments=comments_text,
            question=user_question,
        )

    def answer_question(self, bvid: str, user_question: str) -> str:
        """
        回答关于视频评论的问题

        Args:
            bvid (str): 视频的BVID
            user_question (str): 用户问题

        Returns:
            str: AI的回答
        """
        # 获取评论，传入用户问题以生成相应的 SQL 查询
        messages, sql_info = self.extract_messages(bvid, user_question)
        if not messages:
            return "没有找到评论数据"

        # 生成prompt
        prompt = self.generate_qa_prompt(user_question, messages, sql_info)

        # 添加打印语句
        print("\n发送给AI的prompt内容：")
        print("=" * 50)
        print(prompt)
        print("=" * 50)

        try:
            # 调用API获取回复
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant specialized in analyzing video comments and answering questions.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            # 返回AI的回复
            return completion.choices[0].message.content

        except Exception as e:
            return f"处理问题时发生错误: {str(e)}"


def main():
    """测试功能"""
    qa = CommentQA()

    # 测试BVID和问题
    test_bvid = "BV1FU4y1T7Qf"
    test_question = "这个视频的观众反应如何？主要评论了哪些方面？"

    print(f"正在分析视频 {test_bvid} 的评论...")
    print(f"问题: {test_question}")

    result = qa.answer_question(test_bvid, test_question)
    print("\n回答：")
    print(result)


if __name__ == "__main__":
    main()
