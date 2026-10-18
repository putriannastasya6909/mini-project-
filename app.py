import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

data = pd.DataFrame([
    ["P01",25,21.5,90,110,0,"Risiko Rendah"],
    ["P02",30,23.1,95,115,0,"Risiko Rendah"],
    ["P03",35,25.0,105,120,0,"Risiko Rendah"],
    ["P04",40,27.5,120,125,1,"Risiko Tinggi"],
    ["P05",45,30.2,140,135,1,"Risiko Tinggi"],
    ["P06",50,31.5,155,140,1,"Risiko Tinggi"],
    ["P07",55,33.0,165,145,1,"Risiko Tinggi"],
    ["P08",28,22.5,92,112,0,"Risiko Rendah"],
    ["P09",38,26.8,115,122,0,"Risiko Rendah"],
    ["P10",48,29.5,145,130,1,"Risiko Tinggi"],
], columns=["Pasien","Usia","BMI","Glukosa","Tekanan Darah","Riwayat Keluarga","Kelas"])

FITUR = ["Usia","BMI","Glukosa","Tekanan Darah","Riwayat Keluarga"]
X = data[FITUR]
y = data["Kelas"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = KNeighborsClassifier(n_neighbors=3, metric="euclidean")
model.fit(X_scaled, y)

st.set_page_config(page_title="SPK Risiko Diabetes", layout="centered")

st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}
.block-container {max-width:900px; padding-top:2.5rem; padding-bottom:3rem;}
.judul {border-bottom:2px solid #1f4e79; padding-bottom:14px; margin-bottom:28px;}
.judul h1 {font-size:30px; margin-bottom:6px; color:#1f2937; font-weight:650;}
.judul p {color:#64748b; font-size:15px; margin:0;}
.bagian {color:#1f2937; font-size:21px; font-weight:600; margin-bottom:5px;}
.keterangan {color:#64748b; font-size:14px; margin-bottom:18px;}
div.stButton > button {width:100%; background:#1f4e79; color:white; border:none; border-radius:5px; height:44px; font-size:15px; font-weight:600;}
div.stButton > button:hover {background:#173a5c; color:white;}
.hasil-rendah,.hasil-tinggi {padding:18px 20px; border-radius:5px; margin-top:25px;}
.hasil-rendah {border:1px solid #86a98b; border-left:5px solid #4d7c52; background:#f6faf6;}
.hasil-tinggi {border:1px solid #c78d8d; border-left:5px solid #a63d40; background:#fff8f8;}
.hasil-label {font-size:14px; color:#64748b; margin-bottom:5px;}
.hasil-nilai {font-size:25px; font-weight:650; color:#1f2937;}
.catatan {margin-top:25px; padding-top:15px; border-top:1px solid #e2e8f0; color:#64748b; font-size:13px; line-height:1.6;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="judul">
<h1>Sistem Pendukung Keputusan Risiko Diabetes</h1>
<p>Klasifikasi risiko diabetes menggunakan algoritma K-Nearest Neighbors (KNN)</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="bagian">Input Data Pasien</div>', unsafe_allow_html=True)
st.markdown('<div class="keterangan">Masukkan nilai pasien untuk mendapatkan hasil klasifikasi risiko.</div>', unsafe_allow_html=True)

kiri, kanan = st.columns(2)
with kiri:
    usia = st.number_input("Usia (tahun)", min_value=1, max_value=120, value=42, step=1)
    bmi = st.number_input("BMI", min_value=1.0, max_value=80.0, value=28.5, step=0.1, format="%.1f")
    glukosa = st.number_input("Glukosa", min_value=1, max_value=500, value=130, step=1)
with kanan:
    tekanan = st.number_input("Tekanan Darah", min_value=1, max_value=300, value=128, step=1)
    riwayat = st.selectbox("Riwayat Diabetes dalam Keluarga", [0,1], format_func=lambda x: "Tidak Ada (0)" if x == 0 else "Ada (1)")

st.write("")

if st.button("Prediksi Risiko"):
    pasien = pd.DataFrame([[usia,bmi,glukosa,tekanan,riwayat]], columns=FITUR)
    pasien_scaled = scaler.transform(pasien)
    hasil = model.predict(pasien_scaled)[0]
    jarak, indeks = model.kneighbors(pasien_scaled, n_neighbors=3)
    tetangga = data.iloc[indeks[0]].copy()
    tetangga["Jarak"] = jarak[0]

    if hasil == "Risiko Tinggi":
        st.markdown(f'<div class="hasil-tinggi"><div class="hasil-label">Hasil Klasifikasi</div><div class="hasil-nilai">{hasil}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="hasil-rendah"><div class="hasil-label">Hasil Klasifikasi</div><div class="hasil-nilai">{hasil}</div></div>', unsafe_allow_html=True)

    tinggi = int((tetangga["Kelas"] == "Risiko Tinggi").sum())
    rendah = int((tetangga["Kelas"] == "Risiko Rendah").sum())
    st.write(f"Hasil diperoleh dari 3 data pasien terdekat: {tinggi} Risiko Tinggi dan {rendah} Risiko Rendah.")

    with st.expander("Lihat 3 data pasien terdekat"):
        tampil = tetangga[["Pasien","Usia","BMI","Glukosa","Tekanan Darah","Kelas","Jarak"]].copy()
        tampil["Jarak"] = tampil["Jarak"].round(4)
        st.dataframe(tampil, use_container_width=True, hide_index=True)

st.markdown("""
<div class="catatan">
Metode: K-Nearest Neighbors (KNN), K = 3, jarak Euclidean, dan normalisasi StandardScaler.<br>
Catatan: sistem ini merupakan implementasi akademik berdasarkan dataset studi kasus dan bukan alat diagnosis medis.
</div>
""", unsafe_allow_html=True)
