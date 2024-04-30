import requests

import json
import apimoex
import pandas as pd
from math import log


def calculate_sma(prices, period):
    sma = sum(prices[-period:]) / period
    return sma


def calculate_ema(prices, period, coef):
    ema = 0
    for price in prices[-period:]:
        ema = ema * (1 - coef) + price * coef
    return ema


request_url = ('https://iss.moex.com/iss/engines/stock/'
               'markets/shares/boards/TQBR/securities.json')
arguments = {'securities.columns': ('SECID,'
                                    'REGNUMBER,'
                                    'LOTSIZE,'
                                    'SHORTNAME')}

price, volume, target_up = [], [], []
price1, volume1, target_up1 = [], [], []
# p_norm = [1.05, 1.05, 1.05, 1.05, 1.07, 1.07, 1.12, 1.16, 1.2, 1.25, 1.4, 1.6]
# p_target = 1.4
# n = 150
# vl = 50

p_norm = [1.15, 1.15, 1.15, 1.2, 1.2, 1.2, 1.3, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.4]
# p_norm = [1.15, 1.15, 1.15, 1.2, 1.2, 1.2, 1.3, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.4]
p_target = 1.3
n = 15
vl = 10
pr = 1

with requests.Session() as session:

    tickers1 = ['PHOR', 'SBER', 'SBERP', 'GAZP', 'GMKN', 'MTSS', 'TATNP', 'ROSN', 'NVTK', 'CBOM', 'LKOH', 'IRAO',
                'TATN', 'RUAL', 'ALRS', 'RTKMP', 'MOEX', 'MAGN', 'CHMF', 'RTKM', 'NLMK', 'MGNT', 'AKRN', 'PLZL', 'SIBN',
                'AFKS', 'AFLT', 'SNGS', 'HYDR', 'BELU', 'POSI', 'SMLT', 'PIKK', 'VTBR', 'TCSG', 'SGZH', 'MVID', 'OGKB',
                'ENPG', 'YNDX', 'OZON', 'LENT', 'TRNFP', 'FEES', 'SNGSP', 'FIVE', 'RASP', 'BANE', 'FIXP']
    tickers2 = ['NKNCP', 'VKCO', 'UPRO', 'BANEP', 'LSNGP', 'MTLR', 'GLTR', 'FLOT', 'ETLN', 'CARM', 'AGRO', 'MDMG',
                'LSRG', 'NKNC', 'KMAZ', 'MRKP', 'KRKNP', 'BSPB', 'VSMO', 'MTLRP', 'CIAN', 'WUSH', 'MRKC', 'MSRS',
                'MSNG', 'RENI', 'KZOS', 'AQUA', 'TRMK', 'UGLD', 'HNFG', 'SVCB', 'ABRD', 'SELG', 'RNFT', 'ELFV', 'DSKY',
                'ABIO', 'TGKA', 'OKEY', 'APTK', 'MGTSP', 'LNZLP', 'ASTR', 'YAKG', 'POLY', 'DELI', 'LIFE', 'GCHE']
    tickers3 = ['CNTLP', 'FESH', 'KAZT', 'MRKU', 'MGKL', 'KZOSP', 'UNKL', 'MRKV', 'AMEZ', 'KAZTP', 'NMTP', 'VEON-RX',
                'DIAS', 'LNZL', 'MSTT', 'LSNG', 'GEMC', 'SFIN', 'CNTL', 'KROT', 'SOFL', 'BLNG', 'ROLO', 'TTLK', 'MRKZ',
                'PMSBP', 'RKKE', 'PRFN', 'TGKBP', 'GECO', 'MRKY', 'PMSB', 'VRSB', 'UNAC', 'IRKT', 'KLSB', 'SVAV',
                'NSVZ', 'MRKS', 'EUTR', 'TGKN', 'DVEC', 'NKHP', 'TGKB', 'QIWI', 'CHMK', 'UWGN', 'GTRK']


    for tick in tickers2:
        print(tick)
        data = apimoex.get_market_candles(session=session, security=tick, interval=24, start='2022-03-01',
                                          end='2023-10-31',
                                          columns=('begin', 'open', 'close', 'high', 'low', 'volume'))

        data.sort(key=lambda x: x['begin'])
        for i in range(n, len(data) - pr + 1):
            price.append([data[j]['close'] for j in range(i - n, i)])
            volume.append([sum([data[j]['volume'] for j in range(i - vl, i - 1)])])

            x = (max([data[i + j]['high'] for j in range(pr)]) / data[i - 1]['close'] - 1) * 100
            target_up.append((p_target ** x - 1) / (p_target ** x + 1))

        data = data[-n:]
        data += apimoex.get_market_candles(session=session, security=tick, interval=24, start='2023-11-01',
                                           columns=('begin', 'open', 'close', 'high', 'low', 'volume'))
        data.sort(key=lambda x: x['begin'])
        for i in range(n, len(data) - pr + 1):
            price1.append([data[j]['close'] for j in range(i - n, i)])
            volume1.append([sum([data[j]['volume'] for j in range(i - vl, i - 1)])])

            x = (max([data[i + j]['high'] for j in range(pr)]) / data[i - 1]['close'] - 1) * 100
            target_up1.append((p_target ** x - 1) / (p_target ** x + 1))

print(len(target_up))
with open('price.json', 'w') as json_file:
    json.dump(price, json_file)

with open('volume.json', 'w') as json_file:
    json.dump(volume, json_file)

with open('target_up.json', 'w') as json_file:
    json.dump(target_up, json_file)

print(len(target_up1))
with open('price_test.json', 'w') as json_file:
    json.dump(price1, json_file)

with open('volume_test.json', 'w') as json_file:
    json.dump(volume1, json_file)

with open('target_up_test.json', 'w') as json_file:
    json.dump(target_up1, json_file)
