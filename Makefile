.PHONY: up

all: up

up:
	@echo "Создание и запуск контейнеров..."
	docker-compose up -d
	@echo "✨ Twitter Clone запущен! ✨"
	@echo "Перейдите по адресу http://localhost:5000/"
