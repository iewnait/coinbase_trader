"""
Coinbase Python Client Library

AUTHOR

Kevin Roberts
Github:  Kevin-Roberts
Started on: 12-11-2013

LICENSE (The MIT License)

Copyright (c) 2013 Kevin Roberts "kr0b1486@hotmail.com"

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

__author__ = 'Kevin-Roberts'




import sys
from coinbase import CoinbaseAccount
from coinbase.models import CoinbaseTransfer, CoinbaseError
import oauth2client         # Maybe someone can test if I need this or not
from datetime import datetime

import time
import os

MARKET_BUY = "MarketBuy"
MARKET_SELL = "MarketSell"
LIMIT_BUY = "LimitBuy"
LIMIT_SELL = "LimitSell"
STOP_LOSS = "StopLoss"
TRAIL_STOP_VALUE = "ValueTrailingStopLoss"
TRAIL_STOP_PERCENT = "PercentageTrailingStopLoss"

ORDER_ID = 0

class CoinOrder(object):
    """
    Represents DIfferent Types of Orders. Used in the order list. 
    """
    def __init__(self, ordertype, qty, price = 0, changeval = 0, parentorder = None):
        global ORDER_ID
        self.orderid = ORDER_ID
        ORDER_ID+=1 
        self.ordertype = ordertype
        self.qty = qty
        self.price = price
        self.changeval = changeval
        self.parentorder = parentorder
        self.executed = False



class Trader(object):

    def __init__(self,api_key = None, oauth2_credentials = None, orderbook = None, logname = "traderlog.txt"):
        if (api_key is None) and (oauth2_credentials is None):
            raise ValueError("api_key and oauth2_credentials cannot be None")
        if (api_key is not None) and (oauth2_credentials is not None):
            raise ValueError("User Provided both api_key and oauth2_credentials, select one")        # I might want to instead just use one or the other 

        
        self.orderbook = [] if orderbook is None else orderbook

        f = open(logname, 'w')
        f.close()
        self.logname = logname
        self.logwrite(str(datetime.now()) + '\n')

        self.account = CoinbaseAccount(oauth2_credentials,api_key)


    def logwrite(self, message):
        """
        Writes to the logfile with appended newline. 
        """
        with open(self.logname, 'a') as log:
            log.write(message + '\n')

    def logexecution(self, order, result):
        """
        Write the result and order to the log file
        """
        self.logorder(order)
        logstr = "Order Type: " + str(result.type) + " Code: " + str(result.code) + " Executed at: " + str(result.created_at) 
        logstr = logstr + "\nBTC Amount: " + str(result.btc_amount) + " Total Price: " + str(result.total_amount) + " Fees: " + str(result.fees_bank+result.fees_coinbase) 
        self.logwrite(logstr)     

    def logorder(self, order, header = None):
        """
        Writes the order the log file
        """
        logstr = header + '\n' if isinstance(header,str) else ''
        logstr = "OrderID: %s OrderType: %s Quantity: %s Price: %s" % (order.orderid, order.ordertype, order.qty, order.price)
        logstr = logstr + " Change Value: " + str(order.changeval)
        logstr = logstr + " Executed: " + str(order.executed) + '\n'
        if order.parentorder is not None:
            self.logorder(order.parentorder, "Parent Order:")
        self.logwrite(logstr)

    def ExecuteOrder(self, order):
        """
        Executes an order based on its order.ordertype
        Returns None if the trade is valid is not yet active(i.e limit not met)
        Returns a CoinbaseError or CoinbaseTransfer object if order attempted to execute
        Returns False if the order should be Deleted or removed from the orderbook. 
        """
        traderesult = None
        currentprice = -1

        if order.ordertype in [MARKET_BUY, LIMIT_BUY]:
            currentprice = self.account.buy_price(qty = order.qty)
            print "Current Buy Price: " + str(currentprice/order.qty) 
        elif order.ordertype in [MARKET_SELL, LIMIT_SELL, STOP_LOSS, TRAIL_STOP_VALUE, TRAIL_STOP_PERCENT]: 
            currentprice = self.account.sell_price(qty = order.qty)
            print "Current Sell Price: " + str(currentprice/order.qty)

        if order.ordertype == MARKET_BUY:
            traderesult = self.account.buy_btc(qty = order.qty)
        elif order.ordertype == MARKET_SELL:
            traderesult = self.account.sell_btc(qty = order.qty)
        elif order.ordertype == LIMIT_BUY:
            if currentprice <= order.price:
                traderesult = self.account.buy_btc(qty = order.qty)
            else:
                print "Did not met LIMIT_BUY price at: " + str(order.price / order.qty) + ' for ' + str(order.qty) + ' BTC'
        elif order.ordertype == LIMIT_SELL:
            if currentprice >= order.price:
                print currentprice, order.price
                traderesult = self.account.sell_btc(qty = order.qty)
            else:
                print "Did not met LIMIT_SELL price at: " + str(order.price / order.qty) + ' for ' + str(order.qty) + ' BTC'
        elif order.ordertype == STOP_LOSS:
            if currentprice <= order.price:
                traderesult = CoinOrder(ordertype = MARKET_SELL, qty = order.qty, parentorder = order)
            else:
                print "Did not met STOP_LOSS price at: " + str(order.price / order.qty) + ' for ' + str(order.qty) + ' BTC'
        elif order.ordertype == TRAIL_STOP_VALUE:
            if currentprice > order.price:
                order.price = currentprice
                print "Setting new TRAIL_STOP_VALUE max price seen: " + str(order.price / order.qty)
            elif currentprice <= (order.price - order.changeval):
                traderesult = CoinOrder(ordertype = MARKET_SELL, qty = order.qty, parentorder = order)
            else:
                print "Did not meet TRAIL_STOP_VALUE price at: " + str((order.price - order.changeval) / order.qty) + ' for ' + str(order.qty) + ' BTC'
        elif order.ordertype == TRAIL_STOP_PERCENT:
            if currentprice > order.price:
                order.price = currentprice
                print "Setting new TRAIL_STOP_PERCENT max price seen: " + str(order.price / order.qty)
            elif currentprice <= (order.price * (1.0 - order.changeval) ):
                traderesult = CoinOrder(ordertype = MARKET_SELL, qty = order.qty, parentorder = order)
            else:
                print "Did not meet TRAIL_STOP_PERCENT price at: " + str((order.price * (1.0 - order.changeval) ) / order.qty) + ' for ' + str(order.qty) + ' BTC'
        else:
            print order.ordertype          # Could throw an error on CoinOrder initialize 
            sys.exit(1)

        return traderesult


    def trade(self, runtime = None, sleeptime = 60):
        """ 
        Returns a table of transaction results when time runs out or runs continously. Writes a log file.

        :param runtime: Number of seconds to trade should execute, infinity (None) is the default.
        :param sleeptime: Interval of time between checking orders (coinbase updates their prices once per 60 seconds)
        """
        initialBtcBal = self.account.balance
        initialUsdVal = self.account.sell_price(initialBtcBal)
        initialSellRate = initialUsdVal/initialBtcBal if initialBtcBal != 0 else 0
        self.logwrite("Initial BTC Balance: " + str(initialBtcBal) + " Initial USD Value: " + str(initialUsdVal) + " Price Per Coin: " + str(initialSellRate)) 
        while ( (runtime is None) or (runtime>0) ) and (len(self.orderbook) > 0):
            try:
                temporderbook = []
                sleep = True

                os.system('clear')
                print "Current Balance: " + str(self.account.balance)
                order_counter = 0
                for order in self.orderbook:
                    order_counter = order_counter + 1
                    print str(order_counter) + ": ",
                    result = self.ExecuteOrder(order)
                    if result is False:
                        # Invalid Order ID
                        pass
                    elif isinstance(result, CoinbaseError):
                        # THere is an error, check if its due to improper supply.
                        print result.error
                        self.logorder(order, result.error[0])
                        if result.error[0] == "You must acknowledge that the price can vary by checking the box below.":
                            temporderbook.append(order)     # Means the order failed due to low supply and not agreeing to the price varying.
                        elif len(self.orderbook) == 1:
                            sleep = False       # This is done to exit quickly if the only trade errors
                    elif isinstance(result, CoinOrder):
                        order.executed = True
                        temporderbook.append(result)
                        sleep = False           # If a coinorder is returned it should be executed asap. 
                    elif isinstance(result, CoinbaseTransfer):
                        # Trade executed
                        order.executed = True
                        self.logexecution(order, result)
                    elif result is None:
                        temporderbook.append(order)

                self.orderbook = temporderbook
                if sleep is True:
                    if runtime is not None:
                        runtime = runtime - sleeptime
                    if runtime is None or runtime > 0:
                        time.sleep(sleeptime)
            except KeyboardInterrupt:
                print "Modifying orders"
                return self.orderbook
            except :
                print "Exception in orders, skipping.."

    def _addOrder(self, ordertype, qty, price = 0, changeval = None):
        """
        Generic Order Adding Function. price is in price per share. User shouldn't call.
        """
        price = price * qty
        order = CoinOrder(ordertype = ordertype, qty = qty, price = price, changeval = changeval)

        self.orderbook.append(order)
        self.logorder(order, "Added Order:")
        return order

    def resumeOrder(self, order):
        return self._addOrder(order.ordertype, order.qty, order.price, order.changeval)

    def setMarketBuy(self, qty):
        """
        Buy qty bitcoins as soon as possible
        """
        return self._addOrder(ordertype = MARKET_BUY, qty = qty)


    def setMarketSell(self, qty):
        """
        Sell qty bitcoins as soon as possible
        """
        return self._addOrder(ordertype = MARKET_SELL, qty = qty)


    def setLimitBuy(self, qty, price):
        """
        Helps buy low, Buy at specified price or lower. Input price per share
        """
        return self._addOrder(ordertype = LIMIT_BUY,qty = qty, price = price)


    def setLimitSell(self, qty, price):
        """
        Helps sell high, Sell at specified price or higher. Input execution price per share
        """
        return self._addOrder(ordertype = LIMIT_SELL, qty = qty, price = price ) 

    def setStopLoss(self, qty, price):
        """
        If the price goes below a specified price, sell it all ASAP via market sell order. Input execution price per share
        """
        return self._addOrder(ordertype = STOP_LOSS, qty = qty, price = price)


    def setTrailStopLossValue(self, qty, changeval):
        """
        Sell qty bitcoins when they drop "value" below their maximum per share value since purchase. Basically a Moving Limit sell at: maxPriceSeen - value
        """
        return self._addOrder(ordertype = TRAIL_STOP_VALUE, qty = qty, price = 0, changeval = changeval*qty)

    def setTrailStopLossPercent(self, qty, changeval, maxprice = 0):
        """
        Sell qty bitcoins when they have a changepercent drop below their maximum value since purchase. Basically a Moving Limit sell at: maxPriceSeen * (1 - (changepercent/100) ) 
        """
        return self._addOrder(ordertype = TRAIL_STOP_PERCENT, qty = qty, price = maxprice, changeval = changeval/100.0)



    def RemoveOrder(self, orderid):
        """
        Accepts either the orderid (starts at 0 and increments to the number of total orders)
        Or the CoinOrder object returned when the order was created.
        """
        startlen = len(self.orderbook)
        # Remove the items if the order id matches
        removedOrder = None
        if isinstance(orderid, int):
            temp = []
            for order in self.orderbook:
                if order.orderid != orderid:
                    temp.append(order)
                else:
                    removedOrder = order
            self.orderbook = temp
        if isinstance(orderid, CoinOrder):
            try:
                self.orderbook.remove(order)
                removedOrder = order         
            except:
                pass
        return removedOrder