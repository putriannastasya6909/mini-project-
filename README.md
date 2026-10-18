# Sistem Pendukung Keputusan Risiko Diabetes (KNN)

Aplikasi satu halaman berbasis Python dan Streamlit dengan desain monokrom. Dapat dijalankan di laptop atau dipublikasikan sebagai tautan `streamlit.app`.

## Isi project
- `app.py`: aplikasi utama.
- `requirements.txt`: library yang dibutuhkan saat deployment.

## Menjalankan di laptop
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Membuat link online di Streamlit Community Cloud
1. Ekstrak folder project ini.
2. Buat repository baru di GitHub, misalnya `spk-risiko-diabetes-knn`.
3. Unggah `app.py` dan `requirements.txt` ke bagian utama (root) repository.
4. Buka https://share.streamlit.io lalu masuk dengan akun yang terhubung ke GitHub.
5. Pilih **Create app** / **Deploy an app**.
6. Pilih repository tadi, branch `main`, dan file utama `app.py`.
7. Pada kolom App URL, usulkan nama seperti `spk-risiko-diabetes-putri` jika tersedia. Nama URL tidak dijamin tersedia.
8. Klik **Deploy**. Tunggu proses selesai dan buka URL `https://...streamlit.app` yang diberikan.

Setelah berhasil di-hosting, pengguna dapat membuka tautan HTTPS melalui browser HP/iPhone. Laptop pembuat tidak perlu hidup. Pengguna tetap memerlukan internet untuk membuka aplikasi online.

## Catatan privasi dan akademik
Jika repository dibuat publik, kode aplikasi dapat dilihat orang lain. Jangan mengunggah data pasien asli, kata sandi, atau informasi pribadi. Dataset berisi 10 contoh studi kasus dan hasilnya bukan diagnosis medis.
