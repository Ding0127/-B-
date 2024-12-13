#!/bin/bash
# 启动后端
cd backend && daphne -b 0.0.0.0 -p 8002 myproject.asgi:application & 
# 启动前端
cd frontend && python -m http.server 8000 &
echo "服务已启动:"
echo "前端: http://localhost:8000"
echo "后端: http://localhost:8002" 