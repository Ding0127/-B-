import time
import requests
import csv
import os
import sqlite3
from fake_useragent import UserAgent

# 创建保存CSV和DB的目录
CSV_DIR = os.path.join("data", "csv_comment")
DB_DIR = os.path.join("data", "db_comment")
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)


def save_to_db(comments_data, oid):
    db_path = os.path.join(DB_DIR, f"{oid}.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建评论表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            message TEXT,
            created_time TEXT,
            likes INTEGER,
            location TEXT
        )
    """
    )

    # 插入数据
    for comment in comments_data:
        cursor.execute(
            """
            INSERT INTO comments (video_id, message, created_time, likes, location)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                oid,
                comment["message"],
                comment["created_time"],
                comment["likes"],
                comment["location"],
            ),
        )

    conn.commit()
    conn.close()


def get_bilibili_comments(cookie, oid):
    url_template = "https://api.bilibili.com/x/v2/reply/main?csrf=40a227fcf12c380d7d3c81af2cd8c5e8&mode=3&next={}&oid={}&plat=1&type=1"
    headers = {"user-agent": UserAgent().random, "cookie": cookie}

    comments_data = []
    pre_comment_length = 0
    page_index = 0

    while True:
        try:
            response = requests.get(
                url=url_template.format(page_index, oid), headers=headers
            )
            response.raise_for_status()
            data = response.json().get("data")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}, retrying in 1 second...")
            time.sleep(1)
            continue

        page_index += 1

        if data and "replies" in data:
            for content in data["replies"]:
                comment_info = {
                    "message": content["content"]["message"],
                    "created_time": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(content["ctime"])
                    ),
                    "likes": content["like"],
                    "location": content.get("reply_control", {}).get(
                        "location", "Unknown"
                    ),
                }
                comments_data.append(comment_info)
            print(f"Collected {len(comments_data)} comments")
        else:
            print("No replies found or 'data' key is missing.")

        if len(comments_data) == pre_comment_length:
            print("No new comments. Exiting scraper.")
            break
        else:
            pre_comment_length = len(comments_data)

    # 保存CSV
    csv_path = os.path.join(CSV_DIR, f"{oid}.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["created_time", "message", "likes", "location"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for comment in comments_data:
            writer.writerow(comment)

    # 保存到数据库
    save_to_db(comments_data, oid)

    return comments_data


# # Example usage:
# cookie = "enable_web_push=DISABLE; header_theme_version=CLOSE; is-2022-channel=1; buvid3=7C8D00BD-F73C-846A-4D78-2BA2F472259445216infoc; b_nut=1713752545; _uuid=102284522-E3104-10928-4D59-CD33A96EC810448495infoc; hit-dyn-v2=1; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW3; rpdid=|(k)lYJ~kRR~0J'u~kuJlYY)m; CURRENT_BLACKGAP=0; LIVE_BUVID=AUTO3717250241708352; buvid_fp_plain=undefined; __utma=136533283.745392879.1728024702.1728024702.1728024702.1; __utmz=136533283.1728024702.1.1.utmcsr=search.bilibili.com|utmccn=(referral)|utmcmd=referral|utmcct=/all; buvid4=C9E55B11-589E-5B7B-D8CF-0A382D7C7DC687268-024071902-fkcMIqgd70Q%2F%2BoZ3vc%2FLGg%3D%3D; fingerprint=c085db1c4580e22c851f6edd43c060c5; buvid_fp=c085db1c4580e22c851f6edd43c060c5; home_feed_column=5; PVID=1; browser_resolution=2304-1054; CURRENT_QUALITY=80; bp_t_offset_288901500=1009922003005603840; SESSDATA=05a5c51f%2C1749531754%2C6c392%2Ac2CjAGqZuYAAqBzIQYyxZlSHhxwNugxe2WMdoPp0YphIX0o0g2fSn7au39FJyPEaK9JEsSVkNlUDZpYW9sREw4T0g5ZVF2UTgxbDY0VV9leENOUXNobFVXbzlqaWtXX2ptUUNaVmhCbVNQQzVSSDJ0LVFxMDYxaURWODNzNWhiYlYxdGJKRlZuQ1l3IIEC; bili_jct=a9feb1ea218891d383fe4d362556b4c2; DedeUserID=687133764; DedeUserID__ckMd5=a8095970da14562f; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQzMTY1MzEsImlhdCI6MTczNDA1NzI3MSwicGx0IjotMX0.Osx9A0gH1WJZpFLlYlOvT2fDxoqdiMgrFbrfVaZYADc; bili_ticket_expires=1734316471; bp_t_offset_687133764=1010352736685785088; sid=701shhgc; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; b_lsid=94E57F510_193C2B7E1BC; CURRENT_FNVAL=2000"
# oid = "BV1Zi4y1H7a7"
# comments = get_bilibili_comments(cookie, oid)
