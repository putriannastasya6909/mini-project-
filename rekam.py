import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

# Sesuaikan jika konfigurasi MySQL di komputer berbeda.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_rekam_medis",
}

LEBAR_LABEL = 34
UNSET = object()
GARIS = "=" * 78
GARIS_TIPIS = "-" * 78


# ========================= TAMPILAN & INPUT =========================
def judul(teks):
    """Judul utama dengan garis pembatas seperti tampilan terminal referensi."""
    print("\n" + GARIS)
    print(teks.center(78))
    print(GARIS)


def subjudul(teks):
    """Judul bagian: garis tegas di atas dan garis tipis di bawah."""
    print("\n" + GARIS)
    print(teks.center(78))
    print(GARIS_TIPIS)


def tampil(nilai):
    if nilai is None or nilai == "":
        return "-"
    if isinstance(nilai, datetime):
        return nilai.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(nilai, date):
        return nilai.strftime("%Y-%m-%d")
    return str(nilai)


def input_teks(label, default=UNSET, wajib=False, boleh_kosong=True):
    """Input teks dengan label dan titik dua sejajar.

    Saat mengubah data: Enter mempertahankan nilai lama.
    Tanda '-' mengosongkan kolom hanya jika kolom memang boleh kosong.
    """
    while True:
        awalan = f"{label:<{LEBAR_LABEL}} : "
        if default is not UNSET:
            awalan += f"[{tampil(default)}] "
        nilai = input(awalan).strip()

        if default is not UNSET and nilai == "":
            return default
        if nilai == "-":
            if boleh_kosong and not wajib:
                return None
            print("  Kolom ini wajib diisi dan tidak boleh dikosongkan.")
            continue
        if nilai == "":
            if wajib:
                print("  Kolom ini wajib diisi.")
                continue
            return None
        return nilai


def input_tanggal(label, default=UNSET, wajib=False, dengan_waktu=False):
    """Input tanggal atau tanggal-waktu dengan validasi dan format seragam."""
    format_tanggal = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M") if dengan_waktu else ("%Y-%m-%d",)
    contoh = "YYYY-MM-DD HH:MM atau YYYY-MM-DD HH:MM:SS" if dengan_waktu else "YYYY-MM-DD"

    while True:
        awalan = f"{label:<{LEBAR_LABEL}} : "
        if default is not UNSET:
            awalan += f"[{tampil(default)}] "
        nilai = input(awalan).strip()

        if default is not UNSET and nilai == "":
            if default is None:
                return None
            nilai_lama = tampil(default)
            # Ubah bentuk tanggal Python menjadi string yang diterima MySQL.
            for fmt in format_tanggal:
                try:
                    return datetime.strptime(nilai_lama, fmt).strftime(
                        "%Y-%m-%d %H:%M:%S" if dengan_waktu else "%Y-%m-%d"
                    )
                except ValueError:
                    continue
            return nilai_lama

        if nilai == "-":
            if not wajib:
                return None
            print("  Kolom ini wajib diisi dan tidak boleh dikosongkan.")
            continue
        if nilai == "":
            if wajib:
                print("  Kolom ini wajib diisi.")
                continue
            return None

        for fmt in format_tanggal:
            try:
                hasil = datetime.strptime(nilai, fmt)
                return hasil.strftime("%Y-%m-%d %H:%M:%S" if dengan_waktu else "%Y-%m-%d")
            except ValueError:
                continue
        print(f"  Format tanggal salah. Gunakan {contoh}.")


def input_angka(label, default=UNSET):
    while True:
        awalan = f"{label:<{LEBAR_LABEL}} : "
        if default is not UNSET:
            awalan += f"[{tampil(default)}] "
        nilai = input(awalan).strip()
        if default is not UNSET and nilai == "":
            return float(default)
        if nilai == "":
            print("  Nilai angka wajib diisi.")
            continue
        try:
            return float(nilai.replace(",", "."))
        except ValueError:
            print("  Masukkan angka yang benar, misalnya 14.4.")


def konfirmasi(pesan):
    """Konfirmasi selalu menggunakan jawaban ya/tidak."""
    while True:
        jawaban = input(f"{pesan} (ya/tidak): ").strip().lower()
        if jawaban == "ya":
            return True
        if jawaban == "tidak":
            return False
        print("  Jawaban harus 'ya' atau 'tidak'.")


def petunjuk_edit():
    print("Petunjuk: tekan Enter untuk mempertahankan nilai lama.")
    print("          Ketik '-' untuk mengosongkan kolom yang boleh kosong.\n")


def koneksi_database():
    return mysql.connector.connect(**DB_CONFIG)


def ambil_satu(cursor, sql, parameter=()):
    cursor.execute(sql, parameter)
    return cursor.fetchone()


def ambil_banyak(cursor, sql, parameter=()):
    cursor.execute(sql, parameter)
    return cursor.fetchall()


