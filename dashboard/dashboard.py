import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")
BASE = os.path.dirname(os.path.abspath(__file__))

Q1 = "Pada jam berapa saja terjadi tiga jam puncak dengan rata-rata penyewaan sepeda per jam tertinggi pada hari kerja dibandingkan akhir pekan/hari libur sepanjang tahun 2011–2012, dan berapa selisih rata-ratanya pada jam puncak tersebut, sebagai dasar penjadwalan redistribusi sepeda dan penempatan petugas lapangan?"
Q2 = "Berapa persentase selisih rata-rata penyewaan sepeda per hari pada cuaca hujan/salju ringan dibandingkan cuaca cerah sepanjang tahun 2011–2012, sebagai dasar penentuan strategi promosi saat cuaca buruk?"
Q3 = "Musim apa yang memiliki rata-rata penyewaan sepeda per hari tertinggi dan terendah sepanjang tahun 2011–2012, sebagai dasar penentuan jadwal perawatan dan penambahan armada?"

st.set_page_config(page_title="Dashboard Bike Sharing", page_icon="🚲", layout="wide")


@st.cache_data
def load_data():
    hour = pd.read_csv(os.path.join(BASE, "main_data.csv"), parse_dates=["dteday"])
    day = pd.read_csv(os.path.join(BASE, "day_data.csv"), parse_dates=["dteday"])
    return hour, day


hour_df, day_df = load_data()

