# Thiết Kế Hệ Thống Blog API

## 1. Xác định Resources (Tài nguyên trong miền)

Dựa trên yêu cầu của nền tảng blog, hệ thống xoay quanh 4 tài nguyên chính
*   **Users:** Người dùng hệ thống/tác giả, bao gồm thông tin hồ sơ cá nhân và tính năng theo dõi (follow) tác giả khác
*   **Posts:** Bài viết trên blog
*   **Comments:** Bình luận của người dùng trên các bài viết cụ thể
*   **Tags:** Thẻ phân loại được gắn vào bài viết

---

## 2. Phân loại Resource

*   **Collection (Tập hợp):** Dùng để truy xuất danh sách hoặc tạo mới tài nguyên
    *   `/users`
    *   `/posts`
    *   `/tags`
*   **Item (Tài nguyên đơn lẻ):** Dùng để thao tác trên một tài nguyên cụ thể
    *   `/users/{user_id}`
    *   `/posts/{post_id}`
    *   `/tags/{tag_id}`
*   **Sub-resource (Tài nguyên con):** Thể hiện quan hệ cha-con trực tiếp
    *   `/posts/{post_id}/comments`: Bình luận phụ thuộc vào bài viết
    *   `/users/{user_id}/followers` hoặc `/users/{user_id}/following`: Chức năng theo dõi người dùng

---

## 3. Sơ đồ cây Endpoint & Version Segment

### Users (Người dùng)
*   `GET    /api/v1/users` : Lấy danh sách người dùng.
*   `GET    /api/v1/users/{user_id}` : Xem hồ sơ chi tiết của người dùng.
*   `GET    /api/v1/users/{user_id}/followers` : Lấy danh sách những người theo dõi user này
*   `POST   /api/v1/users/{user_id}/followers` : Theo dõi user này
*   `DELETE /api/v1/users/{user_id}/followers` : Hủy theo dõi

### Posts (Bài viết)
*   `GET    /api/v1/posts` : Lấy danh sách bài viết
*   `POST   /api/v1/posts` : Đăng bài viết mới
*   `GET    /api/v1/posts/{post_id}` : Xem chi tiết một bài viết
*   `PATCH  /api/v1/posts/{post_id}` : Cập nhật một số nội dung của bài viết
*   `DELETE /api/v1/posts/{post_id}` : Xóa bài viết

### Comments (Bình luận)
*   `GET    /api/v1/posts/{post_id}/comments` : Lấy danh sách bình luận của một bài viết cụ thể
*   `POST   /api/v1/posts/{post_id}/comments` : Thêm bình luận mới vào bài viết

### Tags (Thẻ)
*   `GET    /api/v1/tags` : Lấy danh sách tất cả các thẻ hiện có trên blog