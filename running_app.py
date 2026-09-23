import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# === ตั้งค่าหน้าแอป ===
st.set_page_config(page_title="แอปติดตามการวิ่ง", page_icon="🏃", layout="wide")
st.title("🏃 แอปวัดและติดตามระยะทางการวิ่ง")

# === ไฟล์เก็บข้อมูล ===
DATA_FILE = "running_data.csv"

# สร้างไฟล์ถ้ายังไม่มี
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["วันที่", "ระยะทาง_กม", "ชม", "นาที", "วินาที", "เวลารวม_นาที", "พซเรท_นาทีต่อกม"])
    df.to_csv(DATA_FILE, index=False)

# === โหลดข้อมูล ===
def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(วันที่, ระยะ, ชม, นาที, วินาที):
    เวลารวม_นาที = ชม*60 + นาที + วินาที/60
    พซเรท = เวลารวม_นาที / ระยะ if ระยะ > 0 else 0
    
    df = load_data()
    new_row = {
        "วันที่": วันที่,
        "ระยะทาง_กม": ระยะ,
        "ชม": ชม,
        "นาที": นาที,
        "วินาที": วินาที,
        "เวลารวม_นาที": round(เวลารวม_นาที, 2),
        "พซเรท_นาทีต่อกม": round(พซเรท, 2)
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return พซเรท, เวลารวม_นาที

# === เมนู ===
menu = st.sidebar.selectbox("เลือกเมนู", ["บันทึกผลวิ่ง", "ประวัติ & สถิติ", "คำนวณเป้าหมาย"])

# === หน้า 1: บันทึกผล ===
if menu == "บันทึกผลวิ่ง":
    st.subheader("✏️ บันทึกผลการวิ่ง")
    
    col1, col2 = st.columns(2)
    with col1:
        วันที่ = st.date_input("วันที่", datetime.today())
        ระยะ = st.number_input("ระยะทาง (กิโลเมตร)", min_value=0.01, step=0.01, format="%.2f")
    
    with col2:
        ชม = st.number_input("ชั่วโมง", min_value=0, max_value=24, value=0)
        นาที = st.number_input("นาที", min_value=0, max_value=59, value=30)
        วินาที = st.number_input("วินาที", min_value=0, max_value=59, value=0)
    
    if st.button("✅ บันทึก", type="primary"):
        พซเรท, เวลารวม = save_data(วันที่, ระยะ, ชม, นาที, วินาที)
        น_พซ = int(พซเรท)
        วิ_พซ = round((พซเรท - น_พซ) * 60)
        
        st.success("บันทึกสำเร็จ! 🎉")
        st.info(f"""
        📊 ผลลัพธ์:
        - ระยะทาง: {ระยะ:.2f} กม.
        - เวลารวม: {ชม}:{นาที:02d}:{วินาที:02d}
        - พซเรท: **{น_พซ}:{วิ_พซ:02d} / กม.**
        """)

# === หน้า 2: ประวัติ & กราฟ ===
elif menu == "ประวัติ & สถิติ":
    df = load_data()
    st.subheader("📋 ประวัติการวิ่งทั้งหมด")
    
    if df.empty:
        st.info("ยังไม่มีข้อมูล เริ่มบันทึกการวิ่งกันเลย!")
    else:
        st.dataframe(df, use_container_width=True)
        
        # สรุปผล
        รวมระยะ = df["ระยะทาง_กม"].sum()
        เฉลี่ยพซเรท = df["พซเรท_นาทีต่อกม"].mean()
        st.metric("📏 รวมระยะทั้งหมด", f"{รวมระยะ:.2f} กม.")
        st.metric("⏱️ พซเรทเฉลี่ย", f"{เฉลี่ยพซเรท:.2f} นาที/กม")
        
        # กราฟ
        st.subheader("📈 ความก้าวหน้าพซเรท")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df["วันที่"], df["พซเรท_นาทีต่อกม"], marker='o', color='#FF4B4B', linewidth=2)
        ax.set_ylabel("นาทีต่อกม.")
        ax.set_xlabel("วันที่")
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)

# === หน้า 3: คำนวณเป้าหมาย ===
elif menu == "คำนวณเป้าหมาย":
    st.subheader("🎯 คำนวณเวลาจบเป้าหมาย")
    
    col1, col2 = st.columns(2)
    with col1:
        เป้าหมาย_ระยะ = st.number_input("ระยะเป้าหมาย (กม)", min_value=0.1, value=10.0)
    with col2:
        พซเรท_น = st.number_input("พซเรท (นาที/กม)", min_value=1, max_value=30, value=6)
        พซเรท_วิ = st.number_input("วินาที/กม", min_value=0, max_value=59, value=0)
    
    if st.button("คำนวณ", type="primary"):
        พซเรทรวม = พซเรท_น + พซเรท_วิ/60
        เวลารวม_นาที = พซเรทรวม * เป้าหมาย_ระยะ
        ชม = int(เวลารวม_นาที // 60)
        นาที = int(เวลารวม_นาที % 60)
        วินาที = round((เวลารวม_นาที - int(เวลารวม_นาที)) * 60)
        
        st.success(f"""
        ⏱️ เวลาที่คาดว่าจะจบ {เป้าหมาย_ระยะ:.1f} กม.:
        # {ชม} ชม. {นาที} นาที {วินาที} วินาที
        = {ชม}:{นาที:02d}:{วินาที:02d}
        """)