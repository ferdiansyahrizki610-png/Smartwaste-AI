from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)

# ==================================================
# LOKASI PROJECT
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# List untuk menyimpan riwayat deteksi sementara di memori
history_list = []


# ==================================================
# LOAD MODEL AI
# ==================================================

print("=" * 50)
print("SMARTWASTE AI")
print("=" * 50)

print("Lokasi model:")
print(MODEL_PATH)

if not os.path.exists(MODEL_PATH):
    print("❌ ERROR: best.pt tidak ditemukan!")
else:
    print("✅ best.pt ditemukan!")

model = YOLO(MODEL_PATH)

print("✅ Model AI berhasil dimuat!")
print("Kelas AI:")
print(model.names)

print("=" * 50)


# ==================================================
# HALAMAN UTAMA
# ==================================================

@app.route("/")
def index():
    return render_template("index.html", history=history_list)


# ==================================================
# PROSES UPLOAD DAN ANALISIS
# ==================================================

@app.route("/upload", methods=["POST"])
def upload():

    print("\n")
    print("=" * 50)
    print("PROSES ANALISIS DIMULAI")
    print("=" * 50)

    # Cek file
    if "image" not in request.files:
        print("❌ File gambar tidak ditemukan")
        return render_template(
            "index.html",
            error="Tidak ada gambar yang dipilih.",
            history=history_list
        )

    file = request.files["image"]

    if file.filename == "":
        print("❌ Nama file kosong")
        return render_template(
            "index.html",
            error="Silakan pilih gambar terlebih dahulu.",
            history=history_list
        )

    # ==================================================
    # SIMPAN GAMBAR
    # ==================================================

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    print("✅ Gambar berhasil disimpan:")
    print(filepath)

    # ==================================================
    # PREDIKSI AI
    # ==================================================

    try:
        print("🤖 AI sedang menganalisis gambar...")

        results = model(filepath)
        result = results[0]

        # Pastikan model classification
        if result.probs is None:
            print("❌ Model tidak menghasilkan probabilitas klasifikasi.")
            return render_template(
                "index.html",
                image=filename,
                error="Model tidak menghasilkan hasil klasifikasi.",
                history=history_list
            )

        # Ambil kelas dengan probabilitas tertinggi
        class_id = int(result.probs.top1)
        confidence = float(result.probs.top1conf)
        class_name = result.names[class_id]

        # ==========================================
        # KOREKSI / MAPPING NAMA KELAS MANUAL
        # ==========================================
        correction_map = {
            "plastic": "glass",  # Sesuaikan jika ada label yang tertukar saat training dulu
        }
        
        if class_name in correction_map:
            print(f"🔄 Mengoreksi hasil AI dari '{class_name}' menjadi '{correction_map[class_name]}'")
            class_name = correction_map[class_name]

        confidence_percent = round(confidence * 100, 2)

        print("================================")
        print("HASIL AI")
        print("================================")
        print("Class ID    :", class_id)
        print("Jenis       :", class_name)
        print("Confidence  :", confidence_percent, "%")
        print("================================")

    except Exception as e:
        print("❌ ERROR SAAT PREDIKSI:")
        print(e)

        return render_template(
            "index.html",
            image=filename,
            error=f"Terjadi kesalahan saat AI menganalisis: {e}",
            history=history_list
        )

    # ==================================================
    # REKOMENDASI
    # ==================================================

    recommendations = {
        "cardboard": "Sampah kardus dapat digunakan kembali atau dipisahkan untuk didaur ulang.",
        "glass": "Pisahkan sampah kaca dengan hati-hati dan masukkan ke tempat pengumpulan kaca.",
        "metal": "Pisahkan sampah logam agar dapat diproses dan didaur ulang.",
        "paper": "Pisahkan kertas dari sampah basah dan masukkan ke tempat daur ulang.",
        "plastic": "Pisahkan sampah plastik dan masukkan ke tempat daur ulang jika tersedia.",
        "trash": "Sampah ini termasuk kategori residu. Buang ke tempat sampah yang sesuai."
    }

    recommendation = recommendations.get(
        class_name.lower(),
        "Pisahkan sampah berdasarkan jenisnya."
    )

    # Pesan berdasarkan tingkat confidence
    if confidence_percent < 50:
        confidence_message = "⚠️ AI kurang yakin dengan hasil ini. Silakan gunakan foto yang lebih jelas."
    elif confidence_percent < 70:
        confidence_message = "⚠️ Tingkat keyakinan AI sedang. Hasil dapat berubah jika foto berbeda."
    else:
        confidence_message = "✅ AI cukup yakin dengan hasil klasifikasi ini."

    # ==================================================
    # SIMPAN KE RIWAYAT (HISTORY)
    # ==================================================
    history_item = {
        "image": filename,
        "result": class_name,
        "confidence": confidence_percent,
        "recommendation": recommendation
    }
    
    # Masukkan ke urutan paling atas, batasi maksimal 5 riwayat
    history_list.insert(0, history_item)
    if len(history_list) > 5:
        history_list.pop()

    # ==================================================
    # KIRIM HASIL KE HTML
    # ==================================================

    return render_template(
        "index.html",
        image=filename,
        result=class_name,
        confidence=confidence_percent,
        recommendation=recommendation,
        confidence_message=confidence_message,
        history=history_list
    )


# ==================================================
# RUN FLASK (Disesuaikan untuk Lokal & Hosting)
# ==================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)