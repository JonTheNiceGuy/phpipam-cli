.PHONY: test integration all docker-up docker-down docker-clean fresh

test:
	uv run pytest --cov --cov-report=term-missing -v

integration: docker-up
	uv run pytest -m integration -v

all: test integration

docker-up:
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@timeout 120 bash -c 'until docker compose exec -T phpipam-mariadb mariadb -u root -proot_password -e "SELECT 1" >/dev/null 2>&1; do sleep 2; done'
	@timeout 120 bash -c 'until curl -sf -o /dev/null http://localhost:8080; do sleep 2; done'
	@echo "Services ready."

docker-down:
	docker compose down

docker-clean:
	docker compose down -v

fresh: docker-clean integration
