# importacion de librerias
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf

#titulo de la aplicacion (usando streamlit)
st.title('S&P 500 App')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# Web scraping de la informacion de s&p 500 en Wikipedia
@st.cache_data
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

# DataFrame
df = load_data()

# agrupamos por sectores empresariales.
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted( df['GICS Sector'].unique() )
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = df[ (df['GICS Sector'].isin(selected_sector)) ]

st.header('Display Companies in Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# 1) Descarga de la data utilizando la libreria yfinance
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# Descargar S&P500 data, basado en el siguiente link (funcion para descargar)
# https://pypi.org/project/yfinance/
# podemos ver el maximo, minimo, precio de apertura y cierre de cada ticker

data = yf.download(
        tickers = list(df_selected_sector[:10].Symbol),
        period = "ytd",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )

# 2) Crear funcion que segun el parametro de entrada (symbol) retorne un grafico
def price_plot(symbol): # argumento de entrada
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    
    # Crear figura y ejes explícitamente
    fig, ax = plt.subplots()
    
    ax.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
    ax.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
    ax.set_xticks(df.Date[::len(df)//10])  # Para no sobrecargar los xticks
    ax.set_xticklabels(df.Date[::len(df)//10], rotation=90)
    ax.set_title(symbol, fontweight='bold')
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Closing Price', fontweight='bold')
    
    # Pasar la figura creada a st.pyplot()
    st.pyplot(fig)

num_company = st.sidebar.slider('Number of Companies', 1, 5)

# 3) Bucle para que se muestren los plots segun el simbolo ingresado, utilizando la funcion

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)
