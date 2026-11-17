# Lab 4 — Phân tích kết quả

Môi trường đo: máy cá nhân, Flask development server + SQLite, Locust chạy cùng máy (localhost).
Số liệu lấy từ báo cáo `reports/A.html`, `B.html`, `C.html`.

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 29s | 9 | 0% (0/140) | 4,74 |
| B | 50 | 5 | 59s | 14 | 0,43% (6/1.381) | 23,18 |
| C | 200 | 50 | 29s | 61 | 0,34% (5/1.486) | 50,07 |

## 1. Kịch bản có p95 cao nhất

**Kịch bản C (200 user): p95 = 61 ms**, so với 14 ms ở B và 9 ms ở A.
Khi user tăng 4 lần (50 → 200), p95 tăng ~4,4 lần và RPS tăng ~2,2 lần (23,18 → 50,07): tải đồng thời lớn hơn thì các request chia sẻ cùng một tiến trình server nên độ trễ đuôi tăng. Nguyên nhân khả dĩ: Flask development server là single-process, các request ghi `POST /books` phải chờ nhau do SQLite chỉ cho phép một tiến trình được quyền ghi tại một thời điểm.

## 2. Endpoint nào tăng failure rate

Các endpoint `GET /books`, `GET /books/{id}`, `POST /books` đều không có lỗi ở cả 3 kịch bản. `GET /books?year=` có fail rate: 0% (0/21) ở kịch bản A, 3.04% (6/197) ở kịch bản B, 2.29% (5/218) ở kịch bản C. Đây là failure do Locust đánh dấu bằng `response.failure(...)` với xác suất 1% cho mỗi lần gọi task `search_by_year()`, không phải HTTP 500 (server vẫn trả về HTTP 200).

## 3. Với SLO giả định p95 < 300 ms

Cả ba kịch bản đều đạt: p95 lớn nhất là 61 ms ở C.

Giới hạn của phép đo:
- Locust và Server dùng chung tài nguyên CPU/RAM
- localhost không có độ trễ mạng
- Flask dev server + SQLite không dùng cho production

Vậy nên không thể kết luận SLO production từ các thông số này.

Đề xuất baseline cho CI gate: chạy một kịch bản kiểu B ngắn (50 user, 30 s) trên runner cố định; fail khi p95 > 300 ms hoặc có HTTP 5xx / timeout thật.

## 4. Nếu connection pool giới hạn ở 5

Khi pool chỉ có 5 connection và 200 user truy cập đồng thời:
- Xuất hiện HTTP 500 thật với lỗi `QueuePool limit ... timed out`
- p95/p99 của các endpoint DB tăng vì request phải chờ lấy connection;
- RPS không còn tăng theo số user

Cách kiểm chứng: đặt `SQLALCHEMY_ENGINE_OPTIONS = {"pool_size": 5, "max_overflow": 0, "pool_timeout": 2}` trong `create_app`, rồi chạy lại kịch bản C với DB mới và so sánh với kết quả C ở trên.