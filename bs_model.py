import math
from scipy.stats import norm

def black_scholes_price(spot_price, strike_price, time, rate_of_interest, volatility, option_type):
    d1 = (math.log(spot_price / strike_price) + (rate_of_interest + 0.5 * volatility ** 2) * time) / (volatility * math.sqrt(time))
    d2 = d1 - volatility * math.sqrt(time)

    if option_type == 'call':
        price = spot_price * norm.cdf(d1) - strike_price * math.exp(-rate_of_interest * time) * norm.cdf(d2)
    elif option_type == 'put':
        price = strike_price * math.exp(-rate_of_interest * time) * norm.cdf(-d2) - spot_price * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price

def black_scholes_greeks(spot_price, strike_price, time, rate_of_interest, volatility, option_type):
    d1 = (math.log(spot_price / strike_price) + (rate_of_interest + 0.5 * volatility**2) * time) / (volatility * math.sqrt(time))
    d2 = d1 - volatility * math.sqrt(time)

    pdf_d1 = norm.pdf(d1)
    cdf_d1 = norm.cdf(d1)
    cdf_d2 = norm.cdf(d2)

    gamma = pdf_d1 / (spot_price * volatility * math.sqrt(time))
    vega = spot_price * pdf_d1 * math.sqrt(time)

    if option_type == 'call':
        delta = cdf_d1
        theta = (-spot_price * pdf_d1 * volatility / (2 * math.sqrt(time))
                 - rate_of_interest * strike_price * math.exp(-rate_of_interest * time) * cdf_d2)
        rho = strike_price * time * math.exp(-rate_of_interest * time) * cdf_d2
    elif option_type == 'put':
        delta = cdf_d1 - 1
        theta = (-spot_price * pdf_d1 * volatility / (2 * math.sqrt(time))
                 + rate_of_interest * strike_price * math.exp(-rate_of_interest * time) * norm.cdf(-d2))
        rho = -strike_price * time * math.exp(-rate_of_interest * time) * norm.cdf(-d2)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return {
        'delta': delta,  # Change in option price w.r.t. underlying asset price
        'gamma': gamma,  # Rate of change of delta
        'theta': theta,  # Time decay (usually negative)
        'vega': vega / 100,  # Sensitivity to 1% change in volatility
        'rho': rho / 100     # Sensitivity to 1% change in interest rate
    }


def black_scholes_analysis(spot_price, strike_price, time, rate_of_interest, volatility, option_type):
    # Calculate d1 and d2
    d1 = (math.log(spot_price / strike_price) + (rate_of_interest + 0.5 * volatility ** 2) * time) / (volatility * math.sqrt(time))
    d2 = d1 - volatility * math.sqrt(time)

    # Calculate option price
    if option_type == 'call':
        price = spot_price * norm.cdf(d1) - strike_price * math.exp(-rate_of_interest * time) * norm.cdf(d2)
        prob_ITM = norm.cdf(d2)
        breakeven = strike_price if price == 0 else strike_price + price
        max_profit = 'Unlimited'
    elif option_type == 'put':
        price = strike_price * math.exp(-rate_of_interest * time) * norm.cdf(-d2) - spot_price * norm.cdf(-d1)
        prob_ITM = norm.cdf(-d2)
        breakeven = strike_price - price
        max_profit = f"{strike_price - spot_price:.2f}"
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return {
        'option_price': price,
        'probability_in_the_money': prob_ITM,
        'breakeven_price': breakeven,
        'max_profit': max_profit,
        'max_loss': f"{price:.2f} (premium paid)"
    }
