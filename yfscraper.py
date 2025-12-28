import bs4
import requests
import re


class Ticker():
    def __init__(self,code):
        self.code = re.sub(r"\^",r"%5E",code)
        

        self. session = requests.session()
        self. session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8'
        })

        
    def summary(self):
        url = fr"https://au.finance.yahoo.com/quote/{self.code}/"
        response = self.session.get(url)
        soup = bs4.BeautifulSoup(response.content,"lxml")


        
        stats_list = soup.find_all("span", attrs={"class": "value yf-6myrf1"})
        overview_list = soup.find_all("p", attrs={"class": "yf-z5w6qk"})
        perf_list = soup.find_all("div", attrs={"class": "perf positive yf-1sakh5l"})
        rev_earn_list = soup.find_all("span", attrs={"class": "yf-12ikm9e"})
        analyst_targets_list = soup.find_all("span", attrs={"class": "price yf-1ixzjvx"})
        analyst_ratings_list = soup.find_all("span", attrs={"class": "yf-8gyw8v"})
        val_list = soup.find_all("p", attrs={"class": "value yf-cokr5v"})
        fin_list = soup.find_all("p", attrs={"class": "yf-1anmi6r"})
        time_list = soup.find_all("span", attrs={"class": "yf-ipw1h0 base"})

        data = {
            # Price Data
            "price": float(soup.find("span", attrs={"data-testid": "qsp-price"}).text),
            "price_change": float(soup.find("span", attrs={"data-testid": "qsp-price-change"}).text),
            "price_change_percent": soup.find("span", attrs={"data-testid": "qsp-price-change-percent"}).text,
            "post_price": float(soup.find("span", attrs={"data-testid": "qsp-post-price"}).text),
            "post_price_change": float(soup.find("span", attrs={"data-testid": "qsp-post-price-change"}).text),
            "post_price_change_percent": soup.find("span", attrs={"data-testid": "qsp-post-price-change-percent"}).text,
            "close_time": time_list[2].text,
            "after_hours_time": time_list[4].text,

            # Statistics
            "previous_close": stats_list[0].text,
            "open": stats_list[1].text,
            "bid": stats_list[2].text,
            "ask": stats_list[3].text,
            "days_range": stats_list[4].text,
            "one_year_range": stats_list[5].text,
            "volume": stats_list[6].text,
            "avg_volume": stats_list[7].text,
            "intra_day_market_cap": stats_list[8].text,
            "beta_5y_monthly": stats_list[9].text,
            "pe_ratio_ttm": stats_list[10].text,
            "eps_ttm": stats_list[11].text,
            "earnings_date": stats_list[12].text,
            "forward_dividend_and_yield": stats_list[13].text,
            "ex_dividend_date": stats_list[14].text,
            "year_target_est": stats_list[15].text,

            # Company Overview
            "desc": overview_list[0].text,
            "employees": overview_list[1].text,
            "fiscal_year_ends": overview_list[2].text,
            "sector": overview_list[3].text,
            "industry": overview_list[4].text,

            # Performance Overview
            "ytd_return": perf_list[0].text,
            "one_year_return": perf_list[2].text,
            "three_year_return": perf_list[4].text,
            "five_year_return": perf_list[6].text,

            # Revenue vs Earnings
            "relevant_quarter": rev_earn_list[0].text,
            "relevant_quarter_revenue": rev_earn_list[2].text,
            "relevant_quarter_earnings": rev_earn_list[4].text,

            # Analyst Targets
            "low_price_target": analyst_targets_list[0].text,
            "average_price_target": analyst_targets_list[2].text,
            "high_price_target": analyst_targets_list[3].text,

            # Latest Analyst Ratings
            "latest_analyst_date": analyst_ratings_list[0].text,
            "latest_analyst_name": analyst_ratings_list[1].text,
            "latest_analyst_rating_action": analyst_ratings_list[2].text,
            "latest_analyst_rating": analyst_ratings_list[3].text,
            "latest_analyst_price_action": analyst_ratings_list[4].text,
            "latest_analyst_price_target": analyst_ratings_list[5].text,

            # Valuation Measures
            "valuation_date": soup.find("div", attrs={"class": "asofdate yf-cokr5v"}).text,
            "market_cap": val_list[0].text,
            "enterprise_value": val_list[1].text,
            "trailing_pe": val_list[2].text,
            "forward_pe": val_list[3].text,
            "peg_ratio_fiveyr": val_list[4].text,
            "price_to_sales_ttm": val_list[5].text,
            "price_to_book_mqr": val_list[6].text,
            "enterprise_value_to_revenue": val_list[7].text,
            "enterprise_value_to_EBITDA": val_list[8].text,

            # Financial Highlights
            "profit_margin": fin_list[0].text,
            "roa": fin_list[1].text,
            "roe": fin_list[2].text,
            "revenue": fin_list[3].text,
            "net_income_avi_to_common": fin_list[4].text,
            "diluted_eps": fin_list[5].text,
            "total_cash": fin_list[6].text,
            "debt_to_equity": fin_list[7].text,
            "levered_free_cash_flow": fin_list[8].text
        }

        return data




if __name__=="__main__":
    test = Ticker("NVDA")
