import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

st.set_page_config(
    page_title="SPK Risiko Diabetes",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dataset studi kasus
@st.cache_data
def load_data():
    return pd.DataFrame([
        ["P01", 25, 21.5, 90, 110, 0, "Risiko Rendah"],
        ["P02", 30, 23.1, 95, 115, 0, "Risiko Rendah"],
        ["P03", 35, 25.0, 105, 120, 0, "Risiko Rendah"],
        ["P04", 40, 27.5, 120, 125, 1, "Risiko Tinggi"],
        ["P05", 45, 30.2, 140, 135, 1, "Risiko Tinggi"],
        ["P06", 50, 31.5, 155, 140, 1, "Risiko Tinggi"],
        ["P07", 55, 33.0, 165, 145, 1, "Risiko Tinggi"],
        ["P08", 28, 22.5, 92, 112, 0, "Risiko Rendah"],
        ["P09", 38, 26.8, 115, 122, 0, "Risiko Rendah"],
        ["P10", 48, 29.5, 145, 130, 1, "Risiko Tinggi"],
    ], columns=[
        "Pasien", "Usia", "BMI", "Glukosa", "Tekanan Darah",
        "Riwayat Keluarga", "Kelas"
    ])

data = load_data()
FITUR = ["Usia", "BMI", "Glukosa", "Tekanan Darah", "Riwayat Keluarga"]

# Memisahkan fitur dan target, kemudian menormalisasi data latihan.
X = data[FITUR]
y = data["Kelas"]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# Gaya monokrom: putih, abu-abu, dan hitam.
st.markdown("""
<style>
    .stApp { background: #f5f5f5; color: #202020; }
    .block-container { max-width: 860px; padding-top: 2.1rem; padding-bottom: 2.5rem; }
    h1 { font-size: 1.8rem !important; font-weight: 700 !important; color: #202020; }
    h2, h3 { color: #262626; }
    [data-testid="stHeader"] { background: transparent; }
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #d5d5d5;
        border-radius: 5px;
        padding: 1.25rem;
    }
    div.stButton > button, div[data-testid="stFormSubmitButton"] button {
        background: #292929;
        color: #ffffff;
        border: 1px solid #292929;
        border-radius: 4px;
        min-height: 42px;
        font-weight: 600;
    }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] button:hover {
        background: #444444;
        border-color: #444444;
        color: #ffffff;
    }
    [data-testid="stMetric"] { background: #fff; border: 1px solid #ddd; padding: 12px; }
    hr { border-color: #d2d2d2; }
    .eyebrow { font-size: .76rem; letter-spacing: .12em; font-weight: 700; color: #555; }
    .note { color: #595959; font-size: .84rem; line-height: 1.6; }
    div[data-testid="stExpander"] { border: 1px solid #d6d6d6; border-radius: 4px; }
    label { color: #292929 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">SISTEM PENDUKUNG KEPUTUSAN</div>', unsafe_allow_html=True)
st.title("Prediksi Risiko Diabetes")
st.caption("Klasifikasi menggunakan algoritma K-Nearest Neighbors (KNN)")
st.divider()

st.subheader("Input Data Pasien")
st.write("Lengkapi nilai berikut untuk menjalankan klasifikasi.")

with st.form("form_prediksi"):
    col1, col2 = st.columns(2)
    with col1:
        usia = st.number_input("Usia (tahun)", min_value=1, max_value=100, value=40, step=1)
        bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=28.0, step=0.1, format="%.1f")
        riwayat = st.selectbox(
            "Riwayat Diabetes dalam Keluarga",
            options=[0, 1],
            format_func=lambda x: "Tidak ada (0)" if x == 0 else "Ada (1)"
        )
    with col2:
        glukosa = st.number_input("Glukosa (mg/dL)", min_value=50, max_value=300, value=130, step=1)
        tekanan_darah = st.number_input("Tekanan Darah", min_value=80, max_value=200, value=128, step=1)
        k = st.selectbox("Nilai K (jumlah tetangga)", options=[1, 3, 5], index=1)
    submit = st.form_submit_button("Proses Prediksi", use_container_width=True)

if submit:
    input_data = pd.DataFrame(
        [[usia, bmi, glukosa, tekanan_darah, riwayat]],
        columns=FITUR
    )
    input_scaled = scaler.transform(input_data)

    model = KNeighborsClassifier(n_neighbors=int(k), metric="euclidean")
    model.fit(X_scaled, y)

    distances, indices = model.kneighbors(input_scaled, n_neighbors=int(k))
    hasil = model.predict(input_scaled)[0]

    neighbors = data.iloc[indices[0]].copy()
    neighbors["Jarak Euclidean"] = distances[0]
    jumlah_tinggi = int((neighbors["Kelas"] == "Risiko Tinggi").sum())
    jumlah_rendah = int((neighbors["Kelas"] == "Risiko Rendah").sum())

    st.divider()
    st.subheader("Hasil Klasifikasi")
    st.markdown(
        f"""<div style="background:#ededed;border:1px solid #bcbcbc;border-left:5px solid #292929;
        padding:16px 18px;margin:8px 0 14px;">
        <div style="font-size:12px;letter-spacing:.08em;color:#555;text-transform:uppercase;">Hasil prediksi</div>
        <div style="font-size:25px;font-weight:700;color:#202020;margin-top:5px;">{hasil}</div>
        </div>""",
        unsafe_allow_html=True
    )
    st.write(
        f"Berdasarkan **{k} tetangga terdekat**, terdapat "
        f"**{jumlah_tinggi} Risiko Tinggi** dan **{jumlah_rendah} Risiko Rendah**."
    )
    st.caption(f"Jarak Euclidean tetangga terdekat: {distances[0][0]:.4f}")

    with st.expander("Lihat data tetangga terdekat"):
        tampil = neighbors[[
            "Pasien", "Usia", "BMI", "Glukosa", "Tekanan Darah",
            "Riwayat Keluarga", "Kelas", "Jarak Euclidean"
        ]].copy()
        tampil["Jarak Euclidean"] = tampil["Jarak Euclidean"].round(4)
        st.dataframe(tampil, use_container_width=True, hide_index=True)

with st.expander("Lihat dataset latihan (10 data)"):
    st.caption("Data studi kasus yang digunakan sebagai data latihan model KNN.")
    st.dataframe(data, use_container_width=True, hide_index=True)

st.divider()
st.markdown("""
<div class="note">
Metode yang digunakan: StandardScaler, KNN, dan jarak Euclidean.
Dataset berisi 10 data studi kasus dan hanya digunakan untuk keperluan akademik.
Hasil klasifikasi bukan diagnosis medis.
</div>
""", unsafe_allow_html=True)
