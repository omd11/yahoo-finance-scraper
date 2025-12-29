import bs4
import requests
import re
import datetime
import io
import pandas as pd
from typing import Literal

class Ticker():
    def __init__(self,code)->None:
        self.code = re.sub(r"\^",r"%5E",code)
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8'
        })

    def summary(self) -> dict:
        url = fr"https://au.finance.yahoo.com/quote/{self.code}/"
        response = self.session.get(url)
        soup = bs4.BeautifulSoup(response.content,"lxml")
        
        def get_text_safe(element_list, index, default="N/A"):
            try:
                return element_list[index].get_text(strip=True)
            except (IndexError, AttributeError):
                return default

        def get_find_safe(element, default="N/A"):
            try:
                return element.get_text(strip=True)
            except AttributeError:
                return default

        stats_list = soup.find_all("span", attrs={"class": "value yf-6myrf1"})
        overview_list = soup.find_all("p", attrs={"class": "yf-z5w6qk"})
        perf_list = soup.find_all("div", attrs={"class": "perf positive yf-1sakh5l"})
        rev_earn_list = soup.find_all("span", attrs={"class": "yf-12ikm9e"})
        targets_list = soup.find_all("span", attrs={"class": "price yf-1ixzjvx"})
        ratings_list = soup.find_all("span", attrs={"class": "yf-8gyw8v"})
        valuation_list = soup.find_all("p", attrs={"class": "value yf-cokr5v"})
        financials_list = soup.find_all("p", attrs={"class": "yf-1anmi6r"})
        time_list = soup.find_all("span", attrs={"class": "yf-ipw1h0 base"})

        data = {

            "price": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-price"})),
            "price_change": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-price-change"})),
            "price_change_percent": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-price-change-percent"})),
            "post_price": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-post-price"})),
            "post_price_change": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-post-price-change"})),
            "post_price_change_percent": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-post-price-change-percent"})),
            "overnight_price": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-overnight-price"})),
            "overnight_price_change": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-overnight-price-change"})),
            "overnight_price_change_percent": get_find_safe(soup.find("span", attrs={"data-testid": "qsp-overnight-price-change-percent"})),
            "close_time": get_text_safe(time_list, 2),
            "after_hours_time": get_text_safe(time_list, 4),

            # --- Statistics ---
            "previous_close": get_text_safe(stats_list, 0),
            "open": get_text_safe(stats_list, 1),
            "bid": get_text_safe(stats_list, 2),
            "ask": get_text_safe(stats_list, 3),
            "days_range": get_text_safe(stats_list, 4),
            "one_year_range": get_text_safe(stats_list, 5),
            "volume": get_text_safe(stats_list, 6),
            "avg_volume": get_text_safe(stats_list, 7),
            "intra_day_market_cap": get_text_safe(stats_list, 8),
            "beta_5y_monthly": get_text_safe(stats_list, 9),
            "pe_ratio_ttm": get_text_safe(stats_list, 10),
            "eps_ttm": get_text_safe(stats_list, 11),
            "earnings_date": get_text_safe(stats_list, 12),
            "forward_dividend_and_yield": get_text_safe(stats_list, 13),
            "ex_dividend_date": get_text_safe(stats_list, 14),
            "year_target_est": get_text_safe(stats_list, 15),

            # --- Company Overview ---
            "desc": get_text_safe(overview_list, 0),
            "employees": get_text_safe(overview_list, 1),
            "fiscal_year_ends": get_text_safe(overview_list, 2),
            "sector": get_text_safe(overview_list, 3),
            "industry": get_text_safe(overview_list, 4),

            # --- Performance Overview ---
            "ytd_return": get_text_safe(perf_list, 0),
            "one_year_return": get_text_safe(perf_list, 2),
            "three_year_return": get_text_safe(perf_list, 4),
            "five_year_return": get_text_safe(perf_list, 6),

            # --- Revenue vs Earnings ---
            "relevant_quarter": get_text_safe(rev_earn_list, 0),
            "relevant_quarter_revenue": get_text_safe(rev_earn_list, 2),
            "relevant_quarter_earnings": get_text_safe(rev_earn_list, 4),

            # --- Analyst Targets ---
            "low_price_target": get_text_safe(targets_list, 0),
            "average_price_target": get_text_safe(targets_list, 2),
            "high_price_target": get_text_safe(targets_list, 3),

            # --- Latest Analyst Ratings ---
            "latest_analyst_date": get_text_safe(ratings_list, 0),
            "latest_analyst_name": get_text_safe(ratings_list, 1),
            "latest_analyst_rating_action": get_text_safe(ratings_list, 2),
            "latest_analyst_rating": get_text_safe(ratings_list, 3),
            "latest_analyst_price_action": get_text_safe(ratings_list, 4),
            "latest_analyst_price_target": get_text_safe(ratings_list, 5),

            # --- Valuation Measures ---
            "valuation_date": get_find_safe(soup.find("div", attrs={"class": "asofdate yf-cokr5v"})),
            "market_cap": get_text_safe(valuation_list, 0),
            "enterprise_value": get_text_safe(valuation_list, 1),
            "trailing_pe": get_text_safe(valuation_list, 2),
            "forward_pe": get_text_safe(valuation_list, 3),
            "peg_ratio_fiveyr": get_text_safe(valuation_list, 4),
            "price_to_sales_ttm": get_text_safe(valuation_list, 5),
            "price_to_book_mqr": get_text_safe(valuation_list, 6),
            "enterprise_value_to_revenue": get_text_safe(valuation_list, 7),
            "enterprise_value_to_EBITDA": get_text_safe(valuation_list, 8),

            # --- Financial Highlights ---
            "profit_margin": get_text_safe(financials_list, 0),
            "roa": get_text_safe(financials_list, 1),
            "roe": get_text_safe(financials_list, 2),
            "revenue": get_text_safe(financials_list, 3),
            "net_income_avi_to_common": get_text_safe(financials_list, 4),
            "diluted_eps": get_text_safe(financials_list, 5),
            "total_cash": get_text_safe(financials_list, 6),
            "debt_to_equity": get_text_safe(financials_list, 7),
            "levered_free_cash_flow": get_text_safe(financials_list, 8),
        }
        return data

    def get_historical_data(self, start:datetime.datetime, end:datetime.datetime, interval: Literal["1d","1wk","1mo"]) -> tuple[pd.DataFrame, pd.DataFrame]:
        start = start.timestamp()
        end = end.timestamp()

        url = fr"https://au.finance.yahoo.com/quote/{self.code}/history/?frequency={interval}&period1={start}&period2={end}"
        response = self.session.get(url)
        soup = bs4.BeautifulSoup(response.content,"lxml")
        table = io.StringIO(str(soup.find("table")))

        prices = pd.read_html(table)[0]

        # Seperating dividends from historic prices
        try:
            dividends = prices[prices.Open.str.contains("Dividend")]
            dividends = dividends[["Date","Open"]].copy()
            dividends.rename(inplace=True, columns={"Open":"Dividend"})
            dividends['Dividend'] = dividends['Dividend'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
            prices=prices.drop(prices[prices["Open"].str.contains("Dividend")].index)
        except:
            dividends = None

        prices.Date = pd.to_datetime(prices.Date,format="mixed")
        prices.rename(inplace=True,columns={"Close Closing price adjusted for splits.":"Close","Adj Close Adjusted closing price adjusted for splits and dividend and/or capital gain distributions.":"Adj Close"})

        return prices,dividends

    def get_key_stats(self)->tuple[pd.DataFrame,dict,dict]:
        """To improve robustness, this function uses dictionaries to ensure that output keys are always fixed regardless of Yahoo Finance
        """

        url = fr"https://au.finance.yahoo.com/quote/{self.code}/key-statistics/"
        response = self.session.get(url)
        soup = bs4.BeautifulSoup(response.content,"lxml")
    
    # Find the specific table containing "Market Cap"
    # We look for a table where the first row contains "Market Cap"
        tables = soup.find_all("table")
        valuation_table = None
        
        for table in tables:
            if "Market cap" in table.get_text():
                valuation_table = table
                break
                
        if valuation_table:
            # Use pandas to read the HTML table directly
            # read_html returns a list of dataframes, we take the first one
            df_list = pd.read_html(io.StringIO(str(valuation_table)))
            if df_list:
                df_val = df_list[0]
                
                # Clean up the column names
                # usually the first column is the measure name (e.g., "Market Cap")
                # and subsequent columns are dates (e.g., "Current", "9/30/2024")
                df_val.columns = [c if isinstance(c, str) else str(c) for c in df_val.columns]
                
                # Rename the first column to 'Measure' for clarity
                df_val = df_val.rename(columns={df_val.columns[0]: "Measure"})
                
                # Clean up the 'Measure' column (remove footnotes like [1])
                # We do this via regex or string manipulation
                df_val['Measure'] = df_val['Measure'].str.replace(r'\[\d+\]', '', regex=True).str.strip()
                
                valuation_data = df_val

        
        def get_clean_value(label_text, raw_stats_dict):
            # Helper to find a value by its approximate label in the raw dict
            return raw_stats_dict.get(label_text, "N/A")

        # Parse all rows into a raw lookup dictionary first
        raw_stats = {}
        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                # Clean Label
                label_cell = cols[0]
                for sup in label_cell.find_all("sup"): 
                    sup.decompose()
                label = label_cell.get_text(strip=True)
                
                # Clean Value
                val_cell = cols[1]
                value = val_cell.get_text(strip=True)
                
                pattern = r"^(.*?)\s*\(\s*(.*?)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4}|[A-Za-z]{3}\s+\d{1,2},?\s+\d{4})\)$"
                match = re.search(pattern, label)
                if match:
                    clean_label = match.group(1).strip()
                    inner_prefix = match.group(2).strip()
                    date_extracted = match.group(3).strip()

                    if inner_prefix:
                        raw_stats[clean_label+ " " + inner_prefix] = value
                        raw_stats[clean_label + " " + inner_prefix + " date"] = date_extracted

                    else:
                        raw_stats[clean_label] = value
                        raw_stats[clean_label + " date"] = date_extracted
                else:
                    raw_stats[label] = value
                
                
                

        financial_highlights = {
            # Profitability
            "profit_margin": get_clean_value("Profit margin", raw_stats),
            "operating_margin": get_clean_value("Operating margin  (ttm)", raw_stats),
            
            # Management Effectiveness
            "return_on_assets": get_clean_value("Return on assets  (ttm)", raw_stats),
            "return_on_equity": get_clean_value("Return on equity  (ttm)", raw_stats),
            
            # Income Statement
            "revenue": get_clean_value("Revenue  (ttm)", raw_stats),
            "revenue_per_share": get_clean_value("Revenue per share  (ttm)", raw_stats),
            "quarterly_revenue_growth": get_clean_value("Quarterly revenue growth  (yoy)", raw_stats),
            "gross_profit": get_clean_value("Gross profit  (ttm)", raw_stats),
            "ebitda": get_clean_value("EBITDA", raw_stats),
            "net_income_avi": get_clean_value("Net income avi to common  (ttm)", raw_stats),
            "diluted_eps": get_clean_value("Diluted EPS  (ttm)", raw_stats),
            "quarterly_earnings_growth": get_clean_value("Quarterly earnings growth  (yoy)", raw_stats),
            
            # Balance Sheet
            "total_cash": get_clean_value("Total cash  (mrq)", raw_stats),
            "total_cash_per_share": get_clean_value("Total cash per share  (mrq)", raw_stats),
            "total_debt": get_clean_value("Total debt  (mrq)", raw_stats),
            "total_debt_equity": get_clean_value("Total debt/equity  (mrq)", raw_stats),
            "current_ratio": get_clean_value("Current ratio  (mrq)", raw_stats),
            "book_value_per_share": get_clean_value("Book value per share  (mrq)", raw_stats),
            
            # Cash Flow Statement
            "operating_cash_flow": get_clean_value("Operating cash flow  (ttm)", raw_stats),
            "levered_free_cash_flow": get_clean_value("Levered free cash flow  (ttm)", raw_stats),
        }

        trading_information = {
            # Stock Price History
            "beta_5y": get_clean_value("Beta (5Y monthly)", raw_stats),
            "52_week_change": get_clean_value("52-week change", raw_stats),
            "sp500_52_week_change": get_clean_value("S&P 500 52-week change", raw_stats),
            "52_week_high": get_clean_value("52-week high", raw_stats),
            "52_week_low": get_clean_value("52-week low", raw_stats),
            "50_day_avg": get_clean_value("50-day moving average", raw_stats),
            "200_day_avg": get_clean_value("200-day moving average", raw_stats),
            
            # Share Statistics
            "avg_vol_3_month": get_clean_value("Avg vol (3-month)", raw_stats),
            "avg_vol_10_day": get_clean_value("Avg vol (10-day)", raw_stats),
            "shares_outstanding": get_clean_value("Shares outstanding", raw_stats),
            "implied_shares_outstanding": get_clean_value("Implied shares outstanding", raw_stats),
            "float": get_clean_value("Float", raw_stats),
            "held_by_insiders": get_clean_value("% held by insiders", raw_stats),
            "held_by_institutions": get_clean_value("% held by institutions", raw_stats),
            "shares_short": get_clean_value("Shares short", raw_stats),
            "shares_short_date": get_clean_value("Shares short date", raw_stats),
            "short_ratio": get_clean_value("Short ratio", raw_stats),
            "short_ratio_date": get_clean_value("Short ratio date", raw_stats),
            "short_percent_of_float": get_clean_value("Short % of float", raw_stats),
            "short_percent_of_float_date": get_clean_value("Short % of float date", raw_stats),
            "short_percent_of_shares_outstanding": get_clean_value("Short % of shares outstanding", raw_stats),
            "short_percent_of_shares_outstanding_date": get_clean_value("Short % of shares outstanding date", raw_stats),
            "shares_short_prior_month": get_clean_value("Shares short prior month", raw_stats),
            "shares_short_prior_month_date": get_clean_value("Shares short prior month date", raw_stats),
            
            # Dividends & Splits
            "forward_annual_dividend_rate": get_clean_value("Forward annual dividend rate", raw_stats),
            "forward_annual_dividend_yield": get_clean_value("Forward annual dividend yield", raw_stats),
            "trailing_annual_dividend_rate": get_clean_value("Trailing annual dividend rate", raw_stats),
            "trailing_annual_dividend_yield": get_clean_value("Trailing annual dividend yield", raw_stats),
            "5_year_avg_dividend_yield": get_clean_value("5-year average dividend yield", raw_stats),
            "payout_ratio": get_clean_value("Payout ratio", raw_stats),
            "dividend_date": get_clean_value("Dividend date", raw_stats),
            "ex_dividend_date": get_clean_value("Ex-dividend date", raw_stats),
            "last_split_factor": get_clean_value("Last split factor", raw_stats),
            "last_split_date": get_clean_value("Last split date", raw_stats),
        }
    
        return {
        "valuation_measures": valuation_data, 
        "financial_highlights": financial_highlights, 
        "trading_information": trading_information
    }

    def get_annual_income_statement(self)->pd.DataFrame:
        response = self.session.get(f"https://au.finance.yahoo.com/quote/{self.code}/financials/")
        soup = bs4.BeautifulSoup(response.content,"lxml")


        header_row = soup.find('div', class_='row yf-1yyu1pc')
        
        columns = []

        if header_row:
            # Loop through the column divs in the header
            # The first column is usually 'Breakdown' or blank, subsequent are dates
            for cell in header_row.find_all('div', class_='column'):
                text = cell.get_text(strip=True)
                columns.append(text if text else "Breakdown")
        else:
            # Fallback if specific header class isn't found exactly
            columns = ["Breakdown", "TTM", "Date 1", "Date 2", "Date 3", "Date 4"]

        # 2. Extract Data Rows
        # We use the specific class provided by the user for the data rows
        data_rows_html = soup.find_all('div', class_='row lv-0 yf-t22klz')
        
        extracted_data = []

        for row in data_rows_html:
            # Find all individual column cells within the row
            cells = row.find_all('div', class_='column')
            
            # Extract text from each cell
            row_values = [cell.get_text(strip=True) for cell in cells]
            
            # Ensure the row has data before adding
            if row_values:
                extracted_data.append(row_values)

        # 3. Create Pandas DataFrame
        # Ensure columns match data length (handle potential mismatches)
        if extracted_data:
            num_cols = len(extracted_data[0])
            # Truncate or pad headers to match data columns if necessary
            if len(columns) > num_cols:
                columns = columns[:num_cols]
            elif len(columns) < num_cols:
                columns += [f"Col_{i}" for i in range(len(columns), num_cols)]
                
            df = pd.DataFrame(extracted_data, columns=columns)
            
            # Optional: Set the Breakdown column as the index
            if "Breakdown" in df.columns:
                df.set_index("Breakdown", inplace=True)
            return df
        else:
            return None

    def get_analysis(self)->tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame,pd.DataFrame,pd.DataFrame,pd.DataFrame,pd.DataFrame]:
        response = self.session.get(f"https://au.finance.yahoo.com/quote/{self.code}/analysis/")
        soup = bs4.BeautifulSoup(response.content,"lxml")

        def extract_table_by_header(header_text):
        # Find the specific section header (e.g., "Earnings Estimate")
        # Yahoo often uses <h3> or specific classes for section headers.
        # We search for the text directly in the soup to locate the nearest table.
            header = soup.find(string=lambda t: t and header_text in t)
            
            if header:
                # Navigate up to find the container, then find the table within it
                # or find the 'next' table tag after this header.
                parent = header.find_parent('section') # Analysis tables are often in <section> tags
                if not parent:
                    # Fallback: Find the nearest table following this header
                    table = header.find_next('table')
                else:
                    table = parent.find('table')
                
                if table:
                    try:
                        df_list = pd.read_html(io.StringIO(str(table)))
                        if df_list:
                            df = df_list[0]
                            # Set the first column as index (usually the metric label)
                            if not df.empty:
                                df.set_index(df.columns[0], inplace=True)
                            return df
                    except ValueError:
                        pass
            
            return pd.DataFrame() # Return empty if not found

    # Extract each specific table
        df_earnings_est = extract_table_by_header("Earnings estimate")
        df_revenue_est = extract_table_by_header("Revenue estimate")
        df_earnings_hist = extract_table_by_header("Earnings history")
        df_eps_trend = extract_table_by_header("EPS trend")
        df_eps_revisions = extract_table_by_header("EPS revisions")
        df_growth_est = extract_table_by_header("Growth estimates")


        return (
            df_earnings_est, 
            df_revenue_est, 
            df_earnings_hist, 
            df_eps_trend, 
            df_eps_revisions, 
            df_growth_est
        )

    def get_holders(self)->tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
        response = self.session.get(f"https://au.finance.yahoo.com/quote/{self.code}/holders/")
        soup = bs4.BeautifulSoup(response.content,"lxml")

        tables = soup.find_all("table")

        breakdown = pd.read_html(io.StringIO(str(tables[0])))[0]
        top_institutional_holders = pd.read_html(io.StringIO(str(tables[1])))[0]
        top_mutual_fund_holders = pd.read_html(io.StringIO(str(tables[2])))[0]

        return breakdown,top_institutional_holders,top_mutual_fund_holders

    def get_options(self,date)->tuple[pd.DataFrame,pd.DataFrame]:
        if date % 604800 !=86400 or date < datetime.datetime.now().timestamp():
            print("invalid time given, defaulting to closest expiration date")
            response = self.session.get(f"https://au.finance.yahoo.com/quote/{self.code}/options/")
        else:
            response = self.session.get(f"https://au.finance.yahoo.com/quote/{self.code}/options/?date={date}/")

        soup = bs4.BeautifulSoup(response.content,"lxml")

        tables = soup.find_all("table")

        with open("options2.html","w", encoding="utf-8") as file:
            file.write(str(tables))

        calls = pd.read_html(io.StringIO(str(tables[0])))[0]
        puts = pd.read_html(io.StringIO(str(tables[1])))[0]

        return calls,puts

if __name__=="__main__":
    test = Ticker("NVDA")
    data = test.summary()
    print(data)





    