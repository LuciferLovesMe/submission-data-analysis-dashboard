import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style="dark")

pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]

def create_annual_pollutant_df(df):
    # pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
    annual_pollutant_df = df.groupby([df["datetime"].dt.month, 'station'])[pollutants].mean().reset_index()

    annual_pollutant_df.set_index("datetime", inplace=True)
    return annual_pollutant_df

def create_correlation_df(df):
    correlation_df = df[["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]].corr()
    return correlation_df

def create_binning_df(df):
    binning_df = df.copy()
    binning_df["month"] = binning_df["datetime"].dt.month

    def get_season(month):
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'
        else:
            return 'Winter'

    # Tambah kolom season pada dataframe
    binning_df["season"] = binning_df["month"].apply(get_season)

    # Mengelompokkan data berdasarkan season dan station
    # seasonal_avg = binning_df.groupby(['station', 'season'])[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean().reset_index()
    return binning_df

# Mengambil dataframe dari all data csv
all_df = pd.read_csv("all_data.csv")
sorted_all_df = pd.read_csv("all_data.csv")

# Membuat sorted data by datetime column
sorted_all_df.sort_values(by="datetime", inplace=True)
sorted_all_df.reset_index(inplace=True)

# Mendapatkan list Tahun yang ada
all_df["datetime"] = pd.to_datetime(sorted_all_df["datetime"])
sorted_all_df["datetime"] = pd.to_datetime(sorted_all_df["datetime"])
list_tahun = sorted_all_df["datetime"].dt.year.unique().tolist()

# Membuat sidebar filtering datetime
year = list_tahun[0]

with st.sidebar:
    year = st.selectbox(
        label="Tahun",
        options=(list_tahun),
        index=0
    )
    
filtered_date_df = sorted_all_df[(sorted_all_df["datetime"].dt.year == year)]

annual_pollutant_df = create_annual_pollutant_df(filtered_date_df)
correlation_df = create_correlation_df(all_df)
binning_df = create_binning_df(filtered_date_df)

st.header("Dicoding Air Quality Index (AQI) Dashboard")

# Subheader 1 Persebaran Polutan dari data yang dipilih
st.subheader("Persebaran Polutan Tiap Kota Pada Tahun " + str(year))

# Membuat visualisasi data berdasarkan dataframe annual pollutants
plt.figure(figsize=(16, 10))
for i, pollutant in enumerate(pollutants, 1):
    plt.subplot(3, 2, i)
    for station in annual_pollutant_df['station'].unique():
        subset = annual_pollutant_df[annual_pollutant_df['station'] == station]
        plt.plot(subset.index, subset[pollutant], marker='o', label=station)

    plt.title(f'Tren {pollutant} per tahun')
    plt.xlabel("Tahun")
    plt.ylabel(f"Konsentrasi {pollutant}")
    plt.grid(alpha=0.3)
    plt.legend(title='Stasiun')

plt.tight_layout()
st.pyplot(plt)

# Subheader 2 untuk heatmap korelasi
st.subheader("Korelasi Antara Polutan Dengan Parameter Cuaca")

# Membuat heatmap korelasi antar parameter cuaca dengan polutan
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_df, annot=True, fmt='.2f', cmap="coolwarm")
plt.title("Heatmap Korelasi Polutan dan Parameter Cuaca")
st.pyplot(plt)

# Subheader 3 untuk visualisasi data tiap Musim
st.subheader("Sebaran Polutan Tiap Musim Pada Tahun " + str(year))

# Visualisasi data sebaran
seasonal_avg = binning_df.groupby(['station', 'season'])[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean().reset_index() # Mengelompokkan data berdasarkan season dan station
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
seasons = ['Spring', 'Summer', 'Fall', 'Winter']

for i, pollutant in enumerate(pollutants):
    ax = axes[i // 3, i % 3]
    for station in binning_df['station'].unique():
        data = seasonal_avg[seasonal_avg['station'] == station]
        ax.plot(seasons, data[pollutant], marker='o', label=station)
    ax.set_title(f'{pollutant} Average per Season')
    ax.set_xlabel('Season')
    ax.set_ylabel('Concentration')
    ax.legend()

plt.tight_layout()
st.pyplot(plt)