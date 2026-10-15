import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

@st.cache_data
def load_data():
    return pd.DataFrame([
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

data = load_data()
FITUR = ["Usia", "BMI", "Glukosa", "Tekanan Darah", "Riwayat Keluarga"]
X, y = data[FITUR], data["Kelas"]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

st.set_page_config(page_title="SPK Risiko Diabetes", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.block-container{max-width:880px;padding-top:2rem;padding-bottom:2rem}
h1{font-size:1.85rem!important;color:#1f2937;margin-bottom:.25rem}
h2,h3{color:#26384a}
div[data-testid="stForm"]{border:1px solid #d9dee5;border-radius:8px;padding:1.1rem;background:white}
div[data-testid="stFormSubmitButton"] button{background:#24476b;color:white;border:1px solid #24476b;border-radius:5px;font-weight:600;min-height:42px}
div[data-testid="stFormSubmitButton"] button:hover{background:#193653;color:white;border-color:#193653}
</style>
""", unsafe_allow_html=True)

st.title("Sistem Pendukung Keputusan Risiko Diabetes")
st.caption("Klasifikasi menggunakan algoritma K-Nearest Neighbors (KNN)")
st.divider()
st.subheader("Input Data Pasien")
st.write("Masukkan nilai pasien, lalu tekan tombol prediksi.")

with st.form("form_prediksi"):
    c1, c2 = st.columns(2)
    with c1:
        usia = st.number_input("Usia (tahun)", 1, 100, 40, step=1)
        bmi = st.number_input("BMI", 10.0, 50.0, 28.0, step=0.1, format="%.1f")
        riwayat = st.selectbox("Riwayat Diabetes dalam Keluarga", [0, 1], format_func=lambda x: "Tidak ada (0)" if x == 0 else "Ada (1)")
    with c2:
        glukosa = st.number_input("Glukosa (mg/dL)", 50, 300, 130, step=1)
        td = st.number_input("Tekanan Darah", 80, 200, 128, step=1)
        k = st.selectbox("Nilai K (jumlah tetangga)", [1, 3, 5], index=1)
    submit = st.form_submit_button("Prediksi Risiko", use_container_width=True)

if submit:
    input_data = pd.DataFrame([[usia, bmi, glukosa, td, riwayat]], columns=FITUR)
    input_scaled = scaler.transform(input_data)
    model = KNeighborsClassifier(n_neighbors=int(k), metric="euclidean")
    model.fit(X_scaled, y)
    distances, indices = model.kneighbors(input_scaled, n_neighbors=int(k))
    hasil = model.predict(input_scaled)[0]
    neighbors = data.iloc[indices[0]].copy()
    neighbors["Jarak Euclidean"] = distances[0]
    tinggi = int((neighbors["Kelas"] == "Risiko Tinggi").sum())
    rendah = int((neighbors["Kelas"] == "Risiko Rendah").sum())
    st.subheader("Hasil Klasifikasi")
    if hasil == "Risiko Tinggi":
        st.error(f"**{hasil}**")
    else:
        st.success(f"**{hasil}**")
    st.write(f"Dari {k} tetangga terdekat: **{tinggi} Risiko Tinggi** dan **{rendah} Risiko Rendah**.")
    st.caption(f"Jarak tetangga terdekat: {distances[0][0]:.4f}")
    with st.expander("Lihat data tetangga terdekat"):
        shown = neighbors[["Pasien","Usia","BMI","Glukosa","Tekanan Darah","Riwayat Keluarga","Kelas","Jarak Euclidean"]].copy()
        shown["Jarak Euclidean"] = shown["Jarak Euclidean"].round(4)
        st.dataframe(shown, use_container_width=True, hide_index=True)

st.divider()
with st.expander("Lihat dataset latihan (10 data)"):
    st.caption("Dataset studi kasus yang dipakai untuk membentuk model KNN.")
    st.dataframe(data, use_container_width=True, hide_index=True)
st.caption("Metode: StandardScaler, KNN, dan jarak Euclidean. Dataset merupakan contoh studi kasus akademik, bukan alat diagnosis medis.")
