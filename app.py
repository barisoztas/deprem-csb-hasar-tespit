import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

@st.cache
def data():
    df = pd.read_csv("data/bina_tespit.csv")
    df = df.round(1)
    return df
df = data()

st.title("Çevre ve Şehircilik Bakanlığı - Hasar Tespit")

st.write(
    """Bu uygulama https://hasartespit.csb.gov.tr/ sitesindeki hasar tespiti yapılan binaların durumunu göstermek amacıyla yapılmıştır.
    """
)
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


    filtre_il = st.multiselect("İl Seçiniz: ",iller)


    if filtre_il:
        df = df[df["il"].isin(filtre_il)]
        ilceler = df["ilce"].unique().tolist()
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
    
st.write("Bina Sayıları: ")

df_pivot = df.pivot_table(values="binaNo",index=["il","ilce","mahalle"],columns="aciklama",aggfunc="count").fillna(0)
st.write(df_pivot.style.format(precision=0))

st.write("Binalar: ")
st.write(df)
