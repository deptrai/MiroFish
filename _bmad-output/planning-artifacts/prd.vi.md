---
stepsCompleted: ["step-01-init", "step-02-discovery", "step-02b-vision", "step-02c-executive-summary", "step-03-success"]
inputDocuments:
  - "/Users/luisphan/Documents/GitHub/MiroFish/_bmad-output/project-context.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/index.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/project-overview.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/architecture.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/source-tree-analysis.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/component-inventory.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/api-contracts.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/data-models.md"
  - "/Users/luisphan/Documents/GitHub/MiroFish/docs/development-guide.md"
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 9
workflowType: "prd"
classification:
  projectType: "web_app"
  domain: "scientific"
  complexity: "medium"
  projectContext: "brownfield"
---

# Tài Liệu Yêu Cầu Sản Phẩm (PRD) - MiroFish

**Tác giả:** Luisphan  
**Ngày:** 2026-05-17

## Tóm Tắt Điều Hành

MiroFish là một nền tảng dự đoán AI theo hướng brownfield, chuyển đổi dữ liệu hạt giống phi cấu trúc thành pipeline mô phỏng có thể vận hành để diễn tập quyết định. Thay vì dừng ở tóm tắt tài liệu, hệ thống xây dựng world model dựa trên graph, khởi tạo các social agent, và chạy mô phỏng song song trên hai nền tảng để làm lộ tín hiệu xu hướng trước khi kết quả thực tế xảy ra.

Sản phẩm được thiết kế cho các nhóm cần đánh giá kịch bản chính sách, truyền thông, hoặc thị trường trong điều kiện bất định. Giá trị cốt lõi là năng lực dự báo mang tính thực dụng: người dùng có thể đưa giả định vào mô hình, quan sát hành vi trồi lên theo thời gian, và lặp lại quyết định dựa trên bằng chứng sinh ra từ động lực mô phỏng thay vì chỉ phân tích tĩnh.

### Điểm Khác Biệt Cốt Lõi

MiroFish khác biệt nhờ chuỗi vận hành end-to-end: `nạp tài liệu -> tạo ontology và graph -> mô phỏng đa tác tử -> tạo báo cáo và truy vấn tương tác`. Sự tích hợp này tạo ra vòng lặp phản hồi nơi biểu diễn tri thức và sinh hành vi củng cố lẫn nhau.

Insight cốt lõi là chất lượng dự đoán tăng lên khi ngữ cảnh có cấu trúc (graph memory) được kết hợp với tương tác tác tử tiến hóa theo thời gian. Phân tích tĩnh có thể nhận diện sự kiện và quan hệ; mô phỏng giúp bộc lộ hiệu ứng bậc hai, mẫu lan truyền, và chuyển dịch emergent mà tài liệu thuần văn bản khó suy ra.

## Phân Loại Dự Án

- **Loại dự án:** Ứng dụng web (SPA + workflow system dựa trên API)
- **Miền bài toán:** Mô phỏng tính toán / phân tích có hỗ trợ AI
- **Độ phức tạp:** Trung bình
- **Ngữ cảnh dự án:** Brownfield (mở rộng và hoàn thiện hệ thống đang có)

## Tiêu Chí Thành Công

### Thành Công Của Người Dùng

- Người dùng mới có thể hoàn tất flow end-to-end đầu tiên (upload -> graph -> simulation -> report) trong vòng 30 phút mà không cần đọc mã nguồn.
- Analyst có thể trả lời ít nhất 3 câu hỏi "what-if" trong một phiên bằng report và interaction view.
- Tỉ lệ hoàn tất flow từ `/` đến lần tạo report đầu tiên đạt tối thiểu 60% trong môi trường pilot nội bộ.

### Thành Công Kinh Doanh

- Mức độ áp dụng nội bộ mở rộng đến ít nhất 3 team/use-case trong 8 tuần.
- Hành vi quay lại tăng: ít nhất 40% dự án kích hoạt lần chạy simulation thứ hai trong vòng 14 ngày.
- Mỗi pilot ghi nhận ít nhất một quyết định/khuyến nghị chịu ảnh hưởng bởi output của MiroFish.

### Thành Công Kỹ Thuật

- Tình trạng backend ổn định, endpoint `/health` luôn sẵn sàng trong các khung giờ vận hành pilot.
- Tiến trình thực thi theo từng phase có thể truy vết qua status endpoints của graph/simulation/report và log nhất quán.
- Tỉ lệ lỗi job do vấn đề cấu hình/môi trường/đầu vào giảm đáng kể nhờ kiểm tra preflight tốt hơn và thông báo lỗi rõ ràng hơn.

### Kết Quả Đo Lường

- Time-to-first-report (TTFR): median <= 30 phút.
- Tỉ lệ tạo report thành công: >= 85% với đầu vào hợp lệ.
- Tỉ lệ hoàn tất simulation: >= 80% với cấu hình mặc định.
- Lỗi nghiêm trọng lọt ra sau mỗi bản phát hành pilot (P0/P1): 0.

## Phạm Vi Sản Phẩm

### MVP - Sản Phẩm Khả Dụng Tối Thiểu

- Onboarding rõ ràng cho workflow 5 bước.
- Kiểm tra hợp lệ và phản hồi lỗi tốt hơn cho input/env/config trước các job chạy dài.
- Hiển thị trạng thái/tiến trình/log nhất quán từ frontend đến backend.
- Chất lượng report đủ dùng cho vòng decision rehearsal đầu tiên.

### Tính Năng Tăng Trưởng (Sau MVP)

- Bộ template kịch bản theo domain/use-case.
- So sánh nhiều lần chạy simulation (kiểu A/B).
- Cải thiện observability và cơ chế retry/recovery cho simulation chạy dài.

### Tầm Nhìn (Tương Lai)

- Workbench decision-intelligence nơi người dùng tạo, chạy lại, so sánh và audit nhiều future rehearsal trên cùng graph memory.
- Framework chấm điểm chuẩn hóa để so sánh chất lượng kịch bản theo các metric khách quan.
