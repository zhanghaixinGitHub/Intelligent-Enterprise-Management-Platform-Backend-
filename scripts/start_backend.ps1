$ErrorActionPreference = "Stop"

Write-Output "BackendStarter.start >>> 切换到项目目录"
Set-Location "d:\pyCharmProjects\workSpace03"

Write-Output "BackendStarter.start >>> 激活 conda 环境并启动 uvicorn"
conda run -n ai_enterprise uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
