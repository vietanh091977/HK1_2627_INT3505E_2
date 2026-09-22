# Audit GitHub API

**1. Lấy thông tin một user**
* **Endpoint:** `/users/{username}`
* **Method:** `GET`
* **Status codes:** `200 OK`, `404 Not Found`
* **Headers:** `Accept: application/vnd.github+json`
* **Tính RESTful:** **Có.** Endpoint sử dụng danh từ `/users/` định danh đúng resource, dùng `GET` để truy xuấy dữ liệu mà không làm thay đổi trạng thái server.

**2. Tạo mới một Repository**
* **Endpoint:** `/user/repos`
* **Method:** `POST`
* **Status codes:** `201 Created`, `422 Unprocessable Entity`
* **Headers:** `Accept: application/vnd.github+json`, `Authorization: Bearer <YOUR_TOKEN>`, `Content-Type: application/json`
* **Tính RESTful:** **Có.** Dùng `POST` để tạo resource mới, trả về dúng mã `201 Created` kèm theo URI của resource mới trong header `Location`.

**3. Cập nhật thông tin Repository**
* **Endpoint:** `/repos/{owner}/{repo}`
* **Method:** `PATCH`
* **Status codes:** `200 OK`
* **Headers:** `Accept: application/vnd.github+json`, `Authorization: Bearer <YOUR_TOKEN>`, `Content-Type: application/json`
* **Tính RESTful:** **Có.** Dùng `PATCH` cho việc cập nhật một phần dữ liệu là chuẩn theo REST.

**4. Xóa Repository**
* **Endpoint:** `/repos/{owner}/{repo}`
* **Method:** `DELETE`
* **Status codes:** `204 No Content`, `403 Forbidden`.
* **Headers:** `Accept: application/vnd.github+json`, `Authorization: Bearer <YOUR_TOKEN>`
* **Tính RESTful:** **Có.** Trả về đúng mã `204 No Content` do sau khi xóa thì không cần trả về body content.

**5. Lấy danh sách Issues của Repository**
* **Endpoint:** `/repos/{owner}/{repo}/issues`
* **Method:** `GET`
* **Status codes:** `200 OK`
* **Headers:** `Accept: application/vnd.github+json`
* **Tính RESTful:** **Có.** Tương tự như lấy thông tin users