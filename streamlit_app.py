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

try:
    df_stocks, df_z_ref, df_r_ref = load_game_data()

    def get_pct(val, refs):
        if not val or str(val).strip() == "": return 0.0
        val_s = str(val).strip().lower()
        for ref in refs:
            for _, row in ref.iterrows():
                full = f"{row['Тип']} {row['Значение']}".strip().lower()
                if val_s == full or val_s == str(row['Значение']).lower():
                    return float(str(row['%']).replace('%','').replace(',','.'))
        return 0.0

    # Шапка с таймером
    t1, t2, t3 = st.columns([1, 1, 1])
    with t1:
        st.markdown(f"### 🎖️ Золотой стандарт\n## {st.session_state.gold}$")
    with t2:
        # Простой визуальный таймер (циклический на 10 мин)
        mins = (int(time.time()) // 60) % 10
        secs = 60 - (int(time.time()) % 60)
        st.markdown(f"### ⏳ Доход через\n## {9-mins:02d}:{secs:02d}")
    with t3:
        st.markdown("### 🏟️ Локация\n## Игровое поле")

    st.write("---")

    # Отображение акций
    active = df_stocks[df_stocks['Статус'] == "ОТКРЫТА"]
    grid = st.columns(2) # Две колонки, чтобы карточки были крупными

    for i, (idx, row) in enumerate(active.iterrows()):
        # Расчет
        is_reg = "региональные" in str(row['Тип']).lower()
        m_h = get_pct(row.get('модификаторы', ''), [df_z_ref, df_r_ref])
        m_i = get_pct(row.get('I', ''), [df_z_ref, df_r_ref])
        
        # Золото влияет только на регионы
        gold_eff = ((st.session_state.gold - 1200) / 1200) * 100 if is_reg else 0.0
        
        # Твой кастомный рандом из колонки G
        g_val = 0
        try: g_val = float(str(row.get('% рандома', 0)).replace(',','.'))
        except: g_val = 0
        rnd = random.uniform(0, g_val) if g_val >= 0 else random.uniform(g_val, 0)
        
        total_pct = m_h + m_i + gold_eff + rnd
        base_p = float(str(row['Базовая цена']).replace('$',''))
        current_p = max(0, int(base_p * (1 + total_pct / 100)))

        # Цвет карточки в зависимости от типа
        border_color = "#3498DB" if not is_reg else "#F1C40F"
        
        with grid[i % 2]:
            st.markdown(f"""
            <div class="stock-card" style="border-left-color: {border_color}">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 24px; font-weight: bold;">{row['Название']}</span>
                    <span class="{"delta-pos" if total_pct >= 0 else "delta-neg"}">
                        {"+" if total_pct > 0 else ""}{total_pct:.1f}%
                    </span>
                </div>
                <div class="price-big">{current_p}$</div>
                <div style="margin-top: 10px;">
                    <span class="status-tag">{row.get('модификаторы', 'Нет событий')}</span>
                    <span class="status-tag">{row.get('I', '')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.warning("Ожидание сигнала от штаба...")
