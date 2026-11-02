# US Traffic Congestion Analytics & Data Warehouse

**Data Warehousing · ETL · BI Visualization · Machine Learning**

Dự án xây dựng quy trình dữ liệu phân tích giao thông Hoa Kỳ, từ nạp và chuẩn hóa dữ liệu đến kho dữ liệu dạng star schema, trực quan hóa chỉ số ùn tắc và thử nghiệm mô hình phân loại.

## Dự án trong một phút

- **Mục tiêu:** tổ chức dữ liệu sự kiện giao thông để phân tích theo thời gian, vị trí và điều kiện thời tiết.
- **Dữ liệu:** bộ dữ liệu giao thông Hoa Kỳ giai đoạn 2016–2022. Project mô tả nguồn là mẫu 2 triệu bản ghi; repository hiện chứa các bảng CSV đã chuẩn bị, không bao gồm toàn bộ dữ liệu thô.
- **Pipeline:** PostgreSQL staging → Pentaho Data Integration → MS SQL Server Data Warehouse.
- **Phân tích:** dashboard BI, Python notebooks và thử nghiệm phân loại ba mức congestion bằng XGBoost và MLP.
- **Ứng dụng:** Streamlit dashboard và trang demo dự đoán.

## Quy trình ETL

### Nạp CSV vào staging

Transform đầu tiên lấy dữ liệu từ CSV gốc và ghi vào bảng staging trong PostgreSQL.

![Pentaho: nạp CSV vào staging](<REPORT/Load-Stagging.png>)

### Nạp các dimension

Sau khi đọc dữ liệu staging, pipeline chọn trường, tính toán các thuộc tính dẫn xuất và phân nhánh để nạp dimension vị trí, thời tiết và thời gian.

![Pentaho: nạp các bảng dimension](<REPORT/Load-to-Dim.png>)

### Nạp bảng fact

Pipeline fact tra cứu các khóa dimension theo location, weather và time, sau đó ghi các số đo cùng khóa vào bảng fact.

![Pentaho: tra cứu dimension và nạp fact](<REPORT/Stagging-to-DW.png>)

### Mô hình dữ liệu

`FactAccident` lưu các số đo và thuộc tính sự kiện như `severity`, `distance_mi`, thời gian trễ và `congestion_speed`. Các bảng `DimLocation`, `DimWeather`, `DimTime` cung cấp các chiều phân tích để tổng hợp theo địa điểm, thời tiết và thời gian.

```text
                   ┌────────────────┐
                   │  DimLocation   │
                   └───────┬────────┘
                           │
┌──────────────┐   ┌───────▼────────┐   ┌──────────────┐
│  DimWeather  ├──►│  FactAccident  │◄──┤   DimTime    │
└──────────────┘   └────────────────┘   └──────────────┘
```

## Trực quan hóa và phân tích

### Phân bố sự kiện theo địa lý

Bản đồ thể hiện các vị trí có sự kiện tắc nghẽn. Các cụm điểm tập trung tại nhiều khu vực đô thị và hành lang giao thông của Hoa Kỳ.

![Bản đồ vị trí các sự kiện giao thông](<REPORT/Phân bố  mật độ tắt nghẽn.png>)

### Biểu đồ BI về trễ và congestion

Hình BI trong báo cáo tổng hợp thời gian trễ theo ngày, so sánh delay per mile và delay ratio giữa các nhãn `congestion_speed`, đồng thời hiển thị tổng `dist_freeflow` và chỉ số thời tiết theo tháng.

![Dashboard các chỉ số liên quan đến congestion](<REPORT/Các ảnh hưởng với tốc độ tắt nghẽn.png>)


## Thử nghiệm Machine Learning

Hai notebook xây dựng mô hình phân loại ba mức độ congestion. Kết quả dưới đây được đọc từ output đã lưu trong notebook, trên tập holdout 200 quan sát:

| Mô hình | Accuracy | Macro F1 | Weighted F1 |
|---|---:|---:|---:|
| XGBoost | 0.650 | 0.640 | 0.65 |
| MLP (PyTorch) | 0.575 | 0.566 | 0.58 |

Trong lần chạy được lưu, XGBoost đạt điểm cao hơn MLP. Tập holdout nhỏ nên kết quả này chỉ phản ánh lần thử nghiệm trong notebook; cần đánh giá trên dữ liệu mới và đại diện hơn trước khi cân nhắc triển khai.


## Công nghệ

`SQL` · `PostgreSQL` · `Microsoft SQL Server` · `Pentaho Data Integration` · `Python` · `Pandas` · `scikit-learn` · `XGBoost` · `PyTorch` · `Streamlit`

## Tài liệu

- [Báo cáo Data Warehouse](REPORT/Data_Warehouse_Report.pdf)
- [Slide trình bày](REPORT/Data_WareHouse_Slide.pdf)
- [Notebook XGBoost](RESULT/XGB.ipynb)
- [Notebook MLP](RESULT/MLP.ipynb)

## Hạn chế và khả năng mở rộng

- Các CSV trong repository là dữ liệu đã chuẩn bị; không có toàn bộ dữ liệu nguồn để tái chạy từ đầu.
- Để chạy lại ETL cần cấu hình PostgreSQL, SQL Server và Pentaho theo môi trường cài đặt.
- Trang dự đoán hiện là demo. Repository chưa kèm đầy đủ artifact encoder/scaler để tái tạo mọi bước tiền xử lý; đầu vào cần khớp với cách mã hóa và chuẩn hóa lúc huấn luyện.
- Có thể cải thiện đánh giá bằng cách tăng kích thước tập holdout, kiểm soát phân tầng lớp và lưu toàn bộ pipeline tiền xử lý cùng model.
