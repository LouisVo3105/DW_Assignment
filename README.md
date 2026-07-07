# 🚦 Hệ thống Kho Dữ liệu Giao thông Mỹ & Dự báo Tắc nghẽn


## 1. 🎯 Vấn đề cần giải quyết
Tắc nghẽn giao thông là một thách thức nghiêm trọng trong quá trình đô thị hóa, gây thiệt hại hàng trăm tỷ USD mỗi năm, làm tăng lượng khí thải và giảm chất lượng cuộc sống. 
Thách thức đặt ra là làm thế nào để thu thập, lưu trữ và phân tích hiệu quả một lượng dữ liệu giao thông khổng lồ nhằm thấu hiểu các quy luật tắc nghẽn. Dự án này nhằm mục đích xây dựng một Kho dữ liệu (Data Warehouse) và Hệ hỗ trợ quyết định (DSS) mạnh mẽ, giúp các hệ thống Giao thông thông minh (ITS) điều tiết phương tiện và quy hoạch hạ tầng dựa trên dữ liệu thực tế.

## 2. 🗂 Dữ liệu đầu vào
Dự án sử dụng bộ dữ liệu **"US Traffic Congestions (2016-2022)"**. 
* **Khối lượng:** Tập mẫu gồm 2 triệu bản ghi (được trích xuất từ tập dữ liệu gốc 33 triệu bản ghi).
* **Dữ liệu Không gian:** Vĩ độ, Kinh độ, Đường, Thành phố, Bang, Mã bưu chính.
* **Dữ liệu Thời gian:** Thời gian bắt đầu/kết thúc, Múi giờ địa phương.
* **Dữ liệu Khí tượng:** Nhiệt độ, Độ ẩm, Lượng mưa, Tốc độ gió, Điều kiện thời tiết.
* **Chỉ số Giao thông:** Mức độ nghiêm trọng, Quãng đường bị ảnh hưởng, Độ trễ so với thông thường, Tốc độ lưu thông khi tắc nghẽn.

## 3. 🛠 Phương pháp & Cách tiếp cận
Để chuyển hóa dữ liệu thô thành các insight có giá trị, dự án được triển khai qua một quy trình khép kín:

* **Trích xuất & Đưa dữ liệu vào Staging:** Đưa toàn bộ dữ liệu thô vào khu vực Staging sử dụng cơ sở dữ liệu **PostgreSQL**.
* **Xây dựng ETL Pipeline (Vai trò cốt lõi):** Thiết kế luồng dữ liệu tự động bằng **Pentaho Data Integration**. Áp dụng các quy tắc làm sạch nghiêm ngặt như điền khuyết dữ liệu thời tiết dựa trên không gian/thời gian và chuẩn hóa định dạng địa lý.
* **Mô hình hóa Kho dữ liệu:** Xây dựng kiến trúc **Star Schema** trên **MS SQL Server**. Lược đồ xoay quanh bảng trung tâm `FactAccident` và các bảng chiều (`DimTime`, `DimLocation`, `DimWeather`, `dim_season`) để tối ưu hóa các truy vấn phân tích đa chiều (OLAP).
* **Phân tích Khám phá (EDA):** Truy vấn từ Data Marts để phân tích phân phối và ma trận tương quan, qua đó trực quan hóa các xu hướng không gian - thời gian.
* **Machine Learning:** Nhóm áp dụng các thuật toán tiên tiến (XGBoost và Mạng nơ-ron đa lớp - MLP) để dự báo mức độ tắc nghẽn và tìm ra các mối quan hệ phi tuyến phức tạp.

## 4. 🏆 Kết quả đạt được
Dự án đã triển khai thành công một luồng dữ liệu hoàn chỉnh và các công cụ hỗ trợ quyết định:
1. **Kho dữ liệu tập trung:** Một Data Warehouse chuẩn Star Schema có khả năng xử lý hàng triệu bản ghi với hiệu suất truy vấn cao.
2. **Dashboard DSS tương tác:** Phát triển giao diện web bằng **Streamlit** giúp trực quan hóa số liệu giao thông, phân bố thời tiết và xu hướng tắc nghẽn theo giờ.
3. **Mô hình dự báo hiệu suất cao:** Triển khai mô hình **XGBoost Classifier** vượt trội hơn so với phương pháp Deep Learning (MLP), đạt **Độ chính xác tổng thể 76.66%** và **F1-Score cân bằng ở mức 0.77** trên nhiều lớp tắc nghẽn khác nhau.

## 5. 💡 Insight & Đề xuất
### Insight từ Dữ liệu
* **Động lực Phi tuyến tính:** Phân tích khám phá chứng minh rằng tắc nghẽn giao thông gần như không có tương quan tuyến tính với các chỉ số thời tiết đơn lẻ (như nhiệt độ hay lượng mưa). Tắc nghẽn là kết quả của những tương tác phi tuyến phức tạp.
* **Độ quan trọng của Đặc trưng:** Các yếu tố hạ tầng không gian - thời gian (đặc điểm tuyến đường, khoảng cách, giờ trong ngày) có tác động đến tốc độ ùn tắc lớn hơn nhiều so với chỉ riêng các sự kiện thời tiết.

### Đề xuất Hành động
* **Dành cho Quản lý Giao thông:** Các nhà quy hoạch nên ưu tiên theo dõi hạ tầng và điều phối tuyến đường theo thời gian thực thay vì chỉ dựa vào các cảnh báo thời tiết thuần túy.
* **Phát triển Hệ thống:** Để đáp ứng yêu cầu độ trễ thấp (dưới 1 giây) khi triển khai trên các thiết bị biên như camera thông minh, mô hình dự báo cần áp dụng các kỹ thuật Nén (Quantization) hoặc Cắt tỉa (Pruning). 
* **Cải tiến Thuật toán:** Trong tương lai, nên chuyển từ mô hình dạng bảng sang kiến trúc Chuỗi thời gian (như LSTM hoặc Transformers) để nắm bắt tính kế thừa liên tục của các vụ tắc nghẽn.
