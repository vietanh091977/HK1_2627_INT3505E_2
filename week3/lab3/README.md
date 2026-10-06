# Lab 3: Triển khai `/orders` có Cursor Pagination

## Cấu trúc một response

![Response](../proofs/lab3_rs.png)

## Results

### Server log

![Server log](../proofs/lab3_serverlog.png)

### Test với limit nhỏ, lấy `next_cursor`

![Test 1](../proofs/lab3_test1.png)

### Dùng `next_cursor` từ response trước để lấy trang kế tiếp

![Test 2](../proofs/lab3_test2.png)

### Filter theo `status=paid`

![Test 3](../proofs/lab3_test3.png)

### Sparse fieldsets

![Test 4](../proofs/lab3_test4.png)

### Sort + Filter

![Test 5](../proofs/lab3_test5.png)

### Cursor hỏng

![Test 6](../proofs/lab3_test6.png)

### Invalid field

![Test 7](../proofs/lab3_test7.png)