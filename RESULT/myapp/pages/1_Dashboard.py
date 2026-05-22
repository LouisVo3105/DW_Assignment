import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("Dashboard phân tích Congestion Speed")

uploaded = st.file_uploader("Tải lên dataset CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    df["starttime"] = pd.to_datetime(df["starttime"])
    df["day_of_week"] = df["starttime"].dt.day_name()
    df["hour"] = df["starttime"].dt.hour

    st.success("Dữ liệu đã sẵn sàng!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Congestion Speed TB", f"{df['congestion_speed'].mean():.2f}")
    col2.metric("Delay per Mile TB", f"{df['delay_per_mile'].mean():.2f}")
    col3.metric("Số record", len(df))

    st.divider()

    # Weather analysis - ĐẾM số lượng record theo các loại thời tiết
    st.header("Phân bố các điều kiện thời tiết")
    
    # Danh sách các cột thời tiết (giả sử có các cột này)
    weather_columns = ['fog', 'rain', 'snow', 'hail', 'thunderstorm', 'tornado']
    
    # Kiểm tra xem các cột có tồn tại trong dataframe không
    available_weather_cols = [col for col in weather_columns if col in df.columns]
    
    if available_weather_cols:
        # Đếm số lượng record có giá trị = 1 cho mỗi loại thời tiết
        weather_counts = {}
        for col in available_weather_cols:
            count = df[df[col] == 1].shape[0]  # Đếm số dòng có giá trị = 1
            weather_counts[col] = count
        
        # Chuyển thành DataFrame để dễ hiển thị
        weather_df = pd.DataFrame({
            'Weather Condition': list(weather_counts.keys()),
            'Count': list(weather_counts.values())
        })
        
        # Tính phần trăm
        weather_df['Percentage'] = (weather_df['Count'] / len(df) * 100).round(2)
        
        # Sắp xếp theo số lượng giảm dần
        weather_df = weather_df.sort_values('Count', ascending=False)
        
        # Tạo figure với kích thước nhỏ hơn
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Biểu đồ cột
        bars = ax1.bar(weather_df['Weather Condition'], weather_df['Count'], color='skyblue')
        ax1.set_title("Số lượng record theo điều kiện thời tiết")
        ax1.set_xlabel("Điều kiện thời tiết")
        ax1.set_ylabel("Số lượng record (giá trị = 1)")
        ax1.tick_params(axis='x', rotation=45)
        
        # Thêm số trên mỗi cột
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        # Biểu đồ tròn
        colors = plt.cm.Set3(np.linspace(0, 1, len(weather_df)))
        ax2.pie(weather_df['Count'], labels=weather_df['Weather Condition'], 
                autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title("Phân bố tỷ lệ các điều kiện thời tiết")
        
        plt.tight_layout()
        st.pyplot(fig)
        
        st.subheader("Thống kê chi tiết")
        
        clear_count = len(df[df[available_weather_cols].sum(axis=1) == 0])
        total_df = pd.DataFrame({
            'Weather Condition': ['clear'] + list(weather_df['Weather Condition']),
            'Count': [clear_count] + list(weather_df['Count']),
            'Percentage': [(clear_count/len(df)*100)] + list(weather_df['Percentage'])
        })
        
        st.dataframe(total_df, use_container_width=True)
        
        # Congestion Speed trung bình theo từng điều kiện thời tiết
        st.subheader("Congestion Speed trung bình theo điều kiện thời tiết")
        
        speed_by_weather = []
        for col in available_weather_cols:
            if weather_counts[col] > 0:  # Chỉ tính nếu có ít nhất 1 record
                avg_speed = df[df[col] == 1]['congestion_speed'].mean()
                speed_by_weather.append({
                    'Weather Condition': col,
                    'Avg Congestion Speed': round(avg_speed, 2),
                    'Count': weather_counts[col]
                })
        
        if speed_by_weather:
            speed_df = pd.DataFrame(speed_by_weather)
            
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            bars2 = ax3.bar(speed_df['Weather Condition'], speed_df['Avg Congestion Speed'], 
                           color='lightcoral')
            ax3.set_title("Congestion Speed trung bình khi có điều kiện thời tiết")
            ax3.set_xlabel("Điều kiện thời tiết")
            ax3.set_ylabel("Congestion Speed trung bình")
            ax3.tick_params(axis='x', rotation=45)
            
            # Thêm số trên mỗi cột
            for bar in bars2:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9)
            
            st.pyplot(fig3)
            st.dataframe(speed_df, use_container_width=True)
    
    else:
        st.warning("Không tìm thấy cột thời tiết trong dataset. Vui lòng kiểm tra tên cột.")

    st.divider()

    # Day of week
    st.header("Congestion Speed theo ngày trong tuần")

    day_avg = df.groupby("day_of_week")["congestion_speed"].mean().reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    day_avg.plot(marker="o", ax=ax, linewidth=2, markersize=8)
    ax.set_title("Congestion Speed trung bình theo ngày trong tuần")
    ax.set_xlabel("Ngày")
    ax.set_ylabel("Congestion Speed trung bình")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    st.divider()

    # Hour
    st.header("Congestion Speed theo giờ trong ngày")

    hour_avg = df.groupby("hour")["congestion_speed"].mean()

    fig, ax = plt.subplots(figsize=(10, 4))
    hour_avg.plot(marker="o", ax=ax, linewidth=2, markersize=8, color='green')
    ax.set_title("Congestion Speed trung bình theo giờ (0–23)")
    ax.set_xlabel("Giờ")
    ax.set_ylabel("Congestion Speed trung bình")
    ax.grid(True, alpha=0.3)
    
    # Đánh dấu giờ cao điểm nếu có
    if not hour_avg.empty:
        min_hour = hour_avg.idxmin()
        max_hour = hour_avg.idxmax()
        ax.axvline(x=min_hour, color='red', linestyle='--', alpha=0.5, label=f'Thấp nhất: {min_hour}h')
        ax.axvline(x=max_hour, color='blue', linestyle='--', alpha=0.5, label=f'Cao nhất: {max_hour}h')
        ax.legend()
    
    st.pyplot(fig)
    
    # Hiển thị thống kê giờ
    hour_stats = pd.DataFrame({
        'Hour': hour_avg.index,
        'Avg Congestion Speed': hour_avg.values.round(2)
    }).sort_values('Avg Congestion Speed', ascending=False)
    
    st.subheader("Xếp hạng giờ theo Congestion Speed")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top 5 giờ cao nhất:**")
        st.dataframe(hour_stats.head(), use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**Top 5 giờ thấp nhất:**")
        st.dataframe(hour_stats.tail().iloc[::-1], use_container_width=True, hide_index=True)

else:
    st.info("Hãy tải CSV để xem Dashboard.")