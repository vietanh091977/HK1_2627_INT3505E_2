# Review Public API

## Thông tin 
- API: [Google AI Studio (Gemini API)](https://ai.google.dev/gemini-api/docs/deprecations?authuser=8&hl=en)
- Họ và tên: Lê Nguyễn Việt Anh - Nhóm 6
- Nhiệm vụ: Đánh giá tiêu chí 6 (Pagination) và tiêu chí 7 (Filter/Sort)

## 1. Pagination

Áp dụng chiến lược Cursor-based:
- Có giới hạn trên: Sử dụng tham số `pageSize` để kiểm soát số lượng phần tử trả về trong 1 trang
- Sử dụng opaque token, response trả `nextPageToken`, client gửi lại giá trị đó qua `pageToken` để lấy trang kế. Trong một response, nếu còn dữ liệu thì JSON body sẽ chứa trường `nextPageToken`, không có nghĩa là không còn dữ liệu 

### Ví dụ một số endpoint:

| Endpoint | Tham số | `pageSize` mặc định | `pageSize` tối đa |
| --- | --- | --- | --- |
| `GET /v1beta/models` | pageSize, pageToken | 50 | 1000 |
| `GET /v1beta/files` | pageSize, pageToken | 10 | 100 |

## 2. Filter/Sort

- Filtering: Các collection endpoints như `GET /v1beta/models` hay `GET /v1beta/files` hiện không hỗ trợ việc filtering qua tham số
- Sorting: API này cũng không hỗ trợ sorting qua tham số, thứ tự dữ liệu trả về do server quyết định
- Sparse fieldsets: Không hỗ trợ sparse fieldsets

