import streamlit as st
import random
import time
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="🚀 Crash Simulator",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
body {
    background: radial-gradient(circle at bottom, #050014 0%, #090979 45%, #000000 100%);
}
.panel {
    background: rgba(0,0,0,0.55);
    padding: 16px;
    border-radius: 16px;
    box-shadow: 0 0 25px rgba(0,255,255,0.15);
    margin-bottom: 12px;
}
.rocket {
    font-size: 80px;
    animation: fly 0.5s infinite alternate;
}
@keyframes fly {
    from { transform: translateY(6px); }
    to { transform: translateY(-6px); }
}
.mult {
    font-size: 64px;
    font-weight: 800;
    color: #00ffd5;
}
.profit {
    font-size: 24px;
    color: #00ff7f;
}
.bonus {
    border: 2px solid #ffb703;
    padding: 10px;
    border-radius: 12px;
    background: linear-gradient(135deg, #ff006e, #ffbe0b);
    color: black;
    font-weight: 800;
    animation: pulse 1.2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 5px #ffbe0b; }
    50% { box-shadow: 0 0 25px #ffbe0b; }
    100% { box-shadow: 0 0 5px #ffbe0b; }
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
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
if "balance" not in st.session_state:
    st.session_state.balance = 50_000

if "bet" not in st.session_state:
    st.session_state.bet = 0

if "mult" not in st.session_state:
    st.session_state.mult = 1.00

if "crash_at" not in st.session_state:
    st.session_state.crash_at = 1.00

if "in_round" not in st.session_state:
    st.session_state.in_round = False

if "round_id" not in st.session_state:
    st.session_state.round_id = 0

if "history" not in st.session_state:
    st.session_state.history = []

if "fake_players" not in st.session_state:
    st.session_state.fake_players = []

if "big_wins" not in st.session_state:
    st.session_state.big_wins = []

# =========================================================
# HELPERS
# =========================================================
def generate_crash_point():
    r = random.random()
    return round(min(100.0, max(1.0, 1 / (1 - r))), 2)

def generate_fake_players():
    names = ["Alex", "Neo", "Vortex", "Max", "Shadow", "Nova", "Zero", "Flux"]
    players = []
    for _ in range(random.randint(6, 12)):
        players.append({
            "name": random.choice(names),
            "bet": random.randint(50, 5000),
            "cashout": round(random.uniform(1.1, random.uniform(2, 30)), 2)
        })
    return players

def add_big_win():
    mult = round(random.uniform(300, 900), 2)
    win = random.randint(100_000, 500_000)
    st.session_state.big_wins.insert(
        0,
        f"+{win}$ ×{mult}"
    )
    st.session_state.big_wins = st.session_state.big_wins[:8]

# =========================================================
# HEADER
# =========================================================
st.markdown("<h1 style='text-align:center;'>🚀 CRASH SIMULATOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.7;'>Continuous Virtual Rounds</p>", unsafe_allow_html=True)

# =========================================================
# LAYOUT
# =========================================================
left, center, right = st.columns([2,4,2])

# =========================================================
# LEFT — PLAYER PANEL
# =========================================================
with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown(f"💰 **Баланс:** {st.session_state.balance}$")

    bet = st.number_input(
        "Ставка",
        min_value=50,
        max_value=st.session_state.balance,
        step=50
    )

    if st.button("🚀 ВОЙТИ В РАУНД"):
        if not st.session_state.in_round:
            st.session_state.bet = bet
            st.session_state.balance -= bet

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel bonus'>", unsafe_allow_html=True)
    st.markdown("🎁 МЕГА БОНУС<br>150 ФРИ СПИНОВ<br>ТОЛЬКО СЕГОДНЯ", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# CENTER — GAME
# =========================================================
with center:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    if not st.session_state.in_round:
        st.session_state.in_round = True
        st.session_state.round_id += 1
        st.session_state.mult = 1.00
        st.session_state.crash_at = generate_crash_point()
        st.session_state.fake_players = generate_fake_players()

    profit = int(st.session_state.bet * st.session_state.mult)

    st.markdown("<div class='rocket'>🚀</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='mult'>x{st.session_state.mult:.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profit'>Профит: {profit}$</div>", unsafe_allow_html=True)

    if st.button("🟢 ЗАБРАТЬ"):
        win = int(st.session_state.bet * st.session_state.mult)
        st.session_state.balance += win
        st.session_state.bet = 0

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# RIGHT — TABLES
# =========================================================
with right:
    st.markdown("<div class='panel'><b>👥 Игроки в раунде</b><br>", unsafe_allow_html=True)
    for p in st.session_state.fake_players:
        st.markdown(f"{p['name']} — {p['bet']}$", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'><b>🏆 Крупные выигрыши</b><br>", unsafe_allow_html=True)
    for w in st.session_state.big_wins:
        st.markdown(w, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# ROUND PROGRESSION
# =========================================================
time.sleep(0.35)
st.session_state.mult *= 1.035
st.session_state.mult = round(st.session_state.mult, 2)

if st.session_state.mult >= st.session_state.crash_at:
    st.session_state.history.insert(0, st.session_state.crash_at)
    st.session_state.history = st.session_state.history[:12]
    if random.random() < 0.35:
        add_big_win()
    st.session_state.in_round = False
    st.session_state.bet = 0

st.rerun()
