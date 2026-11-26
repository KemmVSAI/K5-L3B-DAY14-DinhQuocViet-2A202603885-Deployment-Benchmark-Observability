# Benchmark & Observability Report — Day 14

Họ tên: Dinh Quoc Viet
Ngày chạy: 2026-11-26
Môi trường: Windows 11, Python 3.13, Docker Desktop 29.9.3, Docker Compose v5.7.0

## 1. SLO của agent

| SLI | SLO | Lý do |
|---|---:|---|
| p95 latency /ask | < 500 ms | Bảo đảm phần lớn request phản hồi nhanh |
| Error rate /ask | < 2% | Cho phép lỗi upstream mock ngẫu nhiên |
| Accuracy golden dataset | >= 80% | Quality gate tối thiểu trước deploy |

## 2. Benchmark hiệu năng

### 2.1 Concurrency vs latency

| Concurrency | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Error rate | SLO |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 4.19 | 203.1 | 233.8 | 1716.5 | 1.67% | PASS |
| 10 | 30.41 | 207.2 | 1689.8 | 1716.0 | 1.00% | FAIL p95 |
| 50 | 97.74 | 204.7 | 519.7 | 1688.9 | 1.00% | FAIL p95 |
| 100 | 56.81 | 665.8 | 4130.0 | 4442.3 | 0.33% | FAIL p95 |

RPS tăng mạnh đến concurrency 50 nhưng không tuyến tính ở 100 vì mock LLM và request chậm tạo tail latency.

### 2.2 Tail latency

| MOCK_SLOW_RATE | Average (ms) | p95 (ms) | p99 (ms) |
|---:|---:|---:|---:|
| 0 | 215.8 | 458.2 | 481.4 |
| 0.03 | 232.0 | 452.6 | 518.7 |
| 0.1 | 396.4 | 1704.3 | 1735.7 |

p95/p99 nhạy hơn average với request chậm; SLO không nên chỉ dùng average.

## 3. Benchmark chất lượng

| Chỉ số | Agent v1 | Agent v2 | Agent v2 sau sửa KB |
|---|---:|---:|---:|
| Accuracy | 4.35% (1/23) | 100% (23/23) | 100% (23/23) |
| Avg tokens/câu | 57.5 | 115.7 | 115.7 |
| Tổng cost (USD) | 0.000410 | 0.000808 | 0.000808 |
| Cost/câu đúng (USD) | 0.00040995 | 0.00003513 | 0.00003513 |
| Quality gate | FAIL | PASS | PASS |

Đã bổ sung knowledge base cho security-02 (JWT/API key) và scaling-03 (Kubernetes HPA). v2 cải thiện 22 câu, không regression.

## 4. Observability stack

Stack production đã chạy local bằng Docker Compose với agent, nginx, Prometheus, Grafana, Jaeger và Locust. Dockerfile production được sửa để runtime tìm đúng Python site-packages dưới user `agent`; sau đó container agent healthy.

Endpoint kiểm tra: nginx `/health` trả 200; `/metrics` bị chặn 404 ở nginx và chỉ Prometheus scrape trực tiếp trong mạng nội bộ theo thiết kế.

## 5. Benchmark scaling

Locust headless đã chạy 2 phút, 100 users, spawn rate 10/s. CSV gốc nằm trong `06-lab-complete/benchmark-observability/production/benchmark-results/` và bản sao ở `benchmark-results/`.

| Run | Request tổng | Lỗi | RPS | p50 tổng hợp | p95 tổng hợp | Ghi chú |
|---|---:|---:|---:|---:|---:|---|
| scale_1 | 7,822 | 76 (0.97%) | 65.79 | 190 ms | 260 ms | lỗi 503 từ mock/upstream |
| scale_3 | 7,817 | 78 (1.00%) | 65.79 | 190 ms | 260 ms | lỗi 503 từ mock/upstream |

Hai run đều đạt error rate dưới SLO 2% và p95 dưới 500 ms, nhưng tail p98 khoảng 1.7 s và lỗi 503 vẫn cần xử lý nếu yêu cầu production nghiêm ngặt. Kết quả scale_3 cần hiểu là Compose đã duy trì hai replica hiện hữu trong lúc chạy; log/container lifecycle cần chuẩn hóa thêm nếu muốn benchmark tách biệt hoàn toàn giữa đúng 1 và đúng 3 replica.

## 6. Kết luận

1. Average latency không phản ánh tail latency.
2. Eval chất lượng cần chạy cùng load test.
3. v2 tốn token hơn nhưng cost trên mỗi câu đúng thấp hơn nhiều.
4. Production observability stack đã được kiểm chứng local; chưa deploy cloud/public URL vì workspace không có credentials hoặc tài khoản cloud được cấp.

