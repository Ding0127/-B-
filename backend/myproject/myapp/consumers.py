import json
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({
            'message': '连接成功！欢迎使用B站评论聊天机器人'
        }))

    def disconnect(self, close_code):
        # 发送关闭确认消息
        try:
            self.send(text_data=json.dumps({
                'message': '连接已关闭'
            }))
        except:
            pass

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            # 这里可以添加处理BVID的逻辑
            if message.startswith('BV'):
                response_message = f'正在获取视频 {message} 的评论...'
            else:
                response_message = '请输入正确的BVID格式'

            self.send(text_data=json.dumps({
                'message': response_message
            }))
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({
                'message': '无效的消息格式'
            })) 