from openai import OpenAI
import os


class SQLQueryGenerator:
    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def get_sql_prompt(self, bvid: str, user_question: str) -> str:
        """
        生成用于创建SQL查询的prompt

        Args:
            bvid: 视频的BVID
            user_question: 用户的问题

        Returns:
            str: 格式化后的prompt
        """
        prompt_template = """请根据用户的问题，生成对应的SQL查询语句。

数据库名称：{bvid}.db
数据库表结构如下：
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    message TEXT,
    created_time TEXT,
    likes INTEGER,
    location TEXT
)

用户问题：
{question}

要求：
1. 充分理解用户问题，并根据用户问题生成SQL查询语句
2. 生成标准的SQL查询语句
3. 必须返回所有字段 (id, video_id, message, created_time, likes, location)
4. 从 comments 表中查询(即 from comments)
5. 只返回SQL语句本身，不需要其他解释
6. 确保SQL语句以分号结尾
7. 涉及到字符匹配采用模糊匹配like

请生成SQL查询语句："""

        return prompt_template.format(bvid=bvid, question=user_question)

    def generate_sql_query(self, bvid: str, user_question: str) -> str:
        """
        根据用户问题生成SQL查询语句

        Args:
            bvid: 视频的BVID
            user_question: 用户的问题

        Returns:
            str: 生成的SQL查询语句
        """
        try:
            # 生成prompt
            prompt = self.get_sql_prompt(bvid, user_question)

            # 调用API获取回复
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Only return the SQL query without any explanation.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            # 获取并清理SQL查询语句
            sql_query = completion.choices[0].message.content.strip()

            # 确保SQL语句以分号结尾
            if not sql_query.endswith(";"):
                sql_query += ";"

            return sql_query

        except Exception as e:
            return f"生成SQL查询时发生错误: {str(e)}"


# # 测试代码
# def main():
#     generator = SQLQueryGenerator()
#     test_bvid = "BV1Zi4y1H7a7"

#     # 测试一些示例问题
#     test_questions = [
#         "找出点赞数最多的10条评论",
#         "统计每个地区的评论数量",
#         "查找包含'好看'关键词的评论",
#         "显示最近一周的所有评论",
#     ]

#     for question in test_questions:
#         print(f"\n问题: {question}")
#         sql = generator.generate_sql_query(test_bvid, question)
#         print(f"SQL查询: {sql}")


# if __name__ == "__main__":
#     main()
