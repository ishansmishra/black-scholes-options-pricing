from fastapi import FastAPI
from pydantic import BaseModel
from bs_model import black_scholes_price, black_scholes_greeks, black_scholes_analysis
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import numpy as np
from fastapi import HTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptionInput(BaseModel):
    spot_price: float
    strike_price: float
    time: float
    rate_of_interest: float
    volatility: float
    option_type: str  # "call" or "put"

@app.post("/option")
def get_option_details(option: OptionInput):
    price = black_scholes_price(**option.dict())
    greeks = black_scholes_greeks(**option.dict())
    analysis = black_scholes_analysis(**option.dict())

    return {
        "price": price,
        "greeks": greeks,
        "analysis": analysis
    }

@app.get("/historical-volatility/{ticker}")
def get_historical_volatility(ticker: str, window: int = 30):
    try:
        data = yf.download(ticker, period='6mo', interval='1d')
        if data.empty or 'Adj Close' not in data:
            raise HTTPException(status_code=404, detail="No valid data found for ticker.")

        close_prices = data['Adj Close']
        log_returns = np.log(close_prices / close_prices.shift(1))
        rolling_vol = log_returns.rolling(window=window).std()
        annualized_vol = rolling_vol * np.sqrt(252)
        latest_vol = annualized_vol.dropna().iloc[-1]

        return {
            "ticker": ticker,
            "window": window,
            "historical_volatility": float(latest_vol)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