# ========================= PASIEN & KUNJUNGAN =========================
def cari_pasien(cursor, no_rm):
    return ambil_satu(cursor, "SELECT * FROM pasien WHERE no_rm = %s", (no_rm,))


def tampilkan_pasien(pasien):
    subjudul("DATA PASIEN")
    print(f"{'No. RM':<{LEBAR_LABEL}} : {tampil(pasien['no_rm'])}")
    print(f"{'Nama pasien':<{LEBAR_LABEL}} : {tampil(pasien['nama_pasien'])}")
    print(f"{'Tanggal lahir':<{LEBAR_LABEL}} : {tampil(pasien['tanggal_lahir'])}")
    print(f"{'Jenis kelamin':<{LEBAR_LABEL}} : {tampil(pasien['jenis_kelamin'])}")
    print(f"{'Alamat':<{LEBAR_LABEL}} : {tampil(pasien['alamat'])}")


def daftar_kunjungan(cursor, id_pasien):
    daftar = ambil_banyak(
        cursor,
        """SELECT k.id_kunjungan, k.kode_kunjungan, k.tanggal_kunjungan,
                  k.jenis_kunjungan, d.nama_dokter
           FROM kunjungan k
           LEFT JOIN dokter d ON d.id_dokter = k.id_dokter
           WHERE k.id_pasien = %s
           ORDER BY k.tanggal_kunjungan DESC""",
        (id_pasien,),
    )
    if not daftar:
        print("Belum ada data kunjungan untuk pasien ini.")
        return []

    subjudul("DAFTAR KUNJUNGAN")
    for nomor, row in enumerate(daftar, start=1):
        print(f"{nomor}. {row['kode_kunjungan']} | {tampil(row['tanggal_kunjungan'])}")
        print(f"   Jenis  : {row['jenis_kunjungan']}")
        print(f"   Dokter : {row['nama_dokter'] or '-'}")
    return daftar


def pilih_kunjungan(cursor, pasien):
    daftar = daftar_kunjungan(cursor, pasien["id_pasien"])
    if not daftar:
        return None
    while True:
        pilihan = input("Pilih nomor kunjungan (0 untuk batal) : ").strip()
        if pilihan == "0":
            return None
        if pilihan.isdigit() and 1 <= int(pilihan) <= len(daftar):
            return daftar[int(pilihan) - 1]
        print("Pilihan tidak valid.")


def pilih_pasien(cursor):
    subjudul("CARI PASIEN")
    no_rm = input_teks("No. RM pasien", wajib=True)
    pasien = cari_pasien(cursor, no_rm)
    if not pasien:
        print("Pasien dengan No. RM tersebut tidak ditemukan.")
        return None
    return pasien


def tampilkan_ringkasan_kunjungan(cursor, pasien, kunjungan):
    tampilkan_pasien(pasien)
    subjudul("DATA KUNJUNGAN")
    print(f"{'Kode kunjungan':<{LEBAR_LABEL}} : {kunjungan['kode_kunjungan']}")
    print(f"{'Tanggal kunjungan':<{LEBAR_LABEL}} : {tampil(kunjungan['tanggal_kunjungan'])}")
    print(f"{'Jenis kunjungan':<{LEBAR_LABEL}} : {kunjungan['jenis_kunjungan']}")
    print(f"{'Dokter':<{LEBAR_LABEL}} : {kunjungan['nama_dokter'] or '-'}")

    soap = ambil_satu(
        cursor,
        "SELECT subjective, objective, asesmen, plan FROM rekam_medis WHERE id_kunjungan = %s",
        (kunjungan["id_kunjungan"],),
    )
    subjudul("CATATAN SOAP")
    if not soap:
        print("Belum ada catatan SOAP.")
    else:
        print(f"S - Subjective : {soap['subjective'] or '-'}")
        print(f"O - Objective  : {soap['objective'] or '-'}")
        print(f"A - Asesmen    : {soap['asesmen'] or '-'}")
        print(f"P - Plan        : {soap['plan'] or '-'}")

    pemeriksaan = ambil_banyak(
        cursor,
        """SELECT * FROM pemeriksaan WHERE id_kunjungan = %s
           ORDER BY tanggal_pemeriksaan, id_pemeriksaan""",
        (kunjungan["id_kunjungan"],),
    )
    subjudul("PEMERIKSAAN PENUNJANG")
    if not pemeriksaan:
        print("Belum ada data pemeriksaan.")
    for p in pemeriksaan:
        print(f"\nID pemeriksaan : {p['id_pemeriksaan']}")
        print(f"{'Jenis pemeriksaan':<{LEBAR_LABEL}} : {p['jenis_pemeriksaan']}")
        print(f"{'Nama pemeriksaan':<{LEBAR_LABEL}} : {p['nama_pemeriksaan']}")
        print(f"{'Tanggal pemeriksaan':<{LEBAR_LABEL}} : {tampil(p['tanggal_pemeriksaan'])}")
        print(f"{'Hasil pemeriksaan':<{LEBAR_LABEL}} : {p['hasil_pemeriksaan'] or '-'}")
        print(f"{'Kesimpulan':<{LEBAR_LABEL}} : {p['kesimpulan'] or '-'}")

        detail = ambil_banyak(
            cursor,
            """SELECT parameter, nilai, satuan, nilai_rujukan
               FROM detail_pemeriksaan WHERE id_pemeriksaan = %s ORDER BY id_detail""",
            (p["id_pemeriksaan"],),
        )
        if detail:
            print("  Detail parameter:")
            for item in detail:
                satuan = f" {item['satuan']}" if item["satuan"] else ""
                print(f"    - {item['parameter']}: {item['nilai']}{satuan} | Rujukan: {item['nilai_rujukan'] or '-'}")

    dokumen = ambil_banyak(
        cursor,
        """SELECT id_dokumen, id_pemeriksaan, jenis_dokumen, nama_dokumen,
                  nomor_dokumen, tanggal_dokumen, status_validasi
           FROM dokumen_pendukung WHERE id_kunjungan = %s
           ORDER BY tanggal_dokumen, id_dokumen""",
        (kunjungan["id_kunjungan"],),
    )
    subjudul("DOKUMEN PENDUKUNG")
    if not dokumen:
        print("Belum ada dokumen pendukung.")
    for dok in dokumen:
        print(f"{'ID dokumen':<{LEBAR_LABEL}} : {dok['id_dokumen']}")
        print(f"{'Jenis dokumen':<{LEBAR_LABEL}} : {dok['jenis_dokumen']}")
        print(f"{'Nama dokumen':<{LEBAR_LABEL}} : {dok['nama_dokumen']}")
        print(f"{'Nomor dokumen':<{LEBAR_LABEL}} : {dok['nomor_dokumen'] or '-'}")
        print(f"{'Tanggal dokumen':<{LEBAR_LABEL}} : {tampil(dok['tanggal_dokumen'])}")
        print(f"{'Status validasi':<{LEBAR_LABEL}} : {dok['status_validasi']}")
        print(f"{'ID pemeriksaan':<{LEBAR_LABEL}} : {dok['id_pemeriksaan'] or '-'}")
        print(GARIS_TIPIS)


