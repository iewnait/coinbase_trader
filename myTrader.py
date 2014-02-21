__author__ = "Kevin-Roberts"

from trader import Trader, CoinOrder
import os

def printorder(order):
    print "ORDER DETAILS:"
    print "OrderId: " + str(order.orderid)
    print "OrderType: " + str(order.ordertype)
    print "Qty: " + str(order.qty)
    print "Price: " + str(order.price)
    print "ChangeVal: " + str(order.changeval)
    print "parentorder: " + str(order.parentorder)
    print "Executed: " + str(order.executed)        


def main():
	api_key = os.environ['COINBASE_KEY'] # PLEASE SET THIS UP IN YOUR BASHRC SCRIPT OR SOMETHING export COINBASE_KEY="YOUR KEY"
	OAUTH2_TEMP = None
	# Edit this value with your api_key or oauth2credenial, uncomment the one you choose to use
	# api_key = "longcharacterstring of api_key given by coinbase"
	# OAUTH2_TEMP ='''{"_module": "oauth2client.client", "token_expiry": "2013-03-31T22:48:20Z", "access_token": "c15a9f84e471db9b0b8fb94f3cb83f08867b4e00cb823f49ead771e928af5c79", "token_uri": "https://www.coinbase.com/oauth/token", "invalid": false, "token_response": {"access_token": "c15a9f84e471db9b0b8fb94f3cb83f08867b4e00cb823f49ead771e928af5c79", "token_type": "bearer", "expires_in": 7200, "refresh_token": "90cb2424ddc39f6668da41a7b46dfd5a729ac9030e19e05fd95bb1880ad07e65", "scope": "all"}, "client_id": "2df06cb383f4ffffac20e257244708c78a1150d128f37d420f11fdc069a914fc", "id_token": null, "client_secret": "7caedd79052d7e29aa0f2700980247e499ce85381e70e4a44de0c08f25bded8a", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "90cb2424ddc39f6668da41a7b46dfd5a729ac9030e19e05fd95bb1880ad07e65", "user_agent": null}'''

	orderbook = []
	while True:
		# IF VALID CREDENTIALS THESE TRADES WILL ATTEMPT TO EXECUTE BE CAREFUL!!!
		myTrader = Trader(api_key = api_key, oauth2_credentials = OAUTH2_TEMP)

		for order in orderbook:
			printorder(order)
			if raw_input("Resume? (y/n): ") == 'y':
				myTrader.resumeOrder(order)

		currentprice = myTrader.account.sell_price(qty = 1)
		print "Current Sell Price: " + str(currentprice)
		currentprice = myTrader.account.buy_price(qty = 1)
		print "Current Buy Price: " + str(currentprice)
		print "Current Balance: " + str(myTrader.account.balance)

		print "\n\nSELL LIMIT ORDERS:"
		sell_limit_qty = float(raw_input("Enter Sell Limit qty: "))
		while (sell_limit_qty >=0.000001):
			sell_limit_price = float(raw_input("Enter Sell Limit: "))
			print 'Sell ' + str(sell_limit_qty) + ' btc at no lower than ' + str(sell_limit_price) + ' usd/btc'
			myTrader.setLimitSell(qty= sell_limit_qty, price = sell_limit_price)
			sell_limit_qty = float(raw_input("Enter Sell Limit qty: "))

		print "\n\nBUY LIMIT ORDERS:"
		buy_limit_qty = float(raw_input("Enter Buy Limit qty: "))
		while (buy_limit_qty >=0.000001):
			buy_limit_price = float(raw_input("Enter Buy Limit: "))
			print 'Buy ' + str(buy_limit_qty) + ' btc at no higher than ' + str(buy_limit_price) + ' usd/btc'
			myTrader.setLimitBuy(qty = buy_limit_qty, price = buy_limit_price)
			buy_limit_qty = float(raw_input("Enter Buy Limit qty: "))

		print "\n\nSELL stop loss ORDERS:"
		sell_stoploss_qty = float(raw_input("Enter Sell stop loss qty: "))
		while (sell_stoploss_qty >=0.000001):
			sell_stoploss_price = float(raw_input("Enter Sell stop loss limit: "))
			print 'Sell ' + str(sell_stoploss_qty) +' btc if the price drops below ' + str(sell_stoploss_price) + ' usd/btc'
			myTrader.setStopLoss(qty = sell_stoploss_qty, price = sell_stoploss_price)
			sell_stoploss_qty = float(raw_input("Enter Sell stop loss percent Limit qty: "))

		print "\n\nSELL stop loss trailing value ORDERS:"
		sell_stoploss_qty = float(raw_input("Enter Sell stop loss trailing value qty: "))
		while (sell_stoploss_qty >=0.000001):
			sell_stoploss_value = float(raw_input("Enter Sell stop loss trailing value limit: "))
			print 'Sell ' + str(sell_stoploss_qty) +' btc if the price drops USD$' + str(sell_stoploss_value) + ' from the max value seen by .trade()'
			myTrader.setTrailStopLossValue(qty = sell_stoploss_qty, changeval = sell_stoploss_value)
			sell_stoploss_qty = float(raw_input("Enter Sell stop loss trailing value qty: "))


		print "\n\nSELL stop loss trailing percent ORDERS:"
		sell_stoploss_qty = float(raw_input("Enter Sell stop loss trailing percent qty: "))
		while (sell_stoploss_qty >=0.000001):
			sell_stoploss_percent = float(raw_input("Enter Sell stop loss trailing percent % limit: "))
			print 'Sell ' + str(sell_stoploss_qty) +' btc if the price drops ' + str(sell_stoploss_percent) + '% from the max value seen by .trade()'
			myTrader.setTrailStopLossPercent(qty = sell_stoploss_qty, changeval = sell_stoploss_percent)
			sell_stoploss_qty = float(raw_input("Enter Sell stop loss trailing percent qty: "))
		
		print 'Start attempting to execute the orders with .trade'
		orderbook = myTrader.trade(sleeptime = 60)


if __name__ == "__main__":
	main()
