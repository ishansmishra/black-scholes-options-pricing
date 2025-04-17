import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="Black-Scholes Model", layout="centered")
st.title("📈 Black-Scholes Option Pricing Model")

with st.sidebar:
    st.header("🧮 Input Parameters")

    col1, col2 = st.columns(2)
    with col1:
        spot_price = st.number_input("Spot Price", min_value=0.0, value=100.0)
        strike_price = st.number_input("Strike Price", min_value=0.0, value=100.0)
    with col2:
        time = st.number_input("Time (years)", min_value=0.0, value=1.0, step=0.01)
        option_type = st.selectbox("Option Type", ("call", "put"))

    rate_of_interest = st.slider("Risk-Free Interest Rate (%)", 0.0, 15.0, 5.0, 0.1) / 100
    ticker = st.text_input("📉 Ticker Symbol (for volatility)", value="AAPL")
    use_hist_vol = st.checkbox("Use Historical Volatility")
    if use_hist_vol and ticker:
        with st.spinner("Fetching historical volatility..."):
            try:
                hist_vol_url = f"http://backend:8000/historical-volatility/{ticker}"
                hist_response = requests.get(hist_vol_url)
                if hist_response.status_code == 200:
                    volatility = hist_response.json()["historical_volatility"]
                    st.success(f"Historical Volatility: {volatility:.2%}")
                else:
                    st.warning("Failed to fetch historical volatility.")
            except Exception as e:
                st.warning(f"Error fetching volatility: {e}")
    if not use_hist_vol:
        volatility = st.slider("Volatility (%)", 0.0, 100.0, 20.0, 0.1) / 100

    calculate = st.button("📊 Calculate")

if calculate:
    try:
        payload = {
            "spot_price": spot_price,
            "strike_price": strike_price,
            "time": time,
            "rate_of_interest": rate_of_interest,
            "volatility": volatility,
            "option_type": option_type
        }

        response = requests.post("http://backend:8000/option", json=payload)

        if response.status_code == 200:
            result = response.json()
            price = result["price"]
            greeks = result["greeks"]
            analysis = result["analysis"]
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            st.stop()

    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        st.stop()

    st.subheader("💰 Option Price")
    st.metric(label="Option Price", value=f"${price:.2f}")

    with st.expander("📉 Option Greeks", expanded=True):
        greek_cols = st.columns(3)
        greek_names = list(greeks.keys())
        for i, col in enumerate(greek_cols):
            for j in range(i, len(greek_names), 3):
                col.metric(label=greek_names[j].capitalize(), value=f"{greeks[greek_names[j]]:.4f}")


    with st.expander("🔍 Option Analysis", expanded=False):
        st.write(f"**Probability of expiring ITM:** {analysis['probability_in_the_money']:.2%}")
        st.write(f"**Breakeven Price:** ${analysis['breakeven_price']:.2f}")
        st.write(f"**Max Profit:** {analysis['max_profit']}")
        st.write(f"**Max Loss:** {analysis['max_loss']}")

    with st.expander("📊 Option Price vs. Strike Price"):
        strike_range = np.linspace(0.5 * spot_price, 1.5 * spot_price, 100)

        prices = []
        for k in strike_range:
            temp_payload = payload.copy()
            temp_payload["strike_price"] = float(k)
            try:
                r = requests.post("http://backend:8000/option", json=temp_payload)
                prices.append(r.json()["price"] if r.status_code == 200 else None)
            except:
                prices.append(None)

        fig, ax = plt.subplots()
        ax.plot(strike_range, prices, label=f"{option_type.capitalize()} Option", color='blue', linewidth=2)
        ax.axvline(x=strike_price, color='red', linestyle='--', label='Input Strike Price')
        ax.set_title("Option Price vs Strike Price")
        ax.set_xlabel("Strike Price")
        ax.set_ylabel("Option Price")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