# ========================= MENU 1: LIHAT DATA =========================
def lihat_data(cursor):
    pasien = pilih_pasien(cursor)
    if not pasien:
        return
    while True:
        kunjungan = pilih_kunjungan(cursor, pasien)
        if not kunjungan:
            return
        lengkap = ambil_satu(
            cursor,
            """SELECT k.*, d.nama_dokter FROM kunjungan k
               LEFT JOIN dokter d ON d.id_dokter = k.id_dokter
               WHERE k.id_kunjungan = %s""",
            (kunjungan["id_kunjungan"],),
        )
        tampilkan_ringkasan_kunjungan(cursor, pasien, lengkap)
        if not konfirmasi("Lihat kunjungan lain dari pasien ini?"):
            break


# ========================= MENU 2: TAMBAH DATA =========================
def pilih_dokter(cursor):
    dokter = ambil_banyak(
        cursor,
        "SELECT id_dokter, kode_dokter, nama_dokter, spesialisasi FROM dokter ORDER BY nama_dokter",
    )
    subjudul("PILIH DOKTER")
    print("0. Dokter belum ditentukan")
    for nomor, d in enumerate(dokter, start=1):
        print(f"{nomor}. {d['kode_dokter']} | {d['nama_dokter']} | {d['spesialisasi']}")
    while True:
        pilihan = input("Pilih nomor dokter (0 jika belum ditentukan) : ").strip()
        if pilihan == "0":
            return None
        if pilihan.isdigit() and 1 <= int(pilihan) <= len(dokter):
            return dokter[int(pilihan) - 1]["id_dokter"]
        print("Pilihan tidak valid.")


def buat_kode_kunjungan(cursor, tanggal_waktu):
    tanggal = tanggal_waktu[:10].replace("-", "")
    awalan = f"KJ-{tanggal}-"
    nomor = 1
    while True:
        kode = f"{awalan}{nomor:03d}"
        if not ambil_satu(cursor, "SELECT id_kunjungan FROM kunjungan WHERE kode_kunjungan = %s", (kode,)):
            return kode
        nomor += 1


def tambah_soap(cursor, id_kunjungan):
    if not konfirmasi("Tambahkan catatan SOAP untuk kunjungan ini?"):
        return
    subjudul("INPUT CATATAN SOAP")
    print("Bagian yang belum tersedia boleh dikosongkan.")
    subjective = input_teks("S - Subjective", wajib=False)
    objective = input_teks("O - Objective", wajib=False)
    asesmen = input_teks("A - Asesmen / diagnosis", wajib=False)
    plan = input_teks("P - Plan", wajib=False)
    cursor.execute(
        """INSERT INTO rekam_medis (id_kunjungan, subjective, objective, asesmen, plan)
           VALUES (%s, %s, %s, %s, %s)""",
        (id_kunjungan, subjective, objective, asesmen, plan),
    )


def tambah_detail_pemeriksaan(cursor, id_pemeriksaan):
    if not konfirmasi("Tambahkan detail parameter numerik untuk pemeriksaan ini?"):
        return
    subjudul("INPUT DETAIL PARAMETER")
    while True:
        parameter = input_teks("Nama parameter", wajib=True)
        nilai = input_angka("Nilai numerik")
        satuan = input_teks("Satuan", wajib=False)
        rujukan = input_teks("Nilai rujukan", wajib=False)
        cursor.execute(
            """INSERT INTO detail_pemeriksaan
               (id_pemeriksaan, parameter, nilai, satuan, nilai_rujukan)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_pemeriksaan, parameter, nilai, satuan, rujukan),
        )
        if not konfirmasi("Tambah parameter lain pada pemeriksaan ini?"):
            break


def tambah_pemeriksaan(cursor, id_kunjungan):
    subjudul("TAMBAH PEMERIKSAAN")
    while konfirmasi("Tambahkan satu pemeriksaan?"):
        jenis = input_teks("Jenis pemeriksaan", wajib=True, boleh_kosong=False)
        nama = input_teks("Nama pemeriksaan", wajib=True, boleh_kosong=False)
        tanggal = input_tanggal("Tanggal pemeriksaan", wajib=True, dengan_waktu=True)
        hasil = input_teks("Hasil pemeriksaan", wajib=False)
        kesimpulan = input_teks("Kesimpulan", wajib=False)
        cursor.execute(
            """INSERT INTO pemeriksaan
               (id_kunjungan, jenis_pemeriksaan, nama_pemeriksaan, tanggal_pemeriksaan,
                hasil_pemeriksaan, kesimpulan)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (id_kunjungan, jenis, nama, tanggal, hasil, kesimpulan),
        )
        tambah_detail_pemeriksaan(cursor, cursor.lastrowid)


def pilih_pemeriksaan_kunjungan(cursor, id_kunjungan, boleh_kosong=True):
    data = ambil_banyak(
        cursor,
        """SELECT id_pemeriksaan, jenis_pemeriksaan, nama_pemeriksaan, tanggal_pemeriksaan
           FROM pemeriksaan WHERE id_kunjungan = %s ORDER BY tanggal_pemeriksaan""",
        (id_kunjungan,),
    )
    if not data:
        print("Belum ada pemeriksaan pada kunjungan ini.")
        return None
    subjudul("PILIH PEMERIKSAAN TERKAIT")
    if boleh_kosong:
        print("0. Tidak dihubungkan ke pemeriksaan tertentu")
    for nomor, p in enumerate(data, start=1):
        print(f"{nomor}. ID {p['id_pemeriksaan']} | {p['jenis_pemeriksaan']} | {p['nama_pemeriksaan']}")
        print(f"   Tanggal : {tampil(p['tanggal_pemeriksaan'])}")
    while True:
        pilihan = input("Pilih nomor pemeriksaan : ").strip()
        if boleh_kosong and pilihan == "0":
            return None
        if pilihan.isdigit() and 1 <= int(pilihan) <= len(data):
            return data[int(pilihan) - 1]["id_pemeriksaan"]
        print("Pilihan tidak valid.")


def tambah_dokumen(cursor, id_kunjungan):
    subjudul("TAMBAH DOKUMEN PENDUKUNG")
    while konfirmasi("Tambahkan satu dokumen pendukung?"):
        jenis = input_teks("Jenis dokumen", wajib=True, boleh_kosong=False)
        nama = input_teks("Nama dokumen", wajib=True, boleh_kosong=False)
        nomor = input_teks("Nomor dokumen", wajib=False)
        tanggal = input_tanggal("Tanggal dokumen", wajib=True, dengan_waktu=True)
        pemeriksaan = pilih_pemeriksaan_kunjungan(cursor, id_kunjungan, boleh_kosong=True)
        status = input_teks("Status validasi", default="Belum diverifikasi", wajib=True, boleh_kosong=False)
        cursor.execute(
            """INSERT INTO dokumen_pendukung
               (id_kunjungan, id_pemeriksaan, jenis_dokumen, nama_dokumen,
                nomor_dokumen, tanggal_dokumen, status_validasi)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (id_kunjungan, pemeriksaan, jenis, nama, nomor, tanggal, status),
        )


def tambah_data(cursor, koneksi):
    try:
        koneksi.start_transaction()
        subjudul("TAMBAH DATA REKAM MEDIS")
        no_rm = input_teks("No. RM pasien", wajib=True, boleh_kosong=False)
        pasien = cari_pasien(cursor, no_rm)

        if pasien:
            print(f"Pasien ditemukan: {pasien['nama_pasien']} ({pasien['no_rm']}).")
        else:
            if not konfirmasi("Pasien belum terdaftar. Tambahkan sebagai pasien baru?"):
                koneksi.rollback()
                print("Penambahan dibatalkan.")
                return
            nama = input_teks("Nama pasien", wajib=True, boleh_kosong=False)
            lahir = input_tanggal("Tanggal lahir", wajib=False)
            while True:
                jk = input_teks("Jenis kelamin (L/P)", wajib=False)
                jk = jk.upper() if jk else None
                if jk in (None, "L", "P"):
                    break
                print("  Masukkan L, P, atau kosongkan.")
            alamat = input_teks("Alamat", wajib=False)
            cursor.execute(
                """INSERT INTO pasien (no_rm, nama_pasien, tanggal_lahir, jenis_kelamin, alamat)
                   VALUES (%s, %s, %s, %s, %s)""",
                (no_rm, nama, lahir, jk, alamat),
            )
            pasien = ambil_satu(cursor, "SELECT * FROM pasien WHERE id_pasien = %s", (cursor.lastrowid,))

        print(f"Pasien terpilih: {pasien['nama_pasien']}")
        dokter_id = pilih_dokter(cursor)
        tanggal = input_tanggal("Tanggal dan waktu kunjungan", wajib=True, dengan_waktu=True)
        jenis = input_teks("Jenis kunjungan", wajib=True, boleh_kosong=False)
        kode = buat_kode_kunjungan(cursor, tanggal)
        cursor.execute(
            """INSERT INTO kunjungan
               (kode_kunjungan, id_pasien, id_dokter, tanggal_kunjungan, jenis_kunjungan)
               VALUES (%s, %s, %s, %s, %s)""",
            (kode, pasien["id_pasien"], dokter_id, tanggal, jenis),
        )
        id_kunjungan = cursor.lastrowid
        print(f"Kode kunjungan dibuat otomatis: {kode}")

        tambah_soap(cursor, id_kunjungan)
        tambah_pemeriksaan(cursor, id_kunjungan)
        tambah_dokumen(cursor, id_kunjungan)
        koneksi.commit()
        print("\nData kunjungan berhasil disimpan.")
    except (Error, ValueError) as e:
        koneksi.rollback()
        print(f"Gagal menyimpan data. Perubahan dibatalkan. Detail: {e}")
    except Exception:
        koneksi.rollback()
        print("Terjadi kesalahan. Perubahan dibatalkan agar data tidak tersimpan setengah.")
        raise


# ========================= MENU 3: UBAH DATA =========================
def ubah_soap(cursor, id_kunjungan):
    soap = ambil_satu(cursor, "SELECT * FROM rekam_medis WHERE id_kunjungan = %s", (id_kunjungan,))
    if not soap:
        print("Belum ada catatan SOAP untuk kunjungan ini.")
        if not konfirmasi("Buat catatan SOAP baru?"):
            return
        subjudul("BUAT CATATAN SOAP")
        subjective = input_teks("S - Subjective", wajib=False)
        objective = input_teks("O - Objective", wajib=False)
        asesmen = input_teks("A - Asesmen / diagnosis", wajib=False)
        plan = input_teks("P - Plan", wajib=False)
        cursor.execute(
            """INSERT INTO rekam_medis (id_kunjungan, subjective, objective, asesmen, plan)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_kunjungan, subjective, objective, asesmen, plan),
        )
        print("Catatan SOAP berhasil dibuat.")
        return

    subjudul("UBAH CATATAN SOAP")
    petunjuk_edit()
    subjective = input_teks("S - Subjective", default=soap["subjective"])
    objective = input_teks("O - Objective", default=soap["objective"])
    asesmen = input_teks("A - Asesmen / diagnosis", default=soap["asesmen"])
    plan = input_teks("P - Plan", default=soap["plan"])
    cursor.execute(
        """UPDATE rekam_medis SET subjective=%s, objective=%s, asesmen=%s, plan=%s
           WHERE id_kunjungan=%s""",
        (subjective, objective, asesmen, plan, id_kunjungan),
    )
    print("Catatan SOAP berhasil diperbarui.")


def pilih_pemeriksaan_untuk_edit(cursor, id_kunjungan):
    daftar = ambil_banyak(
        cursor,
        "SELECT * FROM pemeriksaan WHERE id_kunjungan=%s ORDER BY tanggal_pemeriksaan",
        (id_kunjungan,),
    )
    if not daftar:
        print("Belum ada pemeriksaan pada kunjungan ini.")
        return None
    subjudul("PILIH PEMERIKSAAN")
    for i, p in enumerate(daftar, start=1):
        print(f"{i}. ID {p['id_pemeriksaan']} | {p['jenis_pemeriksaan']} | {p['nama_pemeriksaan']}")
        print(f"   Tanggal : {tampil(p['tanggal_pemeriksaan'])}")
    while True:
        pilihan = input("Pilih nomor pemeriksaan (0 untuk batal) : ").strip()
        if pilihan == "0":
            return None
        if pilihan.isdigit() and 1 <= int(pilihan) <= len(daftar):
            return daftar[int(pilihan) - 1]
        print("Pilihan tidak valid.")


def ubah_pemeriksaan(cursor, id_kunjungan):
    p = pilih_pemeriksaan_untuk_edit(cursor, id_kunjungan)
    if not p:
        return
    subjudul("UBAH PEMERIKSAAN")
    print("1. Ubah data / hasil pemeriksaan")
    print("2. Kelola detail parameter numerik")
    print("0. Kembali")
    pilihan = input("Pilih menu (0-2) : ").strip()

    if pilihan == "1":
        subjudul("UBAH DATA PEMERIKSAAN")
        petunjuk_edit()
        jenis = input_teks("Jenis pemeriksaan", default=p["jenis_pemeriksaan"], wajib=True, boleh_kosong=False)
        nama = input_teks("Nama pemeriksaan", default=p["nama_pemeriksaan"], wajib=True, boleh_kosong=False)
        tanggal = input_tanggal("Tanggal pemeriksaan", default=p["tanggal_pemeriksaan"], wajib=True, dengan_waktu=True)
        hasil = input_teks("Hasil pemeriksaan", default=p["hasil_pemeriksaan"])
        kesimpulan = input_teks("Kesimpulan", default=p["kesimpulan"])
        cursor.execute(
            """UPDATE pemeriksaan SET jenis_pemeriksaan=%s, nama_pemeriksaan=%s,
               tanggal_pemeriksaan=%s, hasil_pemeriksaan=%s, kesimpulan=%s
               WHERE id_pemeriksaan=%s""",
            (jenis, nama, tanggal, hasil, kesimpulan, p["id_pemeriksaan"]),
        )
        print("Data pemeriksaan berhasil diperbarui.")
    elif pilihan == "2":
        kelola_detail(cursor, p["id_pemeriksaan"])
    elif pilihan == "0":
        return
    else:
        print("Pilihan tidak valid.")


