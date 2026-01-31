import streamlit as st
import random
import time
import math

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="🚀 Rocket Crash Casino",
    page_icon="🚀",
    layout="centered"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at bottom, #050014 0%, #090979 40%, #000000 100%);
}
.game-box {
    background: rgba(0,0,0,0.55);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 0 30px rgba(0,255,255,0.15);
}
.rocket {
    font-size: 70px;
    animation: fly 0.6s infinite alternate;
}
@keyframes fly {
    from { transform: translateY(8px); }
    to { transform: translateY(-8px); }
}
.mult {
    font-size: 56px;
    font-weight: 800;
    color: #00ffd5;
}
.profit {
    font-size: 26px;
    color: #00ff7f;
}
.history span {
    padding: 4px 8px;
    border-radius: 8px;
    margin-right: 6px;
    font-weight: bold;
}
.low { background: #2b2b2b; color: #aaa; }
.mid { background: #1f4fff; color: white; }
.high { background: #ff2d55; color: white; }
.balance {
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- STATE ----------------
if "balance" not in st.session_state:
    st.session_state.balance = 10_000

if "in_game" not in st.session_state:
    st.session_state.in_game = False

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
st.markdown("<p style='text-align:center; opacity:0.7;'>Virtual Casino Mode</p>", unsafe_allow_html=True)

# ---------------- BALANCE ----------------
st.markdown(f"""
<div class="game-box balance">
💰 Баланс: <b>{st.session_state.balance}$</b>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------- BET PANEL ----------------
if not st.session_state.in_game:
    st.markdown("<div class='game-box'>", unsafe_allow_html=True)

    bet = st.number_input(
        "💸 Ставка",
        min_value=10,
        max_value=st.session_state.balance,
        step=10
    )

    if st.button("🚀 СТАРТ"):
        st.session_state.bet = bet
        st.session_state.balance -= bet
        st.session_state.mult = 1.00

        # 🔥 ЧЕСТНЫЙ КАЗИНО-РАСПРЕДЕЛЕНИЕ
        r = random.random()
        st.session_state.crash_at = round(
            min(100.0, max(1.0, 1 / (1 - r))), 2
        )

        st.session_state.in_game = True
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- GAME LOOP ----------------
if st.session_state.in_game:
    profit = int(st.session_state.bet * st.session_state.mult)

    st.markdown("<div class='game-box'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown("<div class='rocket'>🚀</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='mult'>x{st.session_state.mult:.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profit'>Профит: {profit}$</div>", unsafe_allow_html=True)

    cashout = st.button("🟢 ЗАБРАТЬ")

    if cashout:
        win = int(st.session_state.bet * st.session_state.mult)
        st.session_state.balance += win
        st.session_state.history.insert(0, round(st.session_state.mult, 2))
        st.session_state.history = st.session_state.history[:12]
        st.session_state.in_game = False
        st.success(f"✅ Вы выиграли {win}$")
        st.rerun()

    # 🚀 РОСТ МНОЖИТЕЛЯ (как в казино)
    st.session_state.mult *= 1.035
    st.session_state.mult = round(st.session_state.mult, 2)

    time.sleep(0.25)

    if st.session_state.mult >= st.session_state.crash_at:
        st.session_state.history.insert(0, st.session_state.crash_at)
        st.session_state.history = st.session_state.history[:12]
        st.session_state.in_game = False
        st.error(f"💥 ВЗРЫВ НА x{st.session_state.crash_at:.2f}")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.rerun()

# ---------------- HISTORY ----------------
st.write("")
st.markdown("<div class='game-box'><b>📜 История раундов</b><br><br>", unsafe_allow_html=True)

if st.session_state.history:
    hist_html = "<div class='history'>"
    for h in st.session_state.history:
        if h < 2:
            cls = "low"
        elif h < 10:
            cls = "mid"
        else:
            cls = "high"
        hist_html += f"<span class='{cls}'>x{h:.2f}</span>"
    hist_html += "</div>"
    st.markdown(hist_html, unsafe_allow_html=True)
else:
    st.caption("Нет данных")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RULES ----------------
with st.expander("📘 Как в настоящем казино"):
    st.markdown("""
- Множитель растёт **экспоненциально**
- Взрыв вычисляется **до начала раунда**
- Можно забрать в любой момент
- Все деньги **виртуальные**
""")
