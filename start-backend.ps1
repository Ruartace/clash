# Clash 后端启动脚本
$env:USE_SQLITE='true'
$env:DEBUG='True'
$env:SECRET_KEY='django-insecure-clash-dev-secret-key-change-in-production'
$env:ALLOWED_HOSTS='localhost,127.0.0.1'
$env:CORS_ALLOWED_ORIGINS='http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175,http://localhost:5176,http://127.0.0.1:5176'

Write-Host '正在启动 Clash 后端...' -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot\Backend
D:\python3.10\python.exe manage.py runserver 127.0.0.1:8000
