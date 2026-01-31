import streamlit as st
import random
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="🚀 Rocket Crash",
    page_icon="🚀",
    layout="centered"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at bottom, #020024 0%, #090979 40%, #000000 100%);
}
.rocket {
    font-size: 60px;
    animation: fly 1s infinite alternate;
}
@keyframes fly {
    from { transform: translateY(10px); }
    to { transform: translateY(-10px); }
}
.mult {
    font-size: 48px;
    font-weight: bold;
    color: #00ffcc;
}
.profit {
    font-size: 24px;
    color: #00ff00;
}
.history {
    font-size: 18px;
}
.card {
    background-color: rgba(0,0,0,0.4);
    padding: 15px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "balance" not in st.session_state:
    st.session_state.balance = 5000

if "active" not in st.session_state:
    st.session_state.active = False

if "bet" not in st.session_state:
    st.session_state.bet = 0

if "mult" not in st.session_state:
    st.session_state.mult = 1.00

if "crash_at" not in st.session_state:
    st.session_state.crash_at = 1.00

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>🚀 ROCKET CRASH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Жадность убивает</p>", unsafe_allow_html=True)

# ---------------- BALANCE ----------------
st.markdown(f"""
<div class="card">
💰 <b>Баланс:</b> {st.session_state.balance} $
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------- BET INPUT ----------------
if not st.session_state.active:
    bet = st.number_input(
        "💸 Ставка",
        min_value=10,
        max_value=st.session_state.balance,
        step=10
    )

    if st.button("🚀 Запуск"):
        st.session_state.bet = bet
        st.session_state.balance -= bet
        st.session_state.mult = 1.00
        st.session_state.crash_at = round(random.uniform(1.00, 100.00), 2)
        st.session_state.active = True
        st.rerun()

# ---------------- GAME LOOP ----------------
if st.session_state.active:
    profit = int(st.session_state.bet * st.session_state.mult)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='rocket'>🚀</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='mult'>x{st.session_state.mult:.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profit'>Прибыль: {profit} $</div>", unsafe_allow_html=True)

    cashout = st.button("🟢 Забрать")

    if cashout:
        win = int(st.session_state.bet * st.session_state.mult)
        st.session_state.balance += win
        st.session_state.history.insert(0, round(st.session_state.mult, 2))
        st.session_state.history = st.session_state.history[:10]
        st.session_state.active = False
        st.success(f"✅ Вы забрали {win} $")
        st.rerun()

    # рост множителя
    st.session_state.mult += random.uniform(0.03, 0.15)
    st.session_state.mult = min(st.session_state.mult, 100.00)

    time.sleep(0.25)

    # взрыв
    if st.session_state.mult >= st.session_state.crash_at:
        st.session_state.history.insert(0, round(st.session_state.crash_at, 2))
        st.session_state.history = st.session_state.history[:10]
        st.session_state.active = False
        st.error(f"💥 ВЗРЫВ НА x{st.session_state.crash_at:.2f}")
        st.rerun()

    st.rerun()

# ---------------- HISTORY ----------------
st.write("")
st.markdown("<div class='card'><b>📜 История иксов</b></div>", unsafe_allow_html=True)

if st.session_state.history:
    st.markdown(
        "<div class='history'>" +
        ", ".join([f"x{h:.2f}" for h in st.session_state.history]) +
        "</div>",
        unsafe_allow_html=True
    )
else:
    st.caption("Пока пусто")

# ---------------- RULES ----------------
with st.expander("📘 Правила"):
    st.markdown("""
- Множитель растёт от **x1.00 до x100.00**
- Взрыв происходит **в абсолютно случайный момент**
- Можно забрать прибыль **в любой момент**
- Не успел — ставка сгорает
""")
