# Proyek Analisis Data: Bike Sharing Dataset

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011–2012) beserta dashboard interaktif Streamlit.

## Struktur Direktori
```
submission
├── dashboard
│   ├── main_data.csv     # data per jam yang sudah dibersihkan
│   ├── day_data.csv      # data harian yang sudah dibersihkan
│   └── dashboard.py
├── data
│   ├── day.csv
│   ├── hour.csv
│   └── Readme.txt
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment
```
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Menjalankan Dashboard
```
cd submission
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.

## Menjalankan Notebook
Jalankan `notebook.ipynb` dari folder `submission` (agar path `data/` terbaca). Menjalankan seluruh sel akan menghasilkan ulang `dashboard/main_data.csv` dan `dashboard/day_data.csv`.
