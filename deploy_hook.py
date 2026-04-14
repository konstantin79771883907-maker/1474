#!/usr/bin/env python3
"""
GitHub Webhook Deploy Hook
Принимает вебхуки от GitHub и автоматически обновляет код + перезапускает приложение
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import hashlib
import hmac
import os
import signal

app = FastAPI(title="Deploy Hook")

# Секретный ключ для проверки вебхуков (должен совпадать с настройками GitHub)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key-change-in-production")

# Путь к репозиторию
REPO_PATH = os.getenv("REPO_PATH", "/workspace")

# Имя сервиса systemd для перезапуска
SERVICE_NAME = os.getenv("SERVICE_NAME", "school-crm")


def verify_signature(payload_body, signature_header, secret):
    """Проверка подписи вебхука GitHub"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)


@app.post("/deploy-hook")
async def deploy_hook(request: Request):
    """Эндпоинт для получения вебхуков от GitHub"""
    
    # Получаем подпись
    signature = request.headers.get("X-Hub-Signature-256")
    
    # Получаем тело запроса
    body = await request.body()
    
    # Проверяем подпись (в production обязательно включите!)
    # if not verify_signature(body, signature, WEBHOOK_SECRET):
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Получаем тип события
    event = request.headers.get("X-GitHub-Event")
    
    if event != "push":
        return JSONResponse({"message": "Ignored non-push event"})
    
    try:
        # Выполняем git pull
        result = subprocess.run(
            ["git", "-C", REPO_PATH, "pull", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"Git pull failed: {result.stderr}")
        
        # Устанавливаем зависимости
        result = subprocess.run(
            ["pip", "install", "-r", f"{REPO_PATH}/requirements.txt"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"Pip install failed: {result.stderr}")
        
        # Перезапускаем сервис (если используется systemd)
        try:
            subprocess.run(
                ["systemctl", "restart", SERVICE_NAME],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            # Если systemd недоступен, пробуем альтернативные методы
            print(f"Systemd restart failed: {e}")
            # Можно добавить перезапуск через supervisor или другой процесс-менеджер
        
        return JSONResponse({
            "message": "Deployment successful",
            "git_output": result.stdout,
            "pip_output": result.stdout
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Проверка работоспособности хука"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
