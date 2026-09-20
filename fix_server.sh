#!/bin/bash
echo "Подключаюсь к серверу 81.91.179.40..."
echo "Пожалуйста, введите пароль от сервера, когда попросит:"
ssh root@81.91.179.40 << 'SSH_EOF'
  echo "Успешно зашли на сервер!"
  # Поиск папки с проектом (может быть luneryagency или luneria-crm)
  if [ -d "/root/luneryagency" ]; then
    cd /root/luneryagency
  elif [ -d "/root/luneria-crm" ]; then
    cd /root/luneria-crm
  elif [ -d "/var/www/luneryagency" ]; then
    cd /var/www/luneryagency
  else
    # Попробуем найти папку
    PROJECT_DIR=$(find /root /var/www -name "backend" -type d 2>/dev/null | head -n 1)
    if [ -n "$PROJECT_DIR" ]; then
      cd $(dirname $PROJECT_DIR)
    else
      echo "Не могу найти папку с проектом на сервере!"
      exit 1
    fi
  fi
  
  echo "Найдена папка проекта: $(pwd)"
  
  # Восстановление базы из Google Sheets, если она пустая
  # Но на самом деле она не пустая (партнеры на месте), так что просто pull
  echo "Обновляю код из GitHub..."
  git pull origin main || git reset --hard origin/main
  
  echo "Перезапускаю бэкенд..."
  if systemctl list-units --type=service | grep -q "lunery"; then
    SERVICE_NAME=$(systemctl list-units --type=service | grep "lunery" | awk '{print $1}')
    systemctl restart $SERVICE_NAME
    echo "Перезапущен сервис $SERVICE_NAME"
  else
    # Если запущен через pm2
    if command -v pm2 &> /dev/null; then
      pm2 restart all
      echo "Перезапущены процессы pm2"
    else
      # Если запущен через nohup/screen, убиваем uvicorn
      pkill -f uvicorn
      cd backend
      source venv/bin/activate 2>/dev/null || true
      nohup uvicorn app.main:app --host 0.0.0.1 --port 8000 > backend.log 2>&1 &
      echo "Перезапущен uvicorn"
    fi
  fi
  echo "Всё готово! Бэкенд обновлен."
SSH_EOF
