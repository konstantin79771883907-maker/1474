# 🚀 Инструкция по развертыванию School Support CRM на сервере

## 1. Подготовка сервера

### Требования:
- Ubuntu/Debian сервер с root доступом
- Python 3.8+
- Git
- Nginx (опционально, для production)

### Установка зависимостей:

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install -y python3 python3-pip python3-venv git nginx

# Установка uvicorn глобально
sudo pip3 install uvicorn
```

## 2. Клонирование репозитория

```bash
# Клонируем репозиторий
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/school-crm.git
cd school-crm

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

## 3. Настройка systemd сервисов

### Сервис основного приложения:

```bash
# Копируем файл сервиса
sudo cp school-crm.service /etc/systemd/system/

# Редактируем при необходимости (путь, пользователь)
sudo nano /etc/systemd/system/school-crm.service

# Перезагружаем systemd и запускаем сервис
sudo systemctl daemon-reload
sudo systemctl enable school-crm
sudo systemctl start school-crm

# Проверяем статус
sudo systemctl status school-crm
```

### Сервис deploy hook:

```bash
# Генерируем секретный ключ
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo $WEBHOOK_SECRET

# Копируем файл сервиса
sudo cp school-crm-hook.service /etc/systemd/system/

# Редактируем файл, заменяя secret на сгенерированный
sudo nano /etc/systemd/system/school-crm-hook.service

# Перезагружаем systemd и запускаем сервис
sudo systemctl daemon-reload
sudo systemctl enable school-crm-hook
sudo systemctl start school-crm-hook

# Проверяем статус
sudo systemctl status school-crm-hook
```

## 4. Настройка Nginx

```bash
# Копируем конфигурацию
sudo cp nginx.conf.example /etc/nginx/sites-available/school-crm

# Редактируем конфигурацию (заменяем домен/IP)
sudo nano /etc/nginx/sites-available/school-crm

# Создаем симлинк
sudo ln -s /etc/nginx/sites-available/school-crm /etc/nginx/sites-enabled/

# Проверяем конфигурацию
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl restart nginx
```

## 5. Настройка вебхука GitHub

1. Откройте ваш репозиторий на GitHub
2. Перейдите в **Settings** → **Webhooks** → **Add webhook**
3. Заполните поля:
   - **Payload URL**: `http://YOUR_SERVER_IP/deploy-hook`
   - **Content type**: `application/json`
   - **Secret**: тот же, что указали в `school-crm-hook.service`
   - **Which events would you like to trigger?**: Just the push event
   - ✅ **Active**

4. Нажмите **Add webhook**

## 6. Проверка работы

### Проверка основного приложения:
```bash
curl http://localhost:8000
# или через браузер: http://YOUR_SERVER_IP/
```

### Проверка deploy hook:
```bash
curl http://localhost:8001/health
```

### Просмотр логов:
```bash
# Логи основного приложения
sudo journalctl -u school-crm -f

# Логи deploy hook
sudo journalctl -u school-crm-hook -f

# Логи Nginx
sudo tail -f /var/log/school-crm-access.log
sudo tail -f /var/log/school-crm-error.log
```

## 7. Автоматическое развертывание

Теперь при каждом push в ветку `main`:
1. GitHub отправляет вебхук на `/deploy-hook`
2. Скрипт выполняет `git pull`
3. Устанавливает новые зависимости (`pip install -r requirements.txt`)
4. Перезапускает сервис `school-crm`

**Изменения будут видны сразу после коммита!** 🎉

## 8. Безопасность (рекомендации)

### Для production обязательно:

1. **Настройте HTTPS**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

2. **Ограничьте доступ к deploy hook по IP**:
   - В nginx.conf раскомментируйте строки с `allow` и `deny`
   - Используйте актуальные IP адреса GitHub: https://api.github.com/meta

3. **Используйте сильного пользователя**:
   - Замените `www-data` на специального пользователя
   - Ограничьте права доступа к файлам

4. **Настройте firewall**:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 9. Управление сервисами

```bash
# Перезапуск основного приложения
sudo systemctl restart school-crm

# Перезапуск deploy hook
sudo systemctl restart school-crm-hook

# Остановка
sudo systemctl stop school-crm

# Автозагрузка при старте системы
sudo systemctl enable school-crm
sudo systemctl enable school-crm-hook
```

## 10. Troubleshooting

### Приложение не запускается:
```bash
# Проверка логов
sudo journalctl -u school-crm --no-pager -n 50

# Проверка порта
sudo netstat -tlnp | grep 8000
```

### Deploy hook не работает:
```bash
# Проверка логов
sudo journalctl -u school-crm-hook --no-pager -n 50

# Тест вручную
curl -X POST http://localhost:8001/deploy-hook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{}'
```

### Проблемы с Nginx:
```bash
# Проверка конфигурации
sudo nginx -t

# Перезапуск
sudo systemctl restart nginx

# Проверка логов
sudo tail -f /var/log/nginx/error.log
```

---

## Быстрый старт (one-liner для тестирования):

```bash
cd /workspace && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 &
```

Для production используйте systemd сервисы!
