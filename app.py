import streamlit as st
import pandas as pd
from scraper import scrape_bazos, scrape_realitymix  # убедись, что scraper.py в той же папке

st.set_page_config(page_title='Apartment Scraper', layout='wide')
st.title('🏠 Apartment Scraper Dashboard')

# Параметры
st.sidebar.header('Настройки')
sources = st.sidebar.multiselect(
    'Выбери сайты для парсинга',
    ['Bazos', 'RealityMix'],
    default=['Bazos', 'RealityMix']
)
keyword = st.sidebar.text_input('Ключевое слово (для Bazos)', '')
pages = st.sidebar.slider('Страниц Bazos', 1, 10, 2)

if st.sidebar.button('Запустить парсинг'):
    all_data = []
    if 'RealityMix' in sources:
        st.info('🔎 Scraping RealityMix...')
        all_data += scrape_realitymix()
    if 'Bazos' in sources:
        st.info('🔎 Scraping Bazos...')
        all_data += scrape_bazos(keyword=keyword, pages=pages)
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f'✅ Собрано {len(df)} объявлений')
        st.dataframe(df)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label='Скачать результаты в CSV',
            data=csv_data,
            file_name='output.csv',
            mime='text/csv'
        )
    else:
        st.warning('Ничего не найдено. Проверь настройки.')
