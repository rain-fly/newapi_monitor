#!/bin/bash

cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3"
    exit 1
fi

python3 run.py start
