
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Product SKU Generator", layout="centered")
st.title("🧾 Product SKU Generator")

if "records" not in st.session_state:
    st.session_state.records = []

def generate_sku(category_code, color_code, size_code, material_code):
    base = f"{category_code}-{color_code}-{size_code}-{material_code}"
    existing = [r for r in st.session_state.records if r["sku"].startswith(base)]
    serial = len(existing) + 1
    return f"{base}-{serial:03d}"

category_map = {"Bracelet": "BR", "Necklace": "NK", "Ring": "RL"}
color_map = {"Black": "BLK", "White": "WHT", "Red": "RED"}
size_map = {"Small": "S", "Medium": "M", "Large": "L"}
material_map = {"Stone": "ST", "Glass": "GL", "Silver": "SL"}

with st.form("sku_form"):
    col1, col2 = st.columns(2)
    category = col1.selectbox("Product Category", list(category_map.keys()))
    color = col2.selectbox("Color", list(color_map.keys()))
    size = col1.selectbox("Size", list(size_map.keys()))
    material = col2.selectbox("Material", list(material_map.keys()))
    submit = st.form_submit_button("➕ Generate SKU")

    if submit:
        sku = generate_sku(category_map[category], color_map[color], size_map[size], material_map[material])
        st.session_state.records.append({
            "sku": sku,
            "category": category,
            "color": color,
            "size": size,
            "material": material
        })
        st.success(f"SKU Generated: {sku}")

if st.session_state.records:
    st.subheader("📋 Generated SKUs")
    df = pd.DataFrame(st.session_state.records)

    for i, row in df.iterrows():
        cols = st.columns([3, 2, 2, 2, 2, 1, 1])
        for j, col in enumerate(["sku", "category", "color", "size", "material"]):
            cols[j].markdown(f"`{row[col]}`")

        if cols[5].button("✏️ Edit", key=f"edit_{i}"):
            with st.form(f"edit_form_{i}"):
                ec1, ec2 = st.columns(2)
                new_category = ec1.selectbox("Product Category", list(category_map.keys()), index=list(category_map.keys()).index(row["category"]))
                new_color = ec2.selectbox("Color", list(color_map.keys()), index=list(color_map.keys()).index(row["color"]))
                new_size = ec1.selectbox("Size", list(size_map.keys()), index=list(size_map.keys()).index(row["size"]))
                new_material = ec2.selectbox("Material", list(material_map.keys()), index=list(material_map.keys()).index(row["material"]))
                if st.form_submit_button("💾 Save Changes"):
                    st.session_state.records[i].update({
                        "category": new_category,
                        "color": new_color,
                        "size": new_size,
                        "material": new_material,
                        "sku": generate_sku(category_map[new_category], color_map[new_color], size_map[new_size], material_map[new_material])
                    })
                    st.experimental_rerun()

        if cols[6].button("🗑️ Delete", key=f"delete_{i}"):
            st.session_state.records.pop(i)
            st.experimental_rerun()

    excel_data = pd.DataFrame(st.session_state.records)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        excel_data.to_excel(writer, index=False)
    st.download_button("📥 Download Excel", data=buffer.getvalue(), file_name="sku_records.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("尚未產生任何 SKU。請從上方輸入資料。")