def kelola_detail(cursor, id_pemeriksaan):
    data = ambil_banyak(
        cursor,
        "SELECT * FROM detail_pemeriksaan WHERE id_pemeriksaan=%s ORDER BY id_detail",
        (id_pemeriksaan,),
    )
    subjudul("KELOLA DETAIL PARAMETER")
    if not data:
        print("Belum ada detail parameter.")
    for i, d in enumerate(data, start=1):
        satuan = f" {d['satuan']}" if d["satuan"] else ""
        print(f"{i}. ID {d['id_detail']} | {d['parameter']} = {d['nilai']}{satuan} | Rujukan: {d['nilai_rujukan'] or '-'}")

    print("\n1. Tambah parameter")
    print("2. Ubah parameter yang ada")
    print("3. Hapus parameter")
    print("0. Kembali")
    pilihan = input("Pilih menu (0-3) : ").strip()

    if pilihan == "1":
        parameter = input_teks("Nama parameter", wajib=True, boleh_kosong=False)
        nilai = input_angka("Nilai numerik")
        satuan = input_teks("Satuan", wajib=False)
        rujukan = input_teks("Nilai rujukan", wajib=False)
        cursor.execute(
            """INSERT INTO detail_pemeriksaan
               (id_pemeriksaan, parameter, nilai, satuan, nilai_rujukan)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_pemeriksaan, parameter, nilai, satuan, rujukan),
        )
        print("Detail parameter berhasil ditambahkan.")

    elif pilihan in ("2", "3"):
        if not data:
            print("Tidak ada parameter yang dapat dipilih.")
            return
        while True:
            pilihan_data = input("Pilih nomor parameter (0 untuk batal) : ").strip()
            if pilihan_data == "0":
                return
            if pilihan_data.isdigit() and 1 <= int(pilihan_data) <= len(data):
                d = data[int(pilihan_data) - 1]
                break
            print("Pilihan tidak valid.")

        if pilihan == "3":
            if konfirmasi(f"Hapus parameter '{d['parameter']}'?"):
                cursor.execute("DELETE FROM detail_pemeriksaan WHERE id_detail=%s", (d["id_detail"],))
                print("Parameter berhasil dihapus.")
            else:
                print("Penghapusan parameter dibatalkan.")
        else:
            subjudul("UBAH DETAIL PARAMETER")
            petunjuk_edit()
            parameter = input_teks("Nama parameter", default=d["parameter"], wajib=True, boleh_kosong=False)
            nilai = input_angka("Nilai numerik", default=d["nilai"])
            satuan = input_teks("Satuan", default=d["satuan"])
            rujukan = input_teks("Nilai rujukan", default=d["nilai_rujukan"])
            cursor.execute(
                """UPDATE detail_pemeriksaan
                   SET parameter=%s, nilai=%s, satuan=%s, nilai_rujukan=%s
                   WHERE id_detail=%s""",
                (parameter, nilai, satuan, rujukan, d["id_detail"]),
            )
            print("Detail parameter berhasil diperbarui.")
    elif pilihan != "0":
        print("Pilihan tidak valid.")


def ubah_dokumen(cursor, id_kunjungan):
    data = ambil_banyak(
        cursor,
        "SELECT * FROM dokumen_pendukung WHERE id_kunjungan=%s ORDER BY tanggal_dokumen",
        (id_kunjungan,),
    )
    if not data:
        print("Belum ada dokumen pendukung pada kunjungan ini.")
        if konfirmasi("Tambahkan dokumen baru?"):
            tambah_dokumen(cursor, id_kunjungan)
        return

    subjudul("PILIH DOKUMEN")
    for i, d in enumerate(data, start=1):
        print(f"{i}. ID {d['id_dokumen']} | {d['jenis_dokumen']} | {d['nama_dokumen']}")
        print(f"   Status : {d['status_validasi']}")
    while True:
        pilihan = input("Pilih nomor dokumen (0 untuk batal) : ").strip()
        if pilihan == "0":
            return
        if pilihan.isdigit() and 1 <= int(pilihan) <= len(data):
            d = data[int(pilihan) - 1]
            break
        print("Pilihan tidak valid.")

    subjudul("UBAH DOKUMEN PENDUKUNG")
    petunjuk_edit()
    jenis = input_teks("Jenis dokumen", default=d["jenis_dokumen"], wajib=True, boleh_kosong=False)
    nama = input_teks("Nama dokumen", default=d["nama_dokumen"], wajib=True, boleh_kosong=False)
    nomor = input_teks("Nomor dokumen", default=d["nomor_dokumen"])
    tanggal = input_tanggal("Tanggal dokumen", default=d["tanggal_dokumen"], wajib=True, dengan_waktu=True)
    status = input_teks("Status validasi", default=d["status_validasi"], wajib=True, boleh_kosong=False)
    cursor.execute(
        """UPDATE dokumen_pendukung SET jenis_dokumen=%s, nama_dokumen=%s,
           nomor_dokumen=%s, tanggal_dokumen=%s, status_validasi=%s
           WHERE id_dokumen=%s""",
        (jenis, nama, nomor, tanggal, status, d["id_dokumen"]),
    )
    print("Data dokumen berhasil diperbarui.")

def ubah_data_pasien(cursor, pasien):
    print("\n=== UBAH DATA PASIEN ===")
    print("Tekan Enter jika data tidak ingin diubah.")

    no_rm = input(f"No. RM [{pasien['no_rm']}] : ").strip()
    nama = input(
        f"Nama pasien [{pasien['nama_pasien']}] : "
    ).strip()
    tanggal_lahir = input(
        f"Tanggal lahir [{pasien['tanggal_lahir']}] : "
    ).strip()
    jenis_kelamin = input(
        f"Jenis kelamin [{pasien['jenis_kelamin']}] : "
    ).strip()
    alamat = input(
        f"Alamat [{pasien['alamat']}] : "
    ).strip()

    if no_rm == "":
        no_rm = pasien["no_rm"]
    if nama == "":
        nama = pasien["nama_pasien"]
    if tanggal_lahir == "":
        tanggal_lahir = pasien["tanggal_lahir"]
    if jenis_kelamin == "":
        jenis_kelamin = pasien["jenis_kelamin"]
    if alamat == "":
        alamat = pasien["alamat"]

    sql = """
        UPDATE pasien
        SET no_rm = %s,
            nama_pasien = %s,
            tanggal_lahir = %s,
            jenis_kelamin = %s,
            alamat = %s
        WHERE id_pasien = %s
    """

    cursor.execute(
        sql,
        (
            no_rm,
            nama,
            tanggal_lahir,
            jenis_kelamin,
            alamat,
            pasien["id_pasien"],
        ),
    )

    print("Data pasien berhasil diperbarui.")

def pilih_dokter(cursor):
    cursor.execute(
        "SELECT * FROM dokter ORDER BY nama_dokter"
    )
    daftar_dokter = cursor.fetchall()

    if not daftar_dokter:
        print("Data dokter tidak ditemukan.")
        return None

    print("\n=== DAFTAR DOKTER ===")
    for i, dokter in enumerate(daftar_dokter, start=1):
        print(
            f"{i}. {dokter['kode_dokter']} - "
            f"{dokter['nama_dokter']} - "
            f"{dokter['spesialisasi']}"
        )

    pilihan = input("Pilih nomor dokter (0 untuk batal): ").strip()

    if pilihan == "0":
        return None

    if pilihan.isdigit() and 1 <= int(pilihan) <= len(daftar_dokter):
        return daftar_dokter[int(pilihan) - 1]

    print("Pilihan tidak valid.")
    return None

def ubah_data_dokter(cursor):
    dokter = pilih_dokter(cursor)

    if dokter is None:
        return

    print("\n=== UBAH DATA DOKTER ===")
    print("Tekan Enter jika data tidak ingin diubah.")

    kode = input(
        f"Kode dokter [{dokter['kode_dokter']}] : "
    ).strip()
    nama = input(
        f"Nama dokter [{dokter['nama_dokter']}] : "
    ).strip()
    spesialisasi = input(
        f"Spesialisasi [{dokter['spesialisasi']}] : "
    ).strip()

    if kode == "":
        kode = dokter["kode_dokter"]
    if nama == "":
        nama = dokter["nama_dokter"]
    if spesialisasi == "":
        spesialisasi = dokter["spesialisasi"]

    sql = """
        UPDATE dokter
        SET kode_dokter = %s,
            nama_dokter = %s,
            spesialisasi = %s
        WHERE id_dokter = %s
    """

    cursor.execute(
        sql,
        (kode, nama, spesialisasi, dokter["id_dokter"]),
    )

    print("Data dokter berhasil diperbarui.")

def ubah_data(cursor, koneksi):
    try:
        pasien = pilih_pasien(cursor)
        if not pasien:
            return
        kunjungan = pilih_kunjungan(cursor, pasien)
        if not kunjungan:
            return

        while True:
            subjudul("MENU UBAH DATA KUNJUNGAN")
            print("1. Ubah data pasien")
            print("2. Ubah data dokter")
            print("3. Ubah catatan data klinis")
            print("4. Ubah pemeriksaan")
            print("5. Ubah dokumen pendukung")
            print("0. Kembali ke menu utama")
            pilihan = input("Pilih menu (0-5) : ").strip()

            if pilihan == "1":
                pasien = pilih_pasien(cursor)
            elif pasien:
                ubah_data_pasien(cursor, pasien)
            elif pilihan == "2":
                ubah_data_dokter(cursor)
            elif pilihan == "3":
                ubah_soap(cursor, kunjungan["id_kunjungan"])
            elif pilihan == "4":
                ubah_pemeriksaan(cursor, kunjungan["id_kunjungan"])
            elif pilihan == "5":
                ubah_dokumen(cursor, kunjungan["id_kunjungan"])
            elif pilihan == "0":
                break
            else:
                print("Pilihan tidak valid.")
        koneksi.commit()
        print("Perubahan berhasil disimpan.")
    except (Error, ValueError) as e:
        koneksi.rollback()
        print(f"Gagal mengubah data. Perubahan dibatalkan. Detail: {e}")


# ========================= MENU 4: HAPUS KUNJUNGAN =========================
def hapus_kunjungan(cursor, koneksi):
    try:
        pasien = pilih_pasien(cursor)
        if not pasien:
            return
        kunjungan = pilih_kunjungan(cursor, pasien)
        if not kunjungan:
            return

        subjudul("KONFIRMASI HAPUS KUNJUNGAN")
        print(f"Kode kunjungan : {kunjungan['kode_kunjungan']}")
        print("SOAP, pemeriksaan, detail parameter, dan dokumen terkait akan ikut terhapus.")
        print("Data pasien dan dokter tidak ikut dihapus.")
        kode = input_teks("Ketik ulang kode kunjungan", wajib=True, boleh_kosong=False)
        if kode != kunjungan["kode_kunjungan"]:
            print("Kode tidak cocok. Data tidak dihapus.")
            return
        if not konfirmasi("Yakin menghapus kunjungan ini?"):
            print("Penghapusan dibatalkan.")
            return

        cursor.execute("DELETE FROM kunjungan WHERE id_kunjungan=%s", (kunjungan["id_kunjungan"],))
        koneksi.commit()
        print("Kunjungan berhasil dihapus. Data terkait ikut terhapus sesuai aturan ON DELETE CASCADE.")
    except Error as e:
        koneksi.rollback()
        print(f"Gagal menghapus kunjungan: {e}")


# ========================= MENU UTAMA =========================
def main():
    koneksi = None
    cursor = None
    try:
        koneksi = koneksi_database()
        cursor = koneksi.cursor(dictionary=True)
    except Error as e:
        print("Tidak dapat terhubung ke MySQL.")
        print("Periksa apakah MySQL di XAMPP aktif dan database db_rekam_medis sudah diimpor.")
        print(f"Detail koneksi: {e}")
        return

    try:
        while True:
            print("\n" + GARIS)
            print("SISTEM DATABASE REKAM MEDIS".center(78))
            print(GARIS)
            print("1. Lihat Data Rekam Medis")
            print("2. Tambah Data Rekam Medis")
            print("3. Ubah Data Rekam Medis")
            print("4. Hapus Data Kunjungan")
            print("5. Keluar")
            print(GARIS)
            pilihan = input("Pilih Menu (1-5): ").strip()

            if pilihan == "1":
                lihat_data(cursor)
            elif pilihan == "2":
                tambah_data(cursor, koneksi)
            elif pilihan == "3":
                ubah_data(cursor, koneksi)
            elif pilihan == "4":
                hapus_kunjungan(cursor, koneksi)
            elif pilihan == "5":
                print("Program selesai.")
                break
            else:
                print("Pilihan tidak valid. Masukkan angka 1 sampai 5.")
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
    finally:
        if cursor is not None:
            cursor.close()
        if koneksi is not None and koneksi.is_connected():
            koneksi.close()


if __name__ == "__main__":
    main()
