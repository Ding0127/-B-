import json
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({
            'message': '连接成功！'
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            if not message.startswith('BV'):
                self.send(text_data=json.dumps({
                    'message': '即将执行sql查询'
                }))
            
            self.send(text_data=json.dumps({
                'message': f'服务器收到消息：{message}'
            }))
            
            self.send(text_data=json.dumps({
                'message': '下面是否要对评论进行进一步分析？'
            }))
            
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({
                'message': '无效的消息格式'
            })) 