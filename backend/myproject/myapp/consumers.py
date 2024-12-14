import json
from channels.generic.websocket import WebsocketConsumer
from .swarm import get_bilibili_comments
from .prompt import CommentAnalyzer


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analyzer = CommentAnalyzer()

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
        sections = result.split('\n')
        formatted_sections = []
        
        for section in sections:
            if section.strip():
                if section.startswith(('1.', '2.', '3.', '4.')):
                    formatted_sections.append(f'<strong>{section}</strong>')
                else:
                    formatted_sections.append(section)
        
        return '<br>'.join(formatted_sections)

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", "")

            if message.startswith("BV"):
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
                        text_data=json.dumps(
                            {
                                "message": "正在分析全部评论，请稍候..."
                            }
                        )
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

                except Exception as e:
                    self.send(
                        text_data=json.dumps({"message": f"处理评论时出错：{str(e)}"})
                    )
            else:
                self.send(
                    text_data=json.dumps(
                        {"message": "请输入正确的BVID格式（以BV开头）"}
                    )
                )

        except json.JSONDecodeError:
            self.send(text_data=json.dumps({"message": "无效的消息格式"}))
