import datetime
import numpy as np
import pandas as pd
import pandas_datareader.data as web

def optimize(symbols):

    start = datetime.datetime.now() - datetime.timedelta(days=5*365)
    end = datetime.datetime.now()

    portfolio_data = web.get_data_yahoo(symbols, start, end)['Adj Close']

    portfolio_ret = portfolio_data.pct_change()

    portfolio_cov_mat = portfolio_ret.cov() * 252

    # Simulate portfolios
    num_port = 5000

    # Empty arrays for weights, returns, risk and sharpe ratio
    all_wts = np.zeros((num_port, len(portfolio_data.columns)))
    port_returns = np.zeros((num_port))
    port_risk = np.zeros((num_port))
    sharpe_ratio = np.zeros((num_port))

    # The loop
    for i in range(num_port):
        wts = np.random.uniform(size = len(portfolio_data.columns))
        wts = wts/np.sum(wts)

        all_wts[i,:] = wts

        port_ret = np.sum(portfolio_ret.mean() * wts)
        port_ret = (port_ret + 1) ** 252 - 1

        port_returns[i] = port_ret

        port_sd = np.sqrt(np.dot(wts.T, np.dot(portfolio_cov_mat, wts)))

        port_risk[i] = port_sd

        sr = (port_ret) / port_sd
        sharpe_ratio[i] = sr


    names = portfolio_data.columns
    max_sr = all_wts[sharpe_ratio.argmax()]

    return {key: round(value * 100, 2) for key, value in list(zip(names, max_sr))}
