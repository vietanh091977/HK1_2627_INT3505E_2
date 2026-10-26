# Security Audit - Social Network API (Auth & Posts)

Phạm vi: ba endpoint `POST /auth/login`, `POST /auth/refresh`, `GET /posts/{id}`

| STT | Điểm có thể bị lộ | Hậu quả | Biện pháp |
|---|---|---|---|
| 1 | `GET /posts/{id}` chỉ kiểm tra token hợp lệ mà thiếu kiểm tra quyền sở hữu đối tượng. | Kẻ tấn công đọc được toàn bộ bài viết riêng tư của tài khoản khác. | Kiểm tra scope `posts:read`, so sánh `author_id` với người gọi; trả về `404` cho bài không được phép xem. |
| 2 | `POST /auth/login` không áp dụng rate-limit. | Kẻ tấn công chiếm đoạt tài khoản bằng cách thử hàng loạt mật khẩu. | Áp dụng rate-limit nghiêm ngặt theo IP và theo tài khoản; trả `429` kèm `Retry-After`. |
| 3 | Refresh token bị đánh cắp/tái sử dụng. | Kẻ tấn công liên tục duy trì phiên truy cập trái phép lấy access token mới mà không cần mật khẩu. | Lưu `jti` phía server để thu hồi, thực hiện xoay vòng token sau mỗi lần dùng và thu hồi toàn bộ phiên nếu phát hiện token cũ bị gửi lại. |
| 4 | Lộ tài khoản do phản hồi khác nhau hoặc chênh lệch thời gian xử lý giữa email tồn tại và không tồn tại. | Kẻ tấn công thực hiện quét tài khoản để xác định email nào đã đăng ký trên hệ thống. | Trả thông báo lỗi chung `invalid_credentials` với cùng mã `401`, đồng thời luôn chạy kiểm tra hàm băm để đồng nhất thời gian phản hồi. |
| 5 | Trả nguyên bản ghi database hoặc cho phép client gửi kèm trường nhạy cảm. | Rò rỉ dữ liệu nội bộ (như `password_hash`) hoặc cho phép người dùng tự nâng quyền (như `is_admin`). | Serialize dữ liệu qua DTO sử dụng whitelist trường cho cả đọc và ghi; cấu hình `additionalProperties: false` cho schema request. |