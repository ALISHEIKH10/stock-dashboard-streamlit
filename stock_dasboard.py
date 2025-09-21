import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("Stock Dashboard")

# Sidebar inputs
ticker_input = st.sidebar.text_input("Enter Stock Ticker Symbol (e.g. AAPL):", value="AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))


class StockDashboard:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.ticker_obj = None
        self.data = None

    def fetch_data(self):
        try:
            self.ticker_obj = yf.Ticker(self.ticker)
            self.data = yf.download(self.ticker, start=self.start_date, end=self.end_date)

            # Flats MultiInde
            if isinstance(self.data.columns, pd.MultiIndex):
                self.data.columns = self.data.columns.get_level_values(0)

        except Exception as e:
            st.error(f"Error fetching data: {e}")
            self.data = pd.DataFrame()

    def plot_charts(self):
        if self.data is None or self.data.empty:
            st.warning("No data found for the selected period.")
            return

        st.subheader(f"Stock Data for {self.ticker.upper()}")
        st.dataframe(self.data)

        y_col = "Adj Close" if "Adj Close" in self.data.columns else "Close"

        # Line chart
        fig = px.line(
            self.data,
            x=self.data.index,
            y=y_col,
            title=f"{self.ticker.upper()} {y_col} Price"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Volume chart
        fig_vol = px.bar(
            self.data,
            x=self.data.index,
            y="Volume",
            title=f"{self.ticker.upper()} Trading Volume"
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    def show_company_info(self):
        if not self.ticker_obj:
            return

        with st.expander("Company Info"):
            try:
                info = self.ticker_obj.info

                company_info = {
                    "Company Name": info.get("longName"),
                    "Sector": info.get("sector"),
                    "Industry": info.get("industry"),
                    "Market Cap": info.get("marketCap"),
                    "PE Ratio": info.get("trailingPE"),
                    "Previous Close": info.get("previousClose"),
                    "52 Week High": info.get("fiftyTwoWeekHigh"),
                    "52 Week Low": info.get("fiftyTwoWeekLow"),
                }

                st.write(company_info)

            except Exception as e:
                st.write("Error fetching company info.")

    def show_financials(self):
        if not self.ticker_obj:
            return

        with st.expander("Balance Sheet"):
            try:
                balance_sheet = self.ticker_obj.balance_sheet
                if not balance_sheet.empty:
                    st.dataframe(balance_sheet)
                else:
                    st.write("No balance sheet data available.")
            except Exception as e:
                st.write("Error fetching balance sheet.")

        with st.expander("Income Statement"):
            try:
                income_statement = self.ticker_obj.financials
                if not income_statement.empty:
                    st.dataframe(income_statement)
                else:
                    st.write("No income statement data available.")
            except Exception as e:
                st.write("Error fetching income statement.")

        with st.expander("Cash Flow Statement"):
            try:
                cashflow = self.ticker_obj.cashflow
                if not cashflow.empty:
                    st.dataframe(cashflow)
                else:
                    st.write("No cash flow data available.")
            except Exception as e:
                st.write("Error fetching cash flow statement.")

    def show_annual_returns(self):
        if not self.ticker_obj:
            return

        with st.expander("Annual Returns"):
            try:
                hist = self.ticker_obj.history(period="5y")
                if not hist.empty:
                    hist["Year"] = hist.index.year
                    annual = hist.groupby("Year")["Close"].agg(["first", "last"])
                    annual["Return %"] = ((annual["last"] - annual["first"]) / annual["first"]) * 100
                    st.dataframe(annual)
                else:
                    st.write("No historical data to calculate annual returns.")
            except Exception as e:
                st.write("Error fetching annual returns.")

    def run(self):
        self.fetch_data()
        self.plot_charts()
        self.show_company_info()
        self.show_financials()
        self.show_annual_returns()


# Run dashboard if user clicks button
if st.sidebar.button("Fetch Data"):
    dashboard = StockDashboard(ticker_input, start_date, end_date)
    dashboard.run()
else:
    st.info("Enter ticker and click Fetch Data to display results.")


st.header("Summary")
file = st.file_uploader("Upload your csv file", type = ["csv"])

if file:
    df = pd.read_csv(file)
    st.subheader("DataPreview")
    st.dataframe(df)

if file:
    st.subheader("Summary stats")
    st.write(df.describe())