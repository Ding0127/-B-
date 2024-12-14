import json
from channels.generic.websocket import WebsocketConsumer
from .swarm import get_bilibili_comments
from .prompt import CommentAnalyzer
from .sql_prompt import SQLQueryGenerator
from .excecute_sql import SQLExecutor
from .extract_prompt import CommentQA


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analyzer = CommentAnalyzer()
        self.sql_generator = SQLQueryGenerator()
        self.sql_executor = SQLExecutor()
        self.comment_qa = CommentQA()
        self.current_bvid = None

    def connect(self):
        self.accept()
        self.send(
            text_data=json.dumps({"message": "连接成功！欢迎使用B站评论聊天机器人"})
        )

    def disconnect(self, close_code):
        try:
            self.send(text_data=json.dumps({"message": "连接已关闭"}))
        except:
            pass

    def format_analysis_result(self, result):
        """格式化分析结果为HTML格式"""
        sections = result.split("\n")
        formatted_sections = []

        current_section = None

        for section in sections:
            if section.strip():
                # 处理主要标题（1. 2. 3. 4.开头的）
                if section.startswith(("1.", "2.", "3.", "4.")):
                    current_section = section.split(".")[0]
                    formatted_sections.append(
                        f'<br><strong style="color: #2c3e50; font-size: 16px;">{section}</strong><br>'
                    )
                # 处理支持证据中的小点（- 开头的）
                elif section.strip().startswith("-"):
                    bullet_content = section.strip()[1:].strip()  # 移除 '-' 并清理空格
                    formatted_sections.append(
                        f'<div style="margin-left: 20px; margin-top: 5px;">'
                        f"• {bullet_content}"
                        f"</div>"
                    )
                # 普通段落
                else:
                    style = ""
                    if current_section == "2":  # 详细分析部分使用缩进
                        style = 'style="margin-left: 15px; margin-top: 5px;"'
                    elif current_section == "4":  # 总结建议部分使用特殊样式
                        style = 'style="margin-left: 15px; margin-top: 5px; color: #34495e;"'
                    formatted_sections.append(f"<div {style}>{section}</div>")

        # 在各大部分之间添加额外的空行
        return "<br>".join(formatted_sections)

    def format_sql_results(self, results):
        """格式化 SQL 查询结果为 HTML 表格"""
        if not results:
            return "查询结果为空"

        # 获取表头（字段名）
        headers = results[0].keys()

        # 构建 HTML 表格
        html = ['<table border="1" style="border-collapse: collapse;">']

        # 添加表头
        html.append("<tr>")
        for header in headers:
            html.append(f'<th style="padding: 8px;">{header}</th>')
        html.append("</tr>")

        # 添加数据行
        for row in results:
            html.append("<tr>")
            for header in headers:
                html.append(f'<td style="padding: 8px;">{row[header]}</td>')
            html.append("</tr>")

        html.append("</table>")
        return "".join(html)

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", "")

            if message.startswith("BV"):
                self.current_bvid = message
                # 发送开始爬取的消息
                self.send(
                    text_data=json.dumps(
                        {"message": f"开始获取视频 {message} 的评论..."}
                    )
                )

                try:
                    # 这里使用你的cookie
                    cookie = "enable_web_push=DISABLE; header_theme_version=CLOSE; is-2022-channel=1; buvid3=7C8D00BD-F73C-846A-4D78-2BA2F472259445216infoc; b_nut=1713752545; _uuid=102284522-E3104-10928-4D59-CD33A96EC810448495infoc; hit-dyn-v2=1; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW3; rpdid=|(k)lYJ~kRR~0J'u~kuJlYY)m; CURRENT_BLACKGAP=0; LIVE_BUVID=AUTO3717250241708352; buvid_fp_plain=undefined; __utma=136533283.745392879.1728024702.1728024702.1728024702.1; __utmz=136533283.1728024702.1.1.utmcsr=search.bilibili.com|utmccn=(referral)|utmcmd=referral|utmcct=/all; buvid4=C9E55B11-589E-5B7B-D8CF-0A382D7C7DC687268-024071902-fkcMIqgd70Q%2F%2BoZ3vc%2FLGg%3D%3D; fingerprint=c085db1c4580e22c851f6edd43c060c5; buvid_fp=c085db1c4580e22c851f6edd43c060c5; home_feed_column=5; PVID=1; browser_resolution=2304-1054; CURRENT_QUALITY=80; bp_t_offset_288901500=1009922003005603840; SESSDATA=05a5c51f%2C1749531754%2C6c392%2Ac2CjAGqZuYAAqBzIQYyxZlSHhxwNugxe2WMdoPp0YphIX0o0g2fSn7au39FJyPEaK9JEsSVkNlUDZpYW9sREw4T0g5ZVF2UTgxbDY0VV9leENOUXNobFVXbzlqaWtXX2ptUUNaVmhCbVNQQzVSSDJ0LVFxMDYxaURWODNzNWhiYlYxdGJKRlZuQ1l3IIEC; bili_jct=a9feb1ea218891d383fe4d362556b4c2; DedeUserID=687133764; DedeUserID__ckMd5=a8095970da14562f; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQzMTY1MzEsImlhdCI6MTczNDA1NzI3MSwicGx0IjotMX0.Osx9A0gH1WJZpFLlYlOvT2fDxoqdiMgrFbrfVaZYADc; bili_ticket_expires=1734316471; bp_t_offset_687133764=1010352736685785088; sid=701shhgc; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; b_lsid=94E57F510_193C2B7E1BC; CURRENT_FNVAL=2000"

                    # 调用爬虫函数
                    comments = get_bilibili_comments(cookie, message)

                    # 发送获取完成的消息
                    self.send(
                        text_data=json.dumps(
                            {
                                "message": f"评论获取完成！共获取到 {len(comments)} 条评论！"
                            }
                        )
                    )

                    # 发送正在分析的提示
                    self.send(
                        text_data=json.dumps({"message": "正在分析全部评论，请稍候..."})
                    )

                    # 分析评论
                    analysis_result = self.analyzer.analyze_comments(message)
                    formatted_result = self.format_analysis_result(analysis_result)

                    # 发送分析结果
                    self.send(
                        text_data=json.dumps(
                            {
                                "message": f"<br><br><strong>评论分析结果：</strong><br>{formatted_result}"
                            }
                        )
                    )

                    # 添加询问下一步分析的消息
                    self.send(
                        text_data=json.dumps(
                            {"message": "是否要对评论进行下一步分析？请输入你的问题"}
                        )
                    )

                except Exception as e:
                    self.send(
                        text_data=json.dumps({"message": f"处理评论时出错：{str(e)}"})
                    )
            else:
                if self.current_bvid:
                    # 生成 SQL 查询
                    sql_query = self.sql_generator.generate_sql_query(
                        self.current_bvid, message
                    )

                    # 发送 SQL 查询消息
                    self.send(
                        text_data=json.dumps(
                            {
                                "message": f"即将执行以下SQL查询：<br><pre>{sql_query}</pre>"
                            }
                        )
                    )

                    try:
                        # 执行 SQL 查询
                        results = self.sql_executor.execute_query(
                            self.current_bvid, sql_query
                        )

                        # 格式化并发送结果
                        formatted_results = self.format_sql_results(results)
                        self.send(
                            text_data=json.dumps(
                                {"message": f"查询结果：<br>{formatted_results}"}
                            )
                        )

                        # 发送正在生成答案的提示
                        self.send(
                            text_data=json.dumps({"message": "正在生成答案，请稍候..."})
                        )

                        # 使用 CommentQA 生成答案
                        answer = self.comment_qa.answer_question(
                            self.current_bvid, message
                        )
                        formatted_answer = self.format_analysis_result(answer)
                        self.send(
                            text_data=json.dumps(
                                {"message": f"<br>问题分析：<br>{formatted_answer}"}
                            )
                        )

                        # 询问是否继续分析
                        self.send(
                            text_data=json.dumps(
                                {"message": "是否要继续分析？请输入你的问题"}
                            )
                        )

                    except Exception as e:
                        self.send(
                            text_data=json.dumps(
                                {"message": f"执行查询时发生错误：{str(e)}"}
                            )
                        )
                else:
                    self.send(
                        text_data=json.dumps({"message": "请先输入要分析的视频BVID"})
                    )

        except json.JSONDecodeError:
            self.send(text_data=json.dumps({"message": "无效的消息格式"}))
