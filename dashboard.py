import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO
from streamlit_option_menu import option_menu
import folium 
from streamlit_folium import folium_static

# Function to load data from the CSV URL
@st.cache_data

def load_data(url):
    response = requests.get(url)

    if response.status_code == 200:
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df

# Streamlit app

# Load the data
geolocation_dataset = load_data("https://drive.google.com/uc?id=1pKRLS_6HoMLUc8r-PjbiFnNYSO5VTush")
orders_dataset = load_data("https://drive.google.com/uc?id=1HgH7ke4kSh9fAdePcFZ0ogMNDvavtNUe")
order_payments_dataset = load_data("https://drive.google.com/uc?id=1gOTQNTOfu11MoXv1aTsTmpJw15pJSWpv")

# Display the loaded data
# st.dataframe(geolocation_dataset)
# st.dataframe(orders_dataset)
# st.dataframe(order_payments_dataset)


#   CLEANING DATA
    # * Data Order Payments Dataset
str_payment = ['order_id','payment_type']
for i in str_payment:
    order_payments_dataset[i] = order_payments_dataset[i] .astype('string')
order_payments_dataset.duplicated()

    # * Geolocation Dataset
str_geolocation = ['geolocation_city','geolocation_state']
for i in str_geolocation:
    geolocation_dataset[i] = geolocation_dataset[i] .astype('string')

    # * orders_dataset
datetime_order = ['order_approved_at','order_delivered_carrier_date','order_delivered_customer_date','order_purchase_timestamp','order_estimated_delivery_date']
for i in datetime_order:
    orders_dataset[i] = pd.to_datetime(orders_dataset[i])

# type str column
str_order = ['order_id','customer_id','order_status']
for i in str_order:
    orders_dataset[i] = orders_dataset[i] .astype('string')


#   Duplikat
order_payments_dataset.duplicated()
geolocation_dataset.drop_duplicates(inplace=True)
geolocation_dataset.reset_index(drop=True, inplace=True)
orders_dataset.drop_duplicates(inplace=True)
data_geo_state = geolocation_dataset.drop_duplicates(subset='geolocation_state')
data_geo_state = data_geo_state.reset_index(drop=True)

#   Missing values
# Menghitung rata-rata dari setiap kolom dan mengisi nilai null dengan rata-rata
orders_dataset['order_approved_at'] = orders_dataset['order_approved_at'].fillna(orders_dataset['order_approved_at'].mean())
orders_dataset['order_delivered_carrier_date'] = orders_dataset['order_delivered_carrier_date'].fillna(orders_dataset['order_delivered_carrier_date'].mean())
orders_dataset['order_delivered_customer_date'] = orders_dataset['order_delivered_customer_date'].fillna(orders_dataset['order_delivered_customer_date'].mean())


# Ekstrak tahun dan bulan dari waktu pembelian
orders_dataset['purchase_year_month'] = orders_dataset['order_purchase_timestamp'].dt.to_period('M')

# Filter pesanan yang sudah diselesaikan
completed_orders = orders_dataset[orders_dataset['order_status'].isin(['delivered', 'shipped', 'canceled', 'unavailable', 'invoiced', 'processing', 'created', 'approved'])]

# Hitung jumlah pesanan per bulan
total_orders_per_month = orders_dataset.groupby('purchase_year_month').size()

# Hitung jumlah pesanan yang sudah diselesaikan per bulan
completed_orders_per_month = completed_orders.groupby('purchase_year_month').size()

# Hitung persentase pesanan yang sudah diselesaikan per bulan
percentage_completed_orders_per_month = (completed_orders_per_month / total_orders_per_month) * 100

# Menghitung total pembayaran untuk setiap jenis pembayaran
payment_type_distribution = order_payments_dataset.groupby('payment_type')['payment_value'].sum()
payment_type_distribution = order_payments_dataset.groupby('payment_type')['payment_value'].count()
payment_type_order = order_payments_dataset.groupby(by="payment_type").order_id.nunique().sort_values(ascending=False)

