import pandas as pd
import os
from pathlib import Path

def load_comments_from_csv(csv_path):
    """
    从CSV文件中读取评论数据
    
    Args:
        csv_path (str): CSV文件的路径
        
    Returns:
        list: 评论消息列表
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        # 获取message列的所有内容，转换为列表
        comments = df['message'].tolist()
        return comments
    except Exception as e:
        print(f"读取文件 {csv_path} 时发生错误: {str(e)}")
        return []

def get_comments_by_bvid(bvid, directory_path="data/csv_comment"):
    """
    根据BVID获取对应视频的所有评论
    
    Args:
        bvid (str): 视频的BVID，如 'BV1Zi4y1H7a7'
        directory_path (str): CSV文件所在的目录路径
        
    Returns:
        list: 评论列表，如果找不到文件则返回空列表
    """
    # 确保BVID格式正确
    bvid = bvid.strip().upper()
    if not bvid.startswith('BV'):
        print("无效的BVID格式")
        return []
    
    # 构建文件路径
    file_path = Path(directory_path) / f"{bvid}.csv"
    
    # 检查文件是否存在
    if not file_path.exists():
        print(f"找不到BVID为 {bvid} 的评论文件")
        return []
    
    return load_comments_from_csv(file_path)

def get_all_comments_from_directory(directory_path="data/csv_comment"):
    """
    从指定目录读取所有CSV文件中的评论
    
    Args:
        directory_path (str): CSV文件所在的目录路径
        
    Returns:
        dict: 以文件名为键，评论列表为值的字典
    """
    comments_dict = {}
    directory = Path(directory_path)
    
    # 确保目录存在
    if not directory.exists():
        print(f"目录 {directory_path} 不存在")
        return comments_dict
    
    # 遍历目录中的所有CSV文件
    for csv_file in directory.glob("*.csv"):
        file_name = csv_file.stem  # 获取文件名（不含扩展名）
        comments = load_comments_from_csv(csv_file)
        comments_dict[file_name] = comments
    
    return comments_dict

# 使用示例
if __name__ == "__main__":
    # 测试根据BVID获取评论
    bvid = "BV1Zi4y1H7a7"
    comments = get_comments_by_bvid(bvid)
    
    if comments:
        print(f"视频 {bvid} 包含 {len(comments)} 条评论")
        print("前3条评论示例：")
        for comment in comments[:3]:
            print(f"- {comment}")
    
    # print("\n获取所有视频的评论：")
    # # 获取所有评论
    # all_comments = get_all_comments_from_directory()
    
    # # 打印每个文件的评论数量
    # for file_name, comments in all_comments.items():
    #     print(f"文件 {file_name} 包含 {len(comments)} 条评论")
    #     # 打印前3条评论作为示例
    #     for comment in comments[:3]:
    #         print(f"- {comment}")
    #     print() 