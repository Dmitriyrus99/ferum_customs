# Используем официальный образ Frappe, чтобы не устанавливать все вручную
FROM frappe/erpnext-worker:v15.12.1

# Переключаемся на пользователя root для установки дополнительных пакетов
USER root

# Устанавливаем утилиты, которые могут понадобиться для разработки
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Переключаемся обратно на пользователя frappe
USER frappe

# Устанавливаем bench в домашнюю директорию пользователя
RUN pip3 install frappe-bench

# Добавляем bench в PATH, чтобы команды были доступны из любого места
ENV PATH="/home/frappe/.local/bin:${PATH}"

# Устанавливаем рабочую директорию
WORKDIR /workspace

# Копируем локальный код приложения в контейнер, чтобы bench мог его найти
COPY --chown=frappe:frappe . /workspace/ferum_customs