#Explor dataset
# Menghitung waktu pengiriman ('delivery_time') hari
orders_dataset['waktu_pengiriman'] = (orders_dataset['order_delivered_customer_date'] - orders_dataset['order_purchase_timestamp']).dt.days
# Menambahkan kolom bulan
orders_dataset['bulan_pesanan'] = orders_dataset['order_purchase_timestamp'].dt.to_period('M')

# Menghitung jumlah pesanan tiap bulan
jumlah_pesanan_bulanan = orders_dataset.groupby('bulan_pesanan')['customer_id'].count()

# Membuat DataFrame baru untuk hasil jumlah pesanan
hasil_pesanan_bulanan = pd.DataFrame(jumlah_pesanan_bulanan).reset_index()

# Menghitung waktu pengiriman rata-rata setiap bulan
waktu_pengiriman_bulanan = orders_dataset.groupby('bulan_pesanan')['waktu_pengiriman'].mean()

# Ubah hasil ke dalam DataFrame untuk kemudahan pembacaan
hasil_rata_rata_bulanan = pd.DataFrame(waktu_pengiriman_bulanan).reset_index().rename(columns={'bulan_pesanan': 'bulan', 'waktu_pengiriman': 'rata-rata pengiriman'})

# Ekstrak tahun dan bulan dari waktu pembelian
orders_dataset['purchase_year_month'] = orders_dataset['order_purchase_timestamp'].dt.to_period('M')

# Filter pesanan yang sudah diselesaikan
completed_orders = orders_dataset[orders_dataset['order_status'].isin(['delivered', 'shipped', 'canceled', 'unavailable', 'invoiced', 'processing', 'created', 'approved'])]

# Hitung jumlah pesanan per bulan
total_orders_per_month = orders_dataset.groupby('purchase_year_month').size()

# Hitung jumlah pesanan yang sudah diselesaikan per bulan
completed_orders_per_month = completed_orders.groupby('purchase_year_month').size()

# Hitung persentase pesanan yang sudah diselesaikan per bulan
percentage_completed_orders_per_month = (completed_orders_per_month / total_orders_per_month) * 100
# Menggabungkan data order dan payment
merged_data = pd.merge(orders_dataset, order_payments_dataset, on='order_id')
# Memfilter data hanya untuk rentang waktu Januari 2017 hingga Januari 2018
filtered_data = merged_data.loc[(merged_data['order_purchase_timestamp'] >= '2017-01-01') & (merged_data['order_purchase_timestamp'] < '2018-02-01')].copy()

# Ekstrak tahun dan bulan dari waktu pembelian
filtered_data['purchase_year_month'] = filtered_data['order_purchase_timestamp'].dt.to_period('M')

# Hitung jumlah pembayaran untuk setiap metode per bulan
payment_trend = filtered_data.groupby(['purchase_year_month', 'payment_type']).size().unstack()





########################################################################################################
########################################################################################################
########################################################################################################





def analisis_pembayaran() :
    # Membuat daftar warna untuk setiap kategori pembayaran
    colors = ['skyblue', 'lightcoral', 'lightgreen', 'orange', 'lightblue']

    # Visualisasi menggunakan diagram batang dengan warna yang berbeda untuk setiap kategori
    plt.figure(figsize=(10, 6))
    plt.bar(payment_type_distribution.index,
            payment_type_distribution,
            color=colors)
    plt.xlabel('Jenis Pembayaran')
    plt.ylabel('Total Pembayaran')
    plt.title('Distribusi Jumlah Pembayaran berdasarkan Jenis Pembayaran')
    st.pyplot()


def analisis_pengiriman_rata2() :
    plt.figure(figsize=(12, 6))
    waktu_pengiriman_bulanan.plot(kind='line',marker='o',color='green')
    # # Hitung rata-rata
    hasil_rata_rata_bulanan_min = waktu_pengiriman_bulanan.mean()

    # Garis rata-rata
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.title('Jumlah Pengiriman Pesanan Rata-rata Setiap Bulan')
    plt.xlabel('Bulan dan Tahun')
    plt.ylabel('Rata-rata Waktu Pengiriman')
    plt.xticks(rotation=45 )
    st.pyplot()

