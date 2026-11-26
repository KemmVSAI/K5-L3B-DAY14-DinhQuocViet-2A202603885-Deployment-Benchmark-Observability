# Deployment Information

## Trạng thái

Agent Part 6 đã chạy local bằng Docker Compose nhưng chưa deploy public lên Railway/Render.

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

Chưa có. Cần deploy Railway hoặc Render, tạo Redis và cập nhật URL thật trước khi nộp.

