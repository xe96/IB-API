from ib_insync import *
import logging
import time
from datetime import datetime
from ib_insync import Stock, Option, MarketOrder
class IBTradingSystem:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='trading_log.txt'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize IB connection
        self.ib = IB()
        self.connected = False

    def connect(self):
        """Establish connection to IB Gateway"""
        try:
            self.ib.connect('127.0.0.1', 4002, clientId=1)  # 4002 for paper trading
            self.connected = True
            self.logger.info("Successfully connected to IB Gateway")
            return self.ib
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            raise

    def get_market_data(self, symbol, sec_type='STK', exchange='SMART', currency='USD'):
        """Get real-time market data for a security"""
        try:
            contract = Stock(symbol, exchange, currency) if sec_type == 'STK' else \
                      Option(symbol, exchange=exchange, currency=currency)
            
            ticker = self.ib.reqMktData(contract)
            self.ib.sleep(2)  # Wait for data to arrive
            
            return {
                'bid': ticker.bid,
                'ask': ticker.ask,
                'last': ticker.last,
                'volume': ticker.volume
            }
        except Exception as e:
            self.logger.error(f"Error getting market data: {str(e)}")
            return None

    def get_historical_data(self, contract, duration='5 D', bar_size='5 mins', what_to_show='TRADES'):
        """Get historical market data"""
        try:
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=True
            )
            return bars
        except Exception as e:
            self.logger.error(f"Error getting historical data: {str(e)}")
            return None

    def create_stock_contract(self, symbol):
        """Create a stock contract"""
        return Stock(symbol, 'SMART', 'USD')

    def create_option_contract(self, symbol, expiry, strike, right):
        """Create an option contract"""
        return Option(
            symbol=symbol,
            lastTradeDateOrContractMonth=expiry,
            strike=strike,
            right=right,
            exchange='SMART'
        )

    def place_order(self, symbol, action, quantity, order_type='MKT'):
        """Place a trade order"""
        try:
            contract = self.create_stock_contract(symbol)
            
            if order_type == 'MKT':
                order = MarketOrder(action, quantity)
            else:
                raise ValueError("Currently only market orders are supported")

            trade = self.ib.placeOrder(contract, order)
            
            # Wait for order to fill
            while not trade.isDone():
                self.ib.sleep(1)
                self.logger.info(f"Order status: {trade.orderStatus.status}")
            
            return trade
        except Exception as e:
            self.logger.error(f"Error placing order: {str(e)}")
            return None

    def disconnect(self):
        """Safely disconnect from IB"""
        if self.connected:
            self.ib.disconnect()
            self.logger.info("Disconnected from IB Gateway")

# Utility functions
def format_option_expiry(date_str):
    """Convert date string to YYYYMMDD format"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y%m%d')
    except ValueError as e:
        logging.error(f"Date format error: {str(e)}")
        return None 