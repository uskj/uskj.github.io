#!/bin/bash
# 漫庐AI直播 - 7x24小时自动运行脚本

WORKDIR="/mnt/d/Projects/.opencode"
LOG_DIR="$WORKDIR/logs"
PID_FILE="$WORKDIR/manlu-live.pid"
PYTHON="/tmp/crawl4ai-env/bin/python"

mkdir -p "$LOG_DIR"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        echo "直播已在运行 (PID: $PID)"
        exit 0
    fi
fi

# 启动直播
echo "启动漫庐AI直播..."
cd $WORKDIR
nohup $PYTHON manlu-live-kling.py stream > "$LOG_DIR/stream.log" 2>&1 &
echo $! > $PID_FILE
echo "直播已启动 (PID: $(cat $PID_FILE))"
echo "日志: $LOG_DIR/stream.log"

# 创建监控脚本
cat > /tmp/manlu-monitor.sh << 'EOF'
#!/bin/bash
while true; do
    if [ -f "$PID_FILE" ] && ps -p $(cat $PID_FILE) > /dev/null 2>&1; then
        echo "[$(date)] 直播运行中..." >> "$LOG_DIR/monitor.log"
    else
        echo "[$(date)] 直播已停止，尝试重启..." >> "$LOG_DIR/monitor.log"
        bash "$WORKDIR/start-stream.sh"
    fi
    sleep 300  # 每5分钟检查一次
done
EOF
chmod +x /tmp/manlu-monitor.sh

# 启动监控
nohup /tmp/manlu-monitor.sh >> "$LOG_DIR/monitor.log" 2>&1 &
echo "监控已启动"