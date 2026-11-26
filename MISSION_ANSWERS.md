# Day 14 Lab — Mission Answers

## Part 1 — Localhost vs Production

Các anti-pattern trong bản develop:

1. Cấu hình/secret phụ thuộc máy local.
2. Không có health/readiness probe chuẩn.
3. State trong memory không phù hợp khi scale.
4. Không có graceful shutdown khi nhận SIGTERM.
5. Không có structured logging và metric.

Production cần environment config, bind 0.0.0.0, health/readiness, JSON logs, state ngoài process và graceful shutdown.

## Part 2 — Docker

- Final image Part 6: 238 MB, đo bằng check_production_ready.py.
- Dockerfile dùng multi-stage python:3.11-slim, user non-root và HEALTHCHECK.
- Compose gồm agent + Redis, REDIS_URL trỏ tới redis service.
- Dependencies được cài trước khi copy source để tận dụng layer cache.

## Part 3 — Cloud Deployment

Đã deploy Render: https://day14-agent-api.onrender.com

- `/health` → HTTP 200, `{"status":"ok"}`
- `/ready` → HTTP 200, `{"status":"ready"}`
- Railway config vẫn được giữ tại `06-lab-complete/railway.toml` làm phương án triển khai thay thế.

Cloud Run pipeline: test, build image, push registry, deploy Cloud Run. service.yaml mô tả autoscaling, resources, secrets và health probes.

Railway deploy trực tiếp từ Dockerfile; Render Blueprint khai báo web service và Redis. Secret/REDIS_URL phải đặt trên platform.

## Part 4 — API Security

Kết quả local Part 6:

- Thiếu/sai X-API-Key: HTTP 401.
- Key đúng: HTTP 200.
- Vượt rate limit: HTTP 429, có Retry-After.
- Vượt budget: HTTP 402.

Rate limit và cost lưu trong Redis để dùng chung giữa worker/instance và tồn tại sau restart.

## Part 5 — Scaling & Reliability

- /health là liveness, độc lập với Redis.
- /ready kiểm tra Redis, Redis lỗi trả 503.
- State nằm trong Redis thay vì RAM.
- Nginx phân phối request tới nhiều instance.
- Graceful shutdown dùng FastAPI lifespan/Uvicorn; kiểm tra SIGTERM native cần WSL2.

## Part 6 — Final Project

Docker checker chạy đầy đủ trong WSL2 đạt **12/12 tiêu chí, 41/41 checks passed**. Docker image 238 MB; Compose, endpoint, Redis state, graceful shutdown và Docker stop đều đã kiểm tra thành công.

## Part 7 — Benchmark & Observability

- Eval v1: 1/23.
- Eval v2: 23/23, không regression.
- Eval v2 fixed: quality gate PASS.
- Load reports đã tạo trong reports/.
- Production stack local đã chạy bằng Docker Compose với agent/nginx/Prometheus/Grafana/Jaeger/Locust.
- CSV scale 1/3 đã lưu trong `benchmark-results/` và `06-lab-complete/benchmark-observability/production/benchmark-results/`.
- Prometheus target agent `up`, Grafana health `ok`, alert cost firing, log agent có `trace_id`/`span_id`.
- Public URL Render đã hoạt động và được xác minh.
- Screenshots UI Grafana/Jaeger/Alerts vẫn chưa có trong workspace.

## AI log

- Dùng AI để đọc rubric và phân tích deliverables.
- Dùng AI để triển khai Part 6, sau đó tự chạy checker, Docker Compose và endpoint tests.
- Dùng AI để chạy benchmark/eval; số liệu lấy từ JSON do script sinh ra.

