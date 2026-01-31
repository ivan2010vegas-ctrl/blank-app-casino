import streamlit as st
import random
import time

# ----------------------------
# НАСТРОЙКИ СТРАНИЦЫ
# ----------------------------
st.set_page_config(
    page_title="🎲 Dice Casino",
    page_icon="🎲",
    layout="centered"
)

# ----------------------------
# СТИЛИ
# ----------------------------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0b1d2b, #000000);
    color: white;
}
.block {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 0 25px rgba(0,255,255,0.15);
    margin-bottom: 20px;
}
.big {
    font-size: 28px;
    font-weight: bold;
}
.center {
    text-align: center;
}
.history {
    letter-spacing: 3px;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# СОСТОЯНИЯ
# ----------------------------
if "balance" not in st.session_state:
    st.session_state.balance = 10_000

if "history" not in st.session_state:
    st.session_state.history = []

# ----------------------------
# КОЭФФИЦИЕНТЫ
# ----------------------------
MORE_COEFS = {
    3: 1.05,
    5: 1.25,
    7: 1.8,
    9: 3.2,
    10: 4.8,
    11: 15.0
}

EXACT_COEFS = {
    2: 36,
    3: 18,
    4: 12,
    5: 8,
    6: 6,
    7: 5,
    8: 6,
    9: 8,
    10: 12,
    11: 18,
    12: 36
}

# ----------------------------
# ЗАГОЛОВОК
# ----------------------------
st.markdown("<h1 class='center'>🎲 DICE CASINO</h1>", unsafe_allow_html=True)
st.markdown("<p class='center'>Виртуальная симуляция казино</p>", unsafe_allow_html=True)

# ----------------------------
# БАЛАНС
# ----------------------------
st.markdown(f"""
<div class="block center big">
💰 Баланс: {st.session_state.balance:,} $
</div>
""", unsafe_allow_html=True)

# ----------------------------
# ФОРМА СТАВКИ
# ----------------------------
with st.form("bet_form"):
    st.markdown("### 🎯 Сделай ставку")

    bet_amount = st.number_input(
        "Сумма ставки",
        min_value=100,
        max_value=st.session_state.balance,
        step=100
    )

    bet_type = st.selectbox(
        "Тип ставки",
        ["Больше", "Меньше", "Точно"]
    )

    if bet_type in ["Больше", "Меньше"]:
        value = st.selectbox("Выбери значение", list(MORE_COEFS.keys()))
        coef = MORE_COEFS[value]
    else:
        value = st.selectbox("Выбери сумму", list(EXACT_COEFS.keys()))
        coef = EXACT_COEFS[value]

    st.markdown(f"**Коэффициент:** x{coef}")

    submit = st.form_submit_button("🎲 БРОСИТЬ КОСТИ")

# ----------------------------
# ЛОГИКА ИГРЫ
# ----------------------------
if submit:
    if bet_amount > st.session_state.balance:
        st.error("Недостаточно средств")
    else:
        st.session_state.balance -= bet_amount

        with st.spinner("🎲 Кости летят..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2

        win = False

        if bet_type == "Больше":
            win = total > value
        elif bet_type == "Меньше":
            win = total < value
        else:
            win = total == value

        st.markdown(f"""
        <div class="block center">
        🎲 Выпало: <span class="big">{dice1} + {dice2} = {total}</span>
        </div>
        """, unsafe_allow_html=True)

        if win:
            profit = int(bet_amount * coef)
            st.session_state.balance += profit
            st.success(f"🎉 ВЫИГРЫШ! +{profit:,} $")
        else:
            st.error("💥 ПРОИГРЫШ")

        st.session_state.history.append(total)
        st.session_state.history = st.session_state.history[-10:]

# ----------------------------
# ИСТОРИЯ
# ----------------------------
if st.session_state.history:
    st.markdown("""
    <div class="block center">
    <h3>📈 История бросков</h3>
    <div class="history">
    """ + " · ".join(map(str, st.session_state.history)) + """
    </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# ПРЕДУПРЕЖДЕНИЕ
# ----------------------------
st.markdown("""
<p class="center" style="opacity:0.5;">
🎮 Это игровая симуляция. Все деньги виртуальны.
</p>
""", unsafe_allow_html=True)
