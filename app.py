import streamlit as st
import pandas as pd
from scraper import scrape_bazos, scrape_expats

st.set_page_config(page_title='Apartment Scraper', layout='wide')
st.title(' Apartment Scraper Dashboard')

# Sidebar
st.sidebar.header('Настройки')
sources = st.sidebar.multiselect(
    'Выбери сайты для парсинга',
    ['Bazos', 'Expats'],
    default=['Bazos', 'Expats']
)
keyword = st.sidebar.text_input('Ключевое слово (для Bazos)', '')
pages   = st.sidebar.slider('Страниц Bazos', 1, 10, 2)

if st.sidebar.button('Запустить парсинг'):
    all_data = []
    if 'Bazos' in sources:
        st.info('Scraping Bazos...')
        all_data += scrape_bazos(keyword=keyword, pages=pages)
    if 'Expats' in sources:
        st.info('🔎 Scraping Expats...')
        all_data += scrape_expats()

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f'✅ Собрано {len(df)} объявлений')
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button('📥 Скачать CSV', csv, 'output.csv', 'text/csv')
    else:
        st.warning('Ничего не найдено. Попробуй изменить фильтры или источники.')