def analisis_tren_pembayaran() :
    # fig, ax = plt.subplots()
    # ax.scatter([1, 2, 3], [1, 2, 3])
    plt.figure(figsize=(12, 6))
    payment_trend.plot(marker='o')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title('Tren Penggunaan Metode Pembayaran dari Januari 2017 hingga Januari 2018')
    plt.xlabel('Tahun dan Bulan Pembelian')
    plt.ylabel('Jumlah Pembayaran')
    plt.legend(title='Metode Pembayaran', loc='upper left')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()



def analisis_penjualan() :
    months = completed_orders_per_month.index.astype(str)
    completed_orders_values = completed_orders_per_month.values

    # Plot diagram batang dengan label dan warna yang diperbarui
    plt.figure(figsize=(14, 8))
    bars = plt.bar(months, completed_orders_values, color='skyblue')

    # Menambahkan label pada setiap batang
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval), ha='center', va='bottom', fontsize=8, color='black')

    plt.title('Jumlah Pesanan yang Sudah Diselesaikan setiap Bulan dari total pesanan pertahun')
    plt.xlabel('Bulan')
    plt.ylabel('Jumlah Pesanan')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45, ha='right')  # Untuk memutar label bulan agar lebih mudah dibaca
    plt.tight_layout()  # Untuk menghindari pemotongan label
    st.pyplot()



def analisis_sebaran_penjualan() :
    # Buat peta Folium
    peta = folium.Map(location=[-10.04, -55.28], zoom_start=4)
    # Tambahkan penanda untuk setiap baris data
    for index, row in data_geo_state.iterrows():
        folium.Marker(
            location=[row['geolocation_lat'], row['geolocation_lng']],
            popup=f"{row['geolocation_city']}, {row['geolocation_state']}",
            icon=folium.Icon(color='blue'),
            tooltip=f"City: {row['geolocation_city']}, State: {row['geolocation_state']}"
        ).add_to(peta)

    # Menampilkan peta di dalam aplikasi Streamlit
    folium_static(peta)

def analisis_pengiriman() :
    plt.figure(figsize=(12, 6))
    jumlah_pesanan_bulanan.plot(kind='line',marker='o',color='green')
    jumlah_pesanan_bulanan_garis = jumlah_pesanan_bulanan.mean()
    plt.axhline(y=jumlah_pesanan_bulanan_garis, color='red', linestyle='--', label='Rata-rata')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.title('Jumlah Pengiriman Pesanan Setiap Bulan')
    plt.xlabel('Bulan dan Tahun')
    plt.ylabel('Jumlah Pengiriman Pesanan')
    plt.xticks(rotation=45 )
    st.pyplot()



# Menghitung jumlah data untuk setiap kota
def analisis_prefiks():
    prefiks_count = geolocation_dataset.groupby('geolocation_state')['geolocation_zip_code_prefix'].count()

    # Membuat plot Bar Chart dengan grid garis
    fig, ax = plt.subplots(figsize=(12, 6))
    prefiks_count.sort_values().plot(kind='bar', color='blue', ax=ax)
    ax.set_xlabel('Negara')
    ax.set_ylabel('Jumlah Prefiks')
    ax.set_title('Jumlah Prefiks dengan Tiap Negara')

    # Menambahkan grid garis
    ax.grid(True, linestyle='--', alpha=0.7)

    # Menampilkan plot menggunakan Streamlit
    st.pyplot(fig)











with st.sidebar :
    selected = option_menu('Menu',['Dashboard'],
    icons =["easel2", "graph-up"],
    menu_icon="cast",
    default_index=0)

if (selected == 'Dashboard') :
    st.header(f"Dashboard Analisis E-Commerce Public Dataset")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Analisis Pengiriman", "Analisis Metode Pembayaran ", "Analisis Penjualan", "Analisis Sebaran Penjualan", "Analsis Pembayaran"])

