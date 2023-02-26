import time
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import streamlit as st
import streamlit.components.v1 as stc
st.set_page_config(layout="wide")

#================================ Parameters ================================# 
fetch_period = '2y'


def Bullish_Cross_200EMA(data):
	if data['Close'][-1] > data['EMA200'][-1] and data['Close'][-2] < data['EMA200'][-2]:
		return True
	else:
		return False

#================================ TradingView Plot ================================# 
header = '''
<div class="tradingview-widget-container">
<div id="tradingview_widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">

var studies = 
[
	{id: "MAExp@tv-basicstudies", inputs: {length: 200}},
	{id: "RSI@tv-basicstudies", inputs: {length: 52}}
];
'''

footer = '''
"studies_overrides": {
      "moving average.ma.color": "red",
      "moving average.ma.linewidth": 2,

      "relative strength index.rsi.color": "green",
      "relative strength index.upper band.color": "#2100f5",
      "relative strength index.lower band.color": "#2100f5",

      "relative strength index.upper band.value": 60,
      "relative strength index.lower band.value": 40,
    },

    "container_id": "tradingview_widget"
  });
  </script>
</div>
'''

# ======================================================================================= # 
# List of Stokes from the Exchange
nasdaq = pd.read_csv("nasdaq_stock_list.csv")
nasdaq=nasdaq.sort_values(by=['Market Cap'], ascending=False)

nifty = pd.read_excel("nifty1000.xlsx")

st.title("Stocks That Just Crossed the 200 EMA in Daily TimeFrame")
st.write("Enter the your ticker symbols separated by commas.")
st.write("(Note: If you want to enter custom NSE stocks then add .NS after the ticker)")
custom_tickers = st.text_input("**:blue[Tickers of Your Choice:]**", "AAPL,MSFT,GOOG")

# ======================================================================================= # 
# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_state.horizontal = False

col1, col2, col3 = st.columns(3)

with col1:
    custom_scan = st.checkbox("Scan my custom stokes list only", key="disabled")
    US_scan = st.checkbox("Scan through NASDAQ ticker  list", key="US")
    IND_scan = st.checkbox("Scan through NSE ticker list", key="IND")

with col2:
	selected_scan_number = st.radio(
		"Comprehensive Scan (By Market Cap) 👇",
		["Top 100", "Top 500", "Top 1000", "Custom Range"],
		key="Scan_Number",
		label_visibility=st.session_state.visibility,
		horizontal=st.session_state.horizontal,
	)

with col3:
	if selected_scan_number== "Custom Range":
		with st.form(key="custom_scan_range_form"):
			scan_start, scan_end = st.slider("Custom Scan Range", 0, 7000, (0, 7000), 1)
			submit_button = st.form_submit_button(label="Submit")

# ======================================================================================= # 
if US_scan:
	st.markdown("<span style='color:red'>Great! You have selected the option to scan the US stocks.</span>",unsafe_allow_html=True)
	Ticker_List = nasdaq['Symbol'].tolist()
elif IND_scan:
	st.markdown("<span style='color:red'>Great! You have selected the option to scan the NSE stocks.</span>",unsafe_allow_html=True)
	Ticker_List = nifty['Symbol'].tolist()
else:
    st.markdown("<span style='color:red'>Great! You have selected your preferred stocks.</span>",unsafe_allow_html=True)
     # Split the ticker symbols and check each one
    Ticker_List = [custom_tickers.strip().upper() for custom_tickers in custom_tickers.split(",")]

		
if custom_scan:
	scan_start = 0
	scan_number = len(Ticker_List)
elif selected_scan_number:
	if (selected_scan_number == 'Top 100'):
		scan_start = 0
		scan_number = 100
	elif (selected_scan_number == 'Top 500'):
		scan_start = 0
		scan_number = 500
	elif (selected_scan_number == 'Top 1000'):
		scan_start = 0
		scan_number = 1000
	else:
		scan_start = scan_start
		scan_number = scan_end
else:
	scan_start = scan_start
	scan_number = scan_end

# ======================================================================================= # 
if US_scan:
	if (fetch_period == '2y'):
		df_desired_length = 504 
	elif (fetch_period == '1y'):
		df_desired_length = 251
	else:
		df_desired_length = 'none'
elif IND_scan:
	if (fetch_period == '2y'):
		df_desired_length = 498 
	elif (fetch_period == '1y'):
		df_desired_length = 251
	else:
		df_desired_length = 'none'
else:
	if (fetch_period == '2y'):
		df_desired_length = 504 
	elif (fetch_period == '1y'):
		df_desired_length = 251
	else:
		df_desired_length = 'none'

print ("[Scan_Start: Scan_End]", scan_start, scan_number)


# ======================================================================================= # 
if st.button('Start the scan now!'):
	st.write(f'We have started the EMA scan ranging [{scan_start} - {scan_number}]')

	#st.write("Count", "\t|Ticker", "\t|Close", "\t|EMA200", "\t|Close-EMA200", "\t|%difference")

	with st.empty():
		bullish_tickers = []
		count = 0
		for tick in range(scan_start, scan_number):
			ticker = Ticker_List[tick]
			#ticker = 'SQ'
			print ("Now Accessing the Symbol:", tick, ticker)
			st.write("Now Accessing the Symbol:", tick, ticker)

			if IND_scan:
				ticker = ticker+".NS"
			
			time.sleep(0.3) # Sleep for 0.3 seconds
			df = yf.download(ticker, period=fetch_period)
			print ("Length of the dataframe:", len(df))

			if (len(df) == df_desired_length):
				df['VWAP'] = (df['Volume']*(df['High']+df['Low']+df['Close'])/3).cumsum() / df['Volume'].cumsum()
				#df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
				df["EMA200"] = ta.ema(df["Close"], length=200) # Take long time series for accurate result

				last_close = round(df['Close'][-1],2)
				last_ema= round(df['EMA200'][-1],2)

				diff_ema = round(last_close-last_ema,2)

				perctd = round(100.0*diff_ema/last_ema, 2)

				print (tick, ticker, last_close, last_ema, diff_ema, perctd)
				if Bullish_Cross_200EMA(df):
					st.write(str(count) + "- " + ticker)
					bullish_tickers.append(ticker)
					#st.write(tick, "\t|", ticker," \t|", last_close, "\t|", last_ema, "\t|", diff_ema, "\t|", perctd, "%")
				
				count = count + 1

		print ("Tickers found:", bullish_tickers)

	# Display the results
	if bullish_tickers:
		st.markdown(f"<span style='color:blue'>{len(bullish_tickers)} stocks just crossed the 200 EMA:</span>", unsafe_allow_html=True)
		for ticker in bullish_tickers:
			st.write("- " + ticker)
			if US_scan or custom_scan:
				stc.html(
					header + f"""
						new TradingView.widget(
						{{
						"width": 1400,
						"height": 500,
						"symbol": "{ticker}",
						"interval": "D",
						"timezone": "Etc/UTC",
						"theme": "light",
						"style": "2",
						"locale": "en",
						"toolbar_bg": "#f1f3f6",
						"enable_publishing": false,
						"allow_symbol_change": true,
						"enabled_features": ["move_logo_to_main_pane"],
						
						"studies": studies,

					""" + footer,
					height=500,
					width=1400,
				)
	else:
		st.write("<span style='color:blue'>No stocks crossed the 200 EMA.</span>", unsafe_allow_html=True)


