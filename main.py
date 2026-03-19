import yfinance as yf

# Prompt user for ticker symbol.
# We normalize user input by stripping whitespace + converting to uppercase. 
# Now, if user types " mu", it becomes "MU", ticker symbol for Micron Technology.

print("Pick a stock to analyze!")
security = input("Enter the ticker symbol:").strip().upper()

# User might enter an invalid ticker symbol. We validate it here.

def valid_ticker(security):
    t = yf.Ticker(security)
    info = t.info
    return bool(info and info.get("regularMarketPrice") != None)

# We use a while loop here to prompt user until they enter a valid ticker symbol.

while not valid_ticker(security):
    print(f"'{security}' is not a valid ticker symbol. Please enter another.")
    security = input("Enter the ticker symbol:").strip().upper()

# We need to fetch fixed data for the company selected by user.
ticker = yf.Ticker(security)
info = ticker.info

# Collecting all fixed data points.
company_name = info.get("longName", "N/A")
industry = info.get("industry", "N/A")




