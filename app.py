import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

# Set page title
st.title("Stock Price App")

# Create a sidebar
# ticker = st.sidebar.text_input("Ticker")
ticker = "MSFT"
st.sidebar.write(f"Ticker: {ticker}")
# start_date = st.sidebar.date_input("Start Date")
start_date = "2019-01-01"
# end_date = st.sidebar.date_input("End Date")
end_date = "2023-12-31"

# fetch data
data = yf.download(ticker, start=start_date, end=end_date)
fig = px.line(data, x=data.index, y=data["Adj Close"], title=f"{ticker} Stock Price")
st.plotly_chart(fig)

# Creating tabs
pricing_data, fundamental_data, news = st.tabs(
    ["Pricing Data", "Fundamental Data", "News"]
)

with pricing_data:
    st.header("**Price Movements**")
    data_2 = data
    data_2["pct_change"] = data_2["Adj Close"].pct_change()
    data_2["pct_change"] = data_2["pct_change"].apply(lambda x: f"{x*100:.2f}%")
    data_2.dropna(inplace=True)
    st.write(data_2)
    # Annual Returns
    st.write("**Annual Returns**")
    annual_returns = data["Adj Close"].resample("Y").ffill().pct_change().dropna()
    st.write(annual_returns.apply(lambda x: f"{x*100:.2f}%"))

    # Plotting

    # Candlestick
    candlestick = go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price",
    )

    # volume
    volume = go.Bar(
        x=data.index,
        y=data["Volume"],
        name="Volume",
        yaxis="y2",
        marker=dict(color="rgba(0,0,0,0.3)"),
    )

    # Layout
    layout = go.Layout(
        title="Price Volume Chart",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
    )

    # final figure
    fig = go.Figure(data=[candlestick, volume], layout=layout)
    st.plotly_chart(fig)


with fundamental_data:
    st.write("Fundamental")
    Key = "OWIJ9Z9AIORO0H21"
    fd = FundamentalData(key=Key, output_format="pandas")
    st.subheader("Balance Sheet")
    bs = fd.get_balance_sheet_annual(ticker)[0]
    bs = bs[2:].T

    st.write(bs)
    st.subheader("Income Statement")
    is_ = fd.get_income_statement_annual(ticker)[0]
    is_ = is_[2:].T

    st.write(is_)
    st.subheader("Cash Flow")
    cf = fd.get_cash_flow_annual(ticker)[0]
    cf = cf[2:].T

    st.write(cf)

with news:
    st.header(f"News for {ticker}")
    sn = StockNews(ticker, save_news=False)
    df_news = sn.read_rss()
    for i in range(5):
        st.subheader(f"News {i+1}")
        st.write(df_news["published"][i])
        st.write(df_news["title"][i])
        st.write(df_news["summary"][i])
        title_statement = df_news["sentiment_title"][i]
        st.write(f"Title Sentiment: {title_statement}")
        news_statement = df_news["sentiment_summary"][i]
        st.write(f"News Sentiment: {news_statement}")
