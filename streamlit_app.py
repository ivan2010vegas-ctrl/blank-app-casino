import streamlit as st
import gspread
import pandas as pd
import random
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_autorefresh import st_autorefresh
import time
import os

# 1. Авто-обновление
st_autorefresh(interval=5000, key="floor_war_v5")

st.set_page_config(page_title="Военный Терминал", layout="wide")

# CSS (Оставляем твой крутой стиль)
st.markdown("""
    <style>
    [data-testid="stStatusWidget"], [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #050505; color: #E0E0E0; }
    .stock-card {
        background-color: #121212; border-radius: 10px; padding: 20px;
        border-left: 5px solid #333; margin-bottom: 20px;
    }
    .status-tag { background-color: #222; color: #888; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }
    .price-big { font-size: 44px; font-weight: bold; color: #FFFFFF; }
    .delta-pos { color: #00FF41; font-weight: bold; }
    .delta-neg { color: #FF3131; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Функция для поиска процентов
def get_pct(val, refs):
    if not val or str(val).strip() == "": return 0.0
    val_s = str(val).strip().lower()
    for ref in refs:
        if 'Значение' in ref.columns and 'Тип' in ref.columns:
            for _, row in ref.iterrows():
                full = f"{row['Тип']} {row['Значение']}".strip().lower()
                if val_s == full or val_s == str(row['Значение']).lower():
                    return float(str(row['%']).replace('%','').replace(',','.'))
    return 0.0

# 2. Загрузка данных с проверкой
@st.cache_data(ttl=2)
def load_game_data():
    if not os.path.exists("credentials.json"):
        st.error("❌ Файл credentials.json не найден в репозитории!")
        return None, None, None
    
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        
        stocks = pd.DataFrame(client.open("«Акции»").worksheet("Лист1").get_all_records())
        z_ref = pd.DataFrame(client.open("«Таблица дификаторы_заводские_проценты»").sheet1.get_all_records())
        r_ref = pd.DataFrame(client.open("Таблица «Модификаторы_региональные_проценты»").sheet1.get_all_records())
        return stocks, z_ref, r_ref
    except Exception as e:
        st.error(f"❌ Ошибка доступа к Google Таблицам: {e}")
        return None, None, None

# --- ГЛАВНЫЙ ЦИКЛ ---
df_stocks, df_z_ref, df_r_ref = load_game_data()

if df_stocks is not None:
    # Логика золота
    if 'gold' not in st.session_state: st.session_state.gold = 1200.0
    st.session_state.gold = round(st.session_state.gold + random.uniform(-3, 3), 2)

    # Шапка
    col_a, col_b = st.columns([1, 1])
    with col_a: st.metric("Золото", f"{st.session_state.gold}$")
    with col_b: 
        secs = 60 - (int(time.time()) % 60)
        st.metric("Доход через", f"00:{secs:02d}")

    st.write("---")

    # Акции
    active = df_stocks[df_stocks['Статус'] == "ОТКРЫТА"]
    c1, c2 = st.columns(2)

    for i, (idx, row) in enumerate(active.iterrows()):
        is_reg = "региональные" in str(row['Тип']).lower()
        m_h = get_pct(row.get('модификаторы', ''), [df_z_ref, df_r_ref])
        m_i = get_pct(row.get('I', ''), [df_z_ref, df_r_ref])
        gold_eff = ((st.session_state.gold - 1200) / 1200) * 100 if is_reg else 0.0
        
        g_val = 0
        try: g_val = float(str(row.get('% рандома', 0)).replace(',','.'))
        except: g_val = 0
        rnd = random.uniform(0, g_val) if g_val >= 0 else random.uniform(g_val, 0)
        
        total_pct = m_h + m_i + gold_eff + rnd
        base_p = float(str(row.get('Базовая цена', 100)).replace('$',''))
        current_p = max(0, int(base_p * (1 + total_pct / 100)))
        
        target = c1 if i % 2 == 0 else c2
        with target:
            st.markdown(f"""
            <div class="stock-card" style="border-left-color: {'#F1C40F' if is_reg else '#3498DB'}">
                <div style="display: flex; justify-content: space-between;">
                    <b>{row['Название']}</b>
                    <span class="{"delta-pos" if total_pct >= 0 else "delta-neg"}">{total_pct:+.1f}%</span>
                </div>
                <div class="price-big">{current_p}$</div>
                <div style="font-size:12px; color:#666;">{row.get('модификаторы', '')} | {row.get('I', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"КУПИТЬ {row['Название']}", key=f"btn_{idx}"):
                st.toast(f"Запрос на покупку {row['Название']} отправлен!")
else:
    st.info("💡 Проверь логи приложения (Manage app), чтобы увидеть детальную ошибку.")
