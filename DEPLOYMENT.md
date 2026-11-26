# Deployment Information

## Trạng thái

Agent Part 6 đã deploy public trên Render và đã xác minh endpoint từ môi trường ngoài local.

## Local test

    cd 06-lab-complete
    docker compose up --build

    curl http://localhost:8000/health
    curl http://localhost:8000/ready
    curl -X POST http://localhost:8000/ask -H "X-API-Key: local-dev-key" -H "Content-Type: application/json" -d "{\"question\":\"What is deployment?\"}"

Expected status: /health 200, /ready 200, /ask có key 200, không có key 401.

## Deployment configuration

- Railway config: 06-lab-complete/railway.toml
- Required variables: AGENT_API_KEY, REDIS_URL, RATE_LIMIT_PER_MINUTE, DAILY_BUDGET_USD, ENVIRONMENT
- Không commit .env hoặc secret thật.

## Public URL

- Base URL: https://day14-agent-api.onrender.com
- Health: https://day14-agent-api.onrender.com/health → HTTP 200, `{"status":"ok"}`
- Readiness: https://day14-agent-api.onrender.com/ready → HTTP 200, `{"status":"ready"}`

Render cần được cấu hình các biến `AGENT_API_KEY`, `REDIS_URL`, `RATE_LIMIT_PER_MINUTE`, `DAILY_BUDGET_USD` và `ENVIRONMENT` trong dashboard; không đưa secret vào Git.