with tab1:
    st.subheader("10122001 - Revi Faturahman")
    st.header('Grafik Pesanan Setiap Bulan')
    st.dataframe(jumlah_pesanan_bulanan)
    analisis_pengiriman()
    with st.expander("Penjelasan Pesanan Setiap Bulan"):
        st.write(
                """Grafik tersebut mencantumkan jumlah pelanggan yang melakukan pesanan pada setiap bulan tertentu. Sebagai contoh, pada bulan September 2016, ada 4 pelanggan yang melakukan pesanan. Namun, terdapat kekosongan data pada bulan November 2016, yang menandakan tidak adanya pesanan dari pelanggan pada bulan tersebut. Selanjutnya, jumlah pelanggan yang melakukan pesanan meningkat secara bertahap dari bulan ke bulan, mencapai puncaknya pada bulan November 2017 dengan 7544 pelanggan yang melakukan pesanan. Setelah itu, terjadi penurunan jumlah pesanan hingga bulan September 2018, di mana hanya ada 16 pelanggan yang melakukan pesanan. Hal ini menunjukkan pola penurunan dalam jumlah pesanan dari tahun 2017 hingga 2018. Perlu diperhatikan bahwa data bulan_pesanan mencakup rentang dari September 2016 hingga Oktober 2018.."""
                )
    st.header('Grafik Rata-Rata Pengiriman Pesanan Setiap Bulan')
    analisis_pengiriman_rata2()
    with st.expander("Penjelasan Rata-Rata Pengiriman Setiap Bulan"):
        st.write(
                """Data rata-rata waktu pengiriman pesanan per bulan menunjukkan variasi yang signifikan dari bulan ke bulan, dengan penurunan stabil yang terlihat dari September 2016 hingga Juli 2018. Namun, perlu diperhatikan bahwa pada bulan Desember 2016, terjadi penurunan yang dramatis dalam rata-rata waktu pengiriman, mengindikasikan kemungkinan perbaikan atau penyesuaian yang signifikan dalam proses pengiriman. Meskipun demikian, adanya anomali pada bulan September dan Oktober 2018, di mana terdapat nilai negatif yang tidak masuk akal dalam konteks waktu pengiriman, menunjukkan kemungkinan adanya kesalahan atau masalah teknis dalam pengumpulan atau pelaporan data. Oleh karena itu, diperlukan investigasi lebih lanjut untuk memahami penyebab anomali tersebut dan memastikan keakuratan data untuk analisis selanjutnya.."""
                )
with tab2:
    st.subheader('10122006 - Fadil Hardiyansyah')
    st.header('Grafik Tren metode pembayaran dari januari 2017 hingga januari 2018')
    st.dataframe(payment_trend)
    analisis_tren_pembayaran()
    with st.expander("Penjelasan Tren Penggunaan metode pembayaran dari januari 2017 hingga januari 2018"):
        st.write(
                """Selama periode Januari 2017 hingga Januari 2018, data menunjukkan adanya tren pertumbuhan yang signifikan dalam penggunaan berbagai metode pembayaran. Kartu kredit mendominasi dalam jumlah penggunaan, menunjukkan preferensi pelanggan untuk menggunakan metode ini dalam melakukan transaksi. Meskipun demikian, kartu debit dan voucher juga mengalami peningkatan penggunaan meskipun dengan fluktuasi yang lebih rendah. Fluktuasi bulanan dalam penggunaan metode pembayaran, khususnya terlihat pada penggunaan voucher yang mengalami penurunan pada bulan Desember 2017 sebelum meningkat kembali pada bulan Januari 2018, menekankan pentingnya pemantauan terus-menerus terhadap tren ini. Analisis ini memberikan pandangan yang berharga bagi perusahaan untuk memahami perilaku pembayaran pelanggan dan menyesuaikan strategi pembayaran mereka sesuai dengan kebutuhan pasar, dengan tujuan meningkatkan pengalaman pelanggan dan efisiensi layanan pembayaran.."""
                )
    
