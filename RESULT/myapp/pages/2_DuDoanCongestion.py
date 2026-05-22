import streamlit as st
import numpy as np
import xgboost as xgb
import torch
import torch.nn as nn

xgb_model = xgb.XGBClassifier()
xgb_model.load_model("models/xgb_model.json")

class DynamicMLP(nn.Module):
    def __init__(self, input_dim, num_classes, hidden_dims, dropout_rate):
        super(DynamicMLP, self).__init__()
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.SiLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        layers.append(nn.Linear(prev_dim, num_classes))
        self.net = nn.Sequential(*layers)
    def forward(self, x):
        return self.net(x)

params = {'hidden_dims': [1024, 512, 256, 128], 'dropout': 0.01}
INPUT_DIM = 28
NUM_CLASSES = 3

mlp_model = DynamicMLP(input_dim=INPUT_DIM, num_classes=NUM_CLASSES,
                       hidden_dims=params['hidden_dims'], dropout_rate=params['dropout'])
mlp_model.load_state_dict(torch.load("models/best_mlp.pth", map_location="cpu"))
mlp_model.eval()

st.title("Dự đoán mức độ tắc nghẽn")
model_choice = st.selectbox("Chọn mô hình dự đoán", ["XGBoost", "MLP (PyTorch)"])
st.write("Nhập dữ liệu cho mô hình dự đoán")

feature_names = [
    "start_lat","start_lng","weather_conditions","fog","rain","snow","hail",
    "thunderstorm","tornado","severity","distance_mi",
    "delayfromfreeflowspeed_mins","delayfromtypicaltraffic_mins",
    "delay_ratio","delay_per_mile","dist_freeflow",
    "starttime_year","starttime_month","starttime_day","starttime_hour",
    "starttime_minute","starttime_second",
    "endtime_year","endtime_month","endtime_day","endtime_hour",
    "endtime_minute","endtime_second"
]


inputs = {}
cols = st.columns(8)
col_idx = 0
for i, fname in enumerate(feature_names):
    c = cols[col_idx]
    default_val = 0.0
    inputs[fname] = c.number_input(fname, value=float(default_val))
    col_idx = (col_idx + 1) % len(cols)

X_list = [inputs[f] for f in feature_names]
X = np.array([X_list], dtype=float)

st.write(f"Expected model input dim: {INPUT_DIM}, Your input shape: {X.shape[1]}")

if st.button("Predict"):
    if X.shape[1] != INPUT_DIM:
        st.error(f"Feature shape mismatch: model expects {INPUT_DIM} features but input has {X.shape[1]}.")
    else:
        labels = {0: "Tắc nghẽn nặng", 1: "Tắc nghẽn trung bình", 2: "Tắc nghẽn nhẹ"}
        st.subheader(" Kết quả dự đoán")

        if model_choice == "XGBoost":
            try:
                pred_xgb = xgb_model.predict(X)[0]
                st.write(f"**XGBoost:** {labels[pred_xgb]}")
            except Exception as e:
                st.error(f"XGBoost prediction error: {e}")

        if model_choice == "MLP (PyTorch)":
            try:
                with torch.no_grad():
                    tensor_x = torch.tensor(X, dtype=torch.float32)
                    logits = mlp_model(tensor_x)
                    pred_mlp = torch.argmax(logits, dim=1).numpy()[0]
                st.write(f"**MLP (PyTorch):** {labels[pred_mlp]}")
            except Exception as e:
                st.error(f"MLP prediction error: {e}")
