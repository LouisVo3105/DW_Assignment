import streamlit as st

st.set_page_config(
    page_title="Congestion Analysis",
    page_icon="🚦",
    layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 95%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    [data-testid="stSidebar"] {
        min-width: 220px;
        max-width: 220px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚦 Hệ thống phân tích & dự đoán tắc nghẽn giao thông")

st.write("""
Chọn một trang trong sidebar để tiếp tục:
- **Dashboard**: phân tích dữ liệu tắc nghẽn theo thời tiết/ngày/giờ  
- **Dự đoán**: nhập dữ liệu và dự đoán tắc nghẽn bằng mô hình sklearn  
""")
