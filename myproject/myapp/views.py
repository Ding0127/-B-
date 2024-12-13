from django.shortcuts import render
from django.http import HttpResponse
import traceback

def chat_view(request):
    try:
        return render(request, 'chat.html')
    except Exception as e:
        error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_message)  # 在服务器控制台打印错误
        return HttpResponse(error_message, status=500)  # 在浏览器中显示错误

def test_view(request):
    return HttpResponse("Test view works!") 