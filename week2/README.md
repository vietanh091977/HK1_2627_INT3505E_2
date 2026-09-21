# Week 2

## Bài 1: GET list + POST create

### Server log

![E1 server log](proofs/e1_serverlog.png)

### GET /books - Lấy danh sách

![E1 test 1](proofs/e1_test_1.png)

### POST /books - Tạo resource mới

![E1 test 2](proofs/e1_test_2.png)

### POST /books thiếu field - `422 Unprocessable Entity`

![E1 test 3](proofs/e1_test_3.png)

### POST /books thiếu Content-Type - `415 Unsupported Media Type`

![E1 test 4](proofs/e1_test_4.png)

## Bài 2: PUT + PATCH + DELETE

### Server log

![E2 server log](proofs/e2_serverlog.png)

### PATCH /books - cập nhật 1 field

![E2 test 1](proofs/e2_test_1.png)

### PUT /books - cập nhật toàn bộ field

![E2 test 2](proofs/e2_test_2.png)

### DELETE /books - Xoá

![E2 test 3](proofs/e2_test_3.png)

## Bài 3: Pagination + Filtering

### Server log

![E3 server log](proofs/e3_serverlog.png)

### Pagination với page và size

![E3 test 1](proofs/e3_test_1.png)

### Lọc theo tên tác giả

![E3 test 2](proofs/e3_test_2.png)

### Lọc theo tựa đề

![E3 test 3](proofs/e3_test_3.png)

### Yêu cầu response định dạng JSON

![E3 test 4](proofs/e3_test_4.png)