import streamlit as st
import random
import time

# ----------------------------
# НАСТРОЙКИ
# ----------------------------
st.set_page_config(
    page_title="🚀 Ракетка",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 Ракетка — зона риска")
st.caption("Чем выше летишь — тем больнее падать")

st.divider()

# ----------------------------
# SESSION STATE
# ----------------------------
if "balance" not in st.session_state:
    st.session_state.balance = 5000

if "rocket_active" not in st.session_state:
    st.session_state.rocket_active = False

if "multiplier" not in st.session_state:
    st.session_state.multiplier = 1.0

if "crash_at" not in st.session_state:
    st.session_state.crash_at = 0.0

if "bet" not in st.session_state:
    st.session_state.bet = 0

# ----------------------------
# БАЛАНС
# ----------------------------
st.subheader(f"💰 Баланс: {st.session_state.balance} $")

# ----------------------------
# СТАВКА
# ----------------------------
if not st.session_state.rocket_active:
    bet = st.number_input(
        "💸 Введите ставку",
        min_value=10,
        max_value=st.session_state.balance,
        step=10
    )

    if st.button("🚀 Запустить ракету"):
        if bet > 0:
            st.session_state.bet = bet
            st.session_state.balance -= bet
            st.session_state.multiplier = 1.0
            st.session_state.crash_at = random.uniform(1.5, 6.0)
            st.session_state.rocket_active = True
            st.rerun()

# ----------------------------
# РАКЕТА В ПОЛЁТЕ
# ----------------------------
if st.session_state.rocket_active:
    st.subheader("🚀 Ракета в полёте")

    placeholder = st.empty()
    progress = st.progress(0)

    cashout = st.button("🟢 Забрать прибыль")

    if cashout:
        win = int(st.session_state.bet * st.session_state.multiplier)
        st.session_state.balance += win
        st.session_state.rocket_active = False
        st.success(f"✅ Вы забрали {win} $")
        st.rerun()

    # рост ракеты
    st.session_state.multiplier += random.uniform(0.05, 0.12)
    progress.progress(min(st.session_state.multiplier / st.session_state.crash_at, 1.0))

    placeholder.markdown(
        f"""
        <div style="text-align:center; font-size:40px;">
            🚀 x{st.session_state.multiplier:.2f}
        </div>
        """,
        unsafe_allow_html=True
    )

    time.sleep(0.35)

    # ВЗРЫВ
    if st.session_state.multiplier >= st.session_state.crash_at:
        st.session_state.rocket_active = False
        st.error("💥 РАКЕТА ВЗОРВАЛАСЬ! Ставка сгорела")
        st.rerun()

    st.rerun()

# ----------------------------
# ПРАВИЛА
# ----------------------------
st.divider()
with st.expander("📜 Правила"):
    st.markdown("""
- Введите ставку и запустите ракету  
- Множитель растёт со временем  
- В любой момент можно забрать прибыль  
- Ракета взрывается **в случайный момент**  
- Если не успел — ставка сгорает  
""")
