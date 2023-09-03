import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib import style

from orderbook import Orderbook

DEFAULT_SYMBOL = "btcusdt"

#Check if symbol was provided as argument, default to DEFAULT_SYMBOL otherwise
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--symbol", help="Ticker symbol")
args = parser.parse_args()

symbol = args.symbol
if not symbol:
    symbol = DEFAULT_SYMBOL

orderbook = Orderbook(symbol)
orderbook.connect()

style.use('dark_background')

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

bid_x = []
bid_z = []
ask_x = []
ask_z = []
y = [[0] * 100]

def set_depth(i):
    bid_data = orderbook.get_bids()
    bid_prices = sorted(bid_data.keys())[-100:]
    bid_quantities = [bid_data[price] for price in bid_prices]
    bid_depth = []
    cumulative_volume = 0
    for qty in bid_quantities[::-1]:
        cumulative_volume += qty
        bid_depth.append(cumulative_volume)

    bid_depth = bid_depth[::-1]

    ask_data = orderbook.get_asks()
    ask_prices = sorted(ask_data.keys())[:100]
    ask_quantities = [ask_data[price] for price in ask_prices]
    ask_depth = []
    cumulative_volume = 0
    for qty in ask_quantities:
        cumulative_volume += qty
        ask_depth.append(cumulative_volume)

    bid_x.append(bid_prices)
    bid_z.append(bid_depth)
    ask_x.append(ask_prices)
    ask_z.append(ask_depth)

    ax.clear()
    ax.set_ylim(y[-1][0], y[0][0])
    ax.set_xlabel("Price")
    ax.set_ylabel("Time (ms)")
    ax.set_zlabel("Depth")
    ax.plot_wireframe(np.array(bid_x), np.array(y), np.array(bid_z), color="green")
    ax.plot_wireframe(np.array(ask_x), np.array(y), np.array(ask_z), color="red")

    y.append([y[-1][0] + 100] * 100)

    if len(y) > 10:
        del bid_x[0]
        del bid_z[0]
        del ask_x[0]
        del ask_z[0]
        del y[0]

ani = animation.FuncAnimation(fig, set_depth, interval=100)
plt.show()