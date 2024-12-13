@echo off
start cmd /k "cd backend && daphne -b 0.0.0.0 -p 8002 myproject.asgi:application"
start cmd /k "cd frontend && python -m http.server 8000"
echo 服务已启动:
echo 前端: http://localhost:8000
echo 后端: http://localhost:8002 