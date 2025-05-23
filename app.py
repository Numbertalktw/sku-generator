import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO

st.set_page_config(page_title="Product SKU Generator", layout="centered")
st.title("🧾 Product SKU Generator")

# === Google Sheets 連接設定 ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/1AzJ6IJayXV7yooFJyWRhDvD0cDGWTexl_hjjtVF4JGs"
SHEET_NAME_MAP = {
    "category": "商品類別",
    "color": "顏色",
    "size": "尺寸",
    "material": "材質"
}

@st.cache_data(show_spinner=False)
def load_dropdown_options():
    # 設定 Google Sheets API 權限（使用 public sheet URL）
    sheet_id = SHEET_URL.split("/")[5]
    base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="

    options = {}
    for key, sheet_name in SHEET_NAME_MAP.items():
        url = base_url + sheet_name
        try:
            df = pd.read_csv(url)
            options[key] = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))  # 名稱對應代碼
        except Exception as e:
            st.warning(f"⚠️ 無法讀取表單：{sheet_name}，請檢查格式與權限。")
            options[key] = {}
    return options

options = load_dropdown_options()

if "records" not in st.session_state:
    st.session_state.records = []

def generate_sku(category_code, color_code, size_code, material_code):
    base = f"{category_code}-{color_code}-{size_code}-{material_code}"
    existing = [r for r in st.session_state.records if r["sku"].startswith(base)]
    serial = len(existing) + 1
    return f"{base}-{serial:03d}"

with st.form("sku_form"):
    col1, col2 = st.columns(2)
    category = col1.selectbox("商品類別", list(options["category"].keys()))
    color = col2.selectbox("顏色", list(options["color"].keys()))
    size = col1.selectbox("尺寸", list(options["size"].keys()))
    material = col2.selectbox("材質", list(options["material"].keys()))
    submit = st.form_submit_button("➕ 產生 SKU")

    if submit:
        sku = generate_sku(options["category"][category], options["color"][color], options["size"][size], options["material"][material])
        st.session_state.records.append({
            "sku": sku,
            "category": category,
            "color": color,
            "size": size,
            "material": material
        })
        st.success(f"SKU 產生成功：{sku}")

if st.session_state.records:
    st.subheader("📋 已產生的 SKU")
    df = pd.DataFrame(st.session_state.records)

    for i, row in df.iterrows():
        cols = st.columns([3, 2, 2, 2, 2, 1, 1])
        for j, col in enumerate(["sku", "category", "color", "size", "material"]):
            cols[j].markdown(f"`{row[col]}`")

        if cols[5].button("✏️ 編輯", key=f"edit_{i}"):
            with st.form(f"edit_form_{i}"):
                ec1, ec2 = st.columns(2)
                new_category = ec1.selectbox("商品類別", list(options["category"].keys()), index=list(options["category"].keys()).index(row["category"]))
                new_color = ec2.selectbox("顏色", list(options["color"].keys()), index=list(options["color"].keys()).index(row["color"]))
                new_size = ec1.selectbox("尺寸", list(options["size"].keys()), index=list(options["size"].keys()).index(row["size"]))
                new_material = ec2.selectbox("材質", list(options["material"].keys()), index=list(options["material"].keys()).index(row["material"]))
                if st.form_submit_button("💾 儲存變更"):
                    st.session_state.records[i].update({
                        "category": new_category,
                        "color": new_color,
                        "size": new_size,
                        "material": new_material,
                        "sku": generate_sku(options["category"][new_category], options["color"][new_color], options["size"][new_size], options["material"][new_material])
                    })
                    st.experimental_rerun()

        if cols[6].button("🗑️ 刪除", key=f"delete_{i}"):
            st.session_state.records.pop(i)
            st.experimental_rerun()

    excel_data = pd.DataFrame(st.session_state.records)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        excel_data.to_excel(writer, index=False)
    st.download_button("📥 匯出 Excel", data=buffer.getvalue(), file_name="sku_records.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("目前尚未產生 SKU。請先選擇資料並點選上方按鈕。")