# ---------------- Sidebar (filter) ----------------
st.sidebar.header("Filter Data")
min_d, max_d = day_df["dteday"].min().date(), day_df["dteday"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", value=(min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start, end = pd.to_datetime(min_d), pd.to_datetime(max_d)

seasons = st.sidebar.multiselect("Musim", ["Spring", "Summer", "Fall", "Winter"],
                                 default=["Spring", "Summer", "Fall", "Winter"])

h = hour_df[(hour_df["dteday"].between(start, end)) & (hour_df["season"].isin(seasons))]
d = day_df[(day_df["dteday"].between(start, end)) & (day_df["season"].isin(seasons))]

st.title("🚲 Dashboard Analisis Bike Sharing (2011–2012)")
st.caption("Sumber data: Capital Bikeshare, Washington D.C.")

if d.empty or h.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah rentang tanggal atau musim.")
    st.stop()

# ---------------- Ringkasan ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Total Penyewaan", f"{d['cnt'].sum():,}")
c2.metric("Rata-rata Penyewaan Harian", f"{d['cnt'].mean():,.0f}")
c3.metric("Proporsi Pengguna Registered", f"{d['registered'].sum() / d['cnt'].sum() * 100:.1f}%")

# ---------------- Pertanyaan 1 ----------------
st.subheader("Pertanyaan 1")
st.write(Q1)
hourly = h.groupby(["day_type", "hr"])["cnt"].mean().unstack(0)
colors = {"Hari Kerja": "#1f77b4", "Akhir Pekan/Libur": "#ff7f0e"}
fig, ax = plt.subplots(figsize=(11, 4.5))
for col in hourly.columns:
    ax.plot(hourly.index, hourly[col], marker="o", linewidth=2.2, label=col, color=colors[col])
    hp = hourly[col].idxmax()
    ax.annotate(f"Puncak jam {hp} ({hourly[col].max():.0f})", xy=(hp, hourly[col].max()),
                xytext=(hp + 0.8, hourly[col].max() + 35), color=colors[col], fontsize=9, fontweight="bold")
ax.set_xticks(range(24))
ax.set_ylim(0, hourly.max().max() * 1.2)
ax.set_xlabel("Jam dalam sehari (0–23)")
ax.set_ylabel("Rata-rata penyewaan per jam")
ax.set_title("Pola rata-rata penyewaan per jam", loc="left")
ax.legend()
sns.despine()
st.pyplot(fig)

cols = st.columns(len(hourly.columns))
for col, w in zip(hourly.columns, cols):
    top3 = hourly[col].nlargest(3)
    w.markdown(f"**3 jam puncak – {col}**")
    w.dataframe(top3.round(1).rename("Rata-rata penyewaan").rename_axis("Jam"))

# ---------------- Pertanyaan 2 ----------------
st.subheader("Pertanyaan 2")
st.write(Q2)
w_order = [w for w in ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan"] if w in d["weathersit"].unique()]
w_avg = d.groupby("weathersit")["cnt"].mean().reindex(w_order)
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar(w_order, w_avg, color=["#d62728" if w == "Hujan/Salju Ringan" else "#bdbdbd" for w in w_order])
ax.bar_label(bars, fmt="%.0f", padding=3)
ax.set_ylim(0, w_avg.max() * 1.2)
ax.set_xlabel("Kondisi cuaca")
ax.set_ylabel("Rata-rata penyewaan sepeda per hari")
ax.set_title("Rata-rata penyewaan menurut kondisi cuaca", loc="left")
sns.despine()
st.pyplot(fig)
if "Cerah" in w_avg.index and "Hujan/Salju Ringan" in w_avg.index:
    gap = (w_avg["Cerah"] - w_avg["Hujan/Salju Ringan"]) / w_avg["Cerah"] * 100
    st.info(f"Rata-rata penyewaan saat hujan/salju ringan **{gap:.0f}% lebih rendah** dibanding cuaca cerah.")
else:
    st.info("Pilih rentang tanggal/musim yang memuat cuaca cerah dan hujan/salju ringan untuk melihat persentase selisih.")

# ---------------- Pertanyaan 3 ----------------
st.subheader("Pertanyaan 3")
st.write(Q3)
s_order = [x for x in ["Spring", "Summer", "Fall", "Winter"] if x in d["season"].unique()]
s_avg = d.groupby("season")["cnt"].mean().reindex(s_order)
fig, ax = plt.subplots(figsize=(8, 4.5))
bar_colors = ["#d62728" if x == s_avg.idxmin() else "#1f77b4" if x == s_avg.idxmax() else "#bdbdbd" for x in s_order]
bars = ax.bar(s_order, s_avg, color=bar_colors)
ax.bar_label(bars, fmt="%.0f", padding=3)
ax.set_ylim(0, s_avg.max() * 1.2)
ax.set_xlabel("Musim")
ax.set_ylabel("Rata-rata penyewaan sepeda per hari")
ax.set_title("Rata-rata penyewaan menurut musim", loc="left")
sns.despine()
st.pyplot(fig)
st.info(f"Musim tertinggi: **{s_avg.idxmax()}** ({s_avg.max():,.0f} per hari); terendah: **{s_avg.idxmin()}** ({s_avg.min():,.0f} per hari).")

# ---------------- Analisis lanjutan ----------------
st.subheader("Analisis Lanjutan: Pengelompokan suhu (binning)")
order = ["Dingin (≤10°C)", "Sejuk (10–20°C)", "Hangat (20–30°C)", "Panas (>30°C)"]
t_avg = d.groupby("temp_group")["cnt"].mean().reindex(order).dropna()
fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.bar(t_avg.index, t_avg, color=["#1f77b4" if v == t_avg.max() else "#bdbdbd" for v in t_avg])
ax.bar_label(bars, fmt="%.0f", padding=3)
ax.set_ylim(0, t_avg.max() * 1.2)
ax.set_xlabel("Kelompok suhu")
ax.set_ylabel("Rata-rata penyewaan harian")
ax.set_title("Penyewaan paling tinggi pada suhu hangat", loc="left")
sns.despine()
st.pyplot(fig)

st.subheader("Rekomendasi")
st.markdown("""
- Redistribusi sepeda sebelum jam 07.00 dan 16.00 pada hari kerja; fokus ke area wisata/taman pada siang akhir pekan.
- Jadwalkan perawatan armada saat permintaan rendah (Spring, suhu dingin, hari hujan); fokuskan promosi pada Fall dan suhu hangat.
- Tawarkan promo pada hari hujan/dingin dan gunakan prakiraan cuaca untuk perencanaan harian.
""")
