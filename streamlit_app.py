import streamlit as st
import gspread
import pandas as pd
import random
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_autorefresh import st_autorefresh
import time

# Обновление каждые 5 секунд
st_autorefresh(interval=5000, key="floor_war_timer")

st.set_page_config(page_title="Глобальный Терминал", layout="wide")

# CSS для атмосферы "Военного штаба"
st.markdown("""
    <style>
    [data-testid="stStatusWidget"], [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #050505; color: #E0E0E0; }
    
    .stock-card {
        background-color: #121212; border-radius: 10px; padding: 20px;
        border-left: 5px solid #333; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .status-tag {
        background-color: #222; color: #888; padding: 2px 8px;
        border-radius: 4px; font-size: 12px; margin-right: 5px;
    }
    .price-big { font-size: 48px; font-weight: bold; color: #FFFFFF; line-height: 1; }
    .delta-pos { color: #00FF41; font-weight: bold; }
    .delta-neg { color: #FF3131; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- Логика золота (Визуальный индекс рынка) ---
if 'gold' not in st.session_state: st.session_state.gold = 1200.0
st.session_state.gold = round(st.session_state.gold + random.uniform(-5, 5), 2)

@st.cache_data(ttl=2)
def load_game_data():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    stocks = pd.DataFrame(client.open("«Акции»").worksheet("Лист1").get_all_records())
    z_ref = pd.DataFrame(client.open("«Таблица дификаторы_заводские_проценты»").sheet1.get_all_records())
    r_ref = pd.DataFrame(client.open("Таблица «Модификаторы_региональные_проценты»").sheet1.get_all_records())
    return stocks, z_ref, r_ref

# ... (начало кода остается прежним: импорты, CSS, загрузка данных)

try:
    df_stocks, df_z_ref, df_r_ref = load_game_data()

    # --- ШАПКА (без изменений) ---
    t1, t2, t3 = st.columns([1, 1, 1])
    # ... твой код шапки ...

    st.write("---")

    # --- СТАБИЛЬНЫЙ ВЫВОД АКЦИЙ ---
    # Создаем один большой контейнер для всего рынка
    with st.container():
        active = df_stocks[df_stocks['Статус'] == "ОТКРЫТА"]
        
        # Вместо динамических колонок используем фиксированные
        col1, col2 = st.columns(2)
        
        for i, (idx, row) in enumerate(active.iterrows()):
            # Математика (оставляем твою логику)
            is_reg = "региональные" in str(row['Тип']).lower()
            m_h = get_pct(row.get('модификаторы', ''), [df_z_ref, df_r_ref])
            m_i = get_pct(row.get('I', ''), [df_z_ref, df_r_ref])
            gold_eff = ((st.session_state.gold - 1200) / 1200) * 100 if is_reg else 0.0
            
            g_val = 0
            try: g_val = float(str(row.get('% рандома', 0)).replace(',','.'))
            except: g_val = 0
            rnd = random.uniform(0, g_val) if g_val >= 0 else random.uniform(g_val, 0)
            
            total_pct = m_h + m_i + gold_eff + rnd
            base_p = float(str(row['Базовая цена']).replace('$',''))
            current_p = max(0, int(base_p * (1 + total_pct / 100)))
            border_color = "#3498DB" if not is_reg else "#F1C40F"

            # Выбираем колонку (левая или правая)
            target_col = col1 if i % 2 == 0 else col2
            
            # Отрисовываем карточку
            with target_col:
                # Обертка в empty() или container помогает избежать ошибки removeChild
                with st.container(border=False):
                    st.markdown(f"""
                    <div class="stock-card" style="border-left-color: {border_color}">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-size: 22px; font-weight: bold;">{row['Название']}</span>
                            <span class="{"delta-pos" if total_pct >= 0 else "delta-neg"}">
                                {total_pct:+.1f}%
                            </span>
                        </div>
                        <div class="price-big">{current_p}$</div>
                        <div style="margin-top: 10px; height: 30px; overflow: hidden;">
                            <span class="status-tag">{row.get('модификаторы', '')}</span>
                            <span class="status-tag">{row.get('I', '')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Важно: Кнопка должна иметь абсолютно уникальный ключ
                    st.button(f"КУПИТЬ {row['Название']}", key=f"buy_btn_{row['Название']}_{idx}")

except Exception as e:
    st.error(f"Ошибка связи с полем боя: {e}")
