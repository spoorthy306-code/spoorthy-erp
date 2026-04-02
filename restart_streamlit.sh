#!/bin/bash
pkill -f "streamlit run" 2>/dev/null
sleep 2

source /home/a_anil/spoorthy_complete/venv/bin/activate

nohup streamlit run /home/a_anil/spoorthy_complete/app.py \
  --server.port 8501 --server.headless true \
  > /tmp/streamlit.log 2>&1 &

sleep 7
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/healthz)
if [ "$STATUS" = "200" ]; then
  echo "✅ Spoorthy ERP running at http://localhost:8501  (PID=$!)"
else
  echo "❌ App failed to start — check /tmp/streamlit.log"
  tail -20 /tmp/streamlit.log
fi
