import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import HeatMap


# eklenilen page_title ile sekme ismi 'Deprem Hasar Tespiti olarak gorunecektir.'
st.set_page_config(layout="wide",
       page_title="Deprem Hasar Tespit",
        )

def il_kordinat():
    df = pd.read_csv("data/il_kordinatlari.csv", delimiter=',', names = ["il", "lon", "lat"])
    return df
il_kordinatlari = il_kordinat()


@st.cache_data
def data():
    df = pd.read_csv("data/bina_tespit.csv")
    df = df.round(1)
    return df
df = data()

@st.cache_data
def data_hatay():
    df = pd.read_csv("data/hatay_geocode.csv")
    df = df[df["x"].isna()==False]
    return df

def clear_multi():
    st.session_state.filtreler = []
    return

hatay = data_hatay()
m = folium.Map(location = [36.44, 36.25], zoom_start=9)
# altlik harita olarak Google Satellite Label kullanildi. Bu sayede
# isi haritasindan gecmis ile hasar goren binalar karsilastirilabilir.
googleMaps = folium.TileLayer(
        tiles='http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}',
        attr='Google Terrain',
        name='Google Satellite',
        overlay=True,
        show=True
        ).add_to(m)



st.title("Çevre ve Şehircilik Bakanlığı - Hasar Tespit")

st.write("illere göre hasar tespit durumu: ")
df_il_pivot = df.pivot_table(values="ilce",index="il",columns="aciklama",aggfunc="count").round(0).fillna(0)
df_il_pivot = df_il_pivot[['Yıkık','Acil Yıktırılacak', 'Ağır Hasarlı','Az Hasarlı', 'Hasarsız','Tespit Yapılamadı',
       'Bina Kilitli İnceleme Yapılamadı (Girilemedi)', 
        'Değerlendirme Dışı',  'Kapsam Dışı']]
st.dataframe(df_il_pivot.style.format(precision=0))

with st.sidebar:
    iller = df["il"].unique().tolist()

    filtre_ilce = None
    filtre_mah = None
    filtre_durum = None
    durumlar = df["aciklama"].unique().tolist()


    filtre_il = st.multiselect("İl Seçiniz: ",iller, key="filtreler")


    if filtre_il:
        df = df[df["il"].isin(filtre_il)]
        ilceler = df["ilce"].unique().tolist()
        # il koordinatlari csv dosyasindan secilen ilin lon ve lat bilgilerini
        # alip haritayi update ediyor.
        # simdilik diger illerin isi haritasi olmadigi icin asagidaki
        # 3 satir kodu commentleyebilirsiniz.
        lon = il_kordinatlari[il_kordinatlari["il"].isin(filtre_il)]["lon"]
        lat = il_kordinatlari[il_kordinatlari["il"].isin(filtre_il)]["lat"]
        m = folium.Map(location = [lon, lat], zoom_start=9)
        
        filtre_ilce = st.multiselect("İlçe Seçiniz: ",ilceler)
    

    if filtre_ilce:
        df = df[df["ilce"].isin(filtre_ilce)]
        mahalleler = df["mahalle"].unique().tolist()
        filtre_mah = st.multiselect("Mahalle Seçiniz: ",mahalleler)



    if filtre_mah:
        df = df[df["mahalle"].isin(filtre_mah)]
        durumlar = df["aciklama"].unique().tolist()



    filtre_durum = st.multiselect("Bina Durumu: ",durumlar)
    if filtre_durum:
        df = df[df["aciklama"].isin(filtre_durum)]


    #create your button to clear the state of the multiselect
    st.button("Filtreleri temizle", on_click=clear_multi)
    
st.write("Bina Sayıları: ")

df_pivot = df.pivot_table(values="binaNo",index=["il","ilce","mahalle"],columns="aciklama",aggfunc="count").fillna(0)
st.write(df_pivot.style.format(precision=0))

st.write("Hatay: Ağır Hasarlı, Yıkık, Acil Yıkılacak olarak hasar tespiti yapılan binalar.")

coor = [[i["y"],i["x"]] for _,i in hatay.iterrows()]
HeatMap(coor,radius=18, name = "Sicaklik Haritasi").add_to(m)
folium.LayerControl().add_to(m)


st.sidebar.info(
    """
Bu uygulama https://hasartespit.csb.gov.tr/ sitesindeki hasar tespiti yapılan binaların durumunu göstermek amacıyla yapılmıştır.

Çevre ve Şehircilik Bakanlığının hasar tespiti yaptığı binaların durumunu gösteren bir panel yaptım. İl, ilçe, mahalle, bina durumunu seçerek bilgileri görebilirsiniz.

Özellikle #Hatay ilinde yıkık, acil yıkılacak ve ağır hasarlı olarak tespit edilen binaları geocoding işlemi ile konumlarını ekledim. Alttaki haritada heatmap oluşturdum.

Bakanlığın verileri güncellendikçe eklemeye devam edeceğim. 18-02-2023 tarihinde aldığım verilere göre panel oluşturdum.

Verilere aşağıdaki github linkinden ulaşabilirsiniz.
https://github.com/savasalturk/deprem-csb-hasar-tespit

"""
)        


html = m.get_root().render()
components.html(html,height= 500,scrolling=False)
