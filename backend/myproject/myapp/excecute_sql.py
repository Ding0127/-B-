import sqlite3
import os
from pathlib import Path


class SQLExecutor:
    def __init__(self):
        # 获取当前文件所在目录的父目录（即 backend/myproject）
        current_dir = Path(__file__).parent.parent
        # 构建到 data/db_comment 目录的路径
        self.db_base_path = current_dir / "data" / "db_comment"
        # 确保目录存在
        self.db_base_path.mkdir(parents=True, exist_ok=True)
        print(f"Database path: {self.db_base_path}")  # 添加调试输出

    def execute_query(self, bvid: str, sql_query: str) -> list:
        """
        执行SQL查询并返回结果

        Args:
            bvid (str): 视频的BVID，用于定位具体的数据库文件
            sql_query (str): 要执行的SQL查询语句

        Returns:
            list: 查询结果列表，每个元素是一个字典，包含查询结果的字段和值
        """
        try:
            # 构建数据库文件的完整路径
            db_path = self.db_base_path / f"{bvid}.db"
            print(f"Trying to access database at: {db_path}")  # 添加调试输出
            print(f"Database exists: {db_path.exists()}")  # 检查文件是否存在

            # 确保数据库文件存在
            if not db_path.exists():
                raise FileNotFoundError(f"数据库文件不存在: {db_path}")

            # 连接数据库
            with sqlite3.connect(str(db_path)) as conn:
                # 设置行工厂以返回字典格式的结果
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 执行查询
                cursor.execute(sql_query)

                # 获取列名
                columns = [description[0] for description in cursor.description]

                # 获取结果并转换为字典列表
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    result_dict = {columns[i]: row[i] for i in range(len(columns))}
                    results.append(result_dict)

                return results

        except sqlite3.Error as e:
            raise Exception(f"数据库查询错误: {str(e)}")
        except Exception as e:
            raise Exception(f"执行查询时发生错误: {str(e)}")


# def main():
#     """
#     主函数，用于测试 SQLExecutor 类的功能
#     """
#     # 创建 SQLExecutor 实例
#     sql_executor = SQLExecutor()

#     # 测试用的 BVID（这里需要替换为实际存在的 BVID）
#     test_bvid = "BV1FU4y1T7Qf"

#     # 测试用的 SQL 查询语句
#     test_queries = [
#         "SELECT * FROM vedio_comments LIMIT 5",  # 获取前5条评论
#         # "SELECT count(*) as comment_count FROM comments",  # 获取评论总数
#         # "SELECT user_name, comment_text FROM comments WHERE likes > 100"  # 获取点赞数超过100的评论
#     ]

#     # 执行测试查询
#     try:
#         for query in test_queries:
#             print(f"\n执行查询: {query}")
#             try:
#                 results = sql_executor.execute_query(test_bvid, query)
#                 print(f"查询结果:")
#                 for result in results:
#                     print(result)
#             except Exception as e:
#                 print(f"查询执行失败: {str(e)}")

#     except Exception as e:
#         print(f"测试过程中发生错误: {str(e)}")


# if __name__ == "__main__":
#     main()
