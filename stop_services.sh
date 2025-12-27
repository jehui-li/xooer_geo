#!/bin/bash

# 停止 GEO Agent 服务脚本

echo "Stopping GEO Agent services..."

# 停止后端
if [ -f /tmp/geo_agent_backend.pid ]; then
    BACKEND_PID=$(cat /tmp/geo_agent_backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm /tmp/geo_agent_backend.pid
        echo "Backend stopped"
    else
        echo "Backend process not found"
        rm /tmp/geo_agent_backend.pid
    fi
else
    echo "Backend PID file not found"
fi

# 停止前端
if [ -f /tmp/geo_agent_frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/geo_agent_frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm /tmp/geo_agent_frontend.pid
        echo "Frontend stopped"
    else
        echo "Frontend process not found"
        rm /tmp/geo_agent_frontend.pid
    fi
else
    echo "Frontend PID file not found"
fi

echo "Done!"