with tab3:
    st.subheader('10122013 - Hilmy Abdurrahman D')
    st.header('Grafik Perkembangan Penjualan Perbulan')
    st.dataframe(completed_orders_per_month)
    analisis_penjualan()
    with st.expander("Penjelasan Perkembangan Penjualan"):
        st.write(
                """Dilihat dari grafik diatas, terlihat dari proses pesanan yang sudah diselesaikan per bulan, terdapat 96.478 paket yang sudah diselesaikan, Puncak tertinggi terjadi pada bulan November 2017, di mana jumlah pesanan yang sudah diselesaikan mencapai 7,544. Peningkatan pesat ini bisa dipengaruhi oleh faktor musiman, penawaran khusus, atau peristiwa lain yang mendorong lonjakan pembelian. Terdapat tren pertumbuhan yang signifikan dalam jumlah pesanan yang sudah diselesaikan dari tahun 2016 hingga pertengahan 2018. Hal ini menunjukkan adanya peningkatan aktivitas pembelian atau mungkin strategi pemasaran yang efektif. Ada variasi jumlah pesanan yang sudah diselesaikan setiap bulan, namun secara umum terjadi peningkatan dari waktu ke waktu. Variabilitas ini bisa disebabkan oleh faktor-faktor seperti musim belanja, promosi tertentu, atau perubahan perilaku konsumen. pada bulan Desember 2016 dan Desember 2017, yang mungkin terkait dengan liburan tahun baru. Pengurangan aktivitas bisnis selama periode liburan ini adalah fenomena umum, dan perlu dipertimbangkan dalam perencanaan bisnis dan manajemen stok.."""
                )


with tab4:
    st.subheader('10122021 - Tijar Taufik Rahman')
    st.header('Grafik Sebaran Penjualan Berdasarkan Negara')
    st.dataframe(data_geo_state['geolocation_state'])
    analisis_sebaran_penjualan()
    with st.expander("Penjelasan Sebaran Pelanggan Negara"):
        st.write(
                """Grafik peta di atas adalah representasi visual yang menggambarkan sebaran pelanggan berdasarkan negara. Dengan menggunakan elemen-elemen peta, seperti titik atau wilayah berwarna, grafik ini memberikan gambaran geografis tentang lokasi pelanggan perusahaan di seluruh dunia.."""
                )
    st.header('Grafik Pelanggan Setiap Negara')
    analisis_prefiks()
    with st.expander("Penjelasan Grafik Pelanggan Setaip negara"):
        st.write(
                    """Grafik batang di atas memberikan representasi visual tentang sebaran pelanggan berdasarkan negara. Setiap batang pada grafik menggambarkan jumlah pelanggan di negara tertentu, dengan sumbu horizontal mewakili negara-negara yang terlibat dan sumbu vertikal mencerminkan jumlah pelanggan. Ukuran atau tinggi batang merepresentasikan seberapa besar kontribusi setiap negara terhadap total pelanggan. Dengan grafik ini, pemangku kepentingan dapat dengan mudah membandingkan jumlah pelanggan di berbagai negara, mengidentifikasi negara-negara dengan basis pelanggan yang signifikan, dan membuat keputusan berdasarkan distribusi pelanggan secara keseluruhan. ."""
                    )
with tab5:
    st.subheader('10122506 - Arya Ababil')
    st.header('Analisis Kredit')
    analisis_pembayaran()
    with st.expander("Penjelsan Analsis Kredit"):
        st.write(
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit
                    ,sed do eiusmod tempor incididunt ut labore et dolore magna
                    aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco
                    laborisnisi ut aliquip ex ea commodo consequat. Duis aute irure d
                    olorin reprehenderit in voluptate velit esse cillum dolore eu
                    fugiatnulla pariatur. Excepteur sint occaecat cupidatat non proi
                    dent,sunt in culpa qui officia deserunt mollit anim id est labo
                    rum."""
                )