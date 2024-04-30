import requests

import apimoex
import numpy as np
from joblib import load
from math import log

p_norm = [1.15, 1.15, 1.15, 1.2, 1.2, 1.2, 1.3, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.4]
p_target = 1.3
n = 15
vl = 10
pr = 5


def ExpThScaler(data):
    for i in range(len(data)):
        norm = data[i].pop()
        for j in range(len(data[i])):
            x = (data[i][j] / norm - 1) * 100
            data[i][j] = (p_norm[j] ** x - 1) / (p_norm[j] ** x + 1)


tickers1 = ['PHOR', 'SBER', 'SBERP', 'GAZP', 'GMKN', 'MTSS', 'TATNP', 'ROSN', 'NVTK', 'CBOM', 'LKOH', 'IRAO', 'TATN',
            'RUAL', 'ALRS', 'RTKMP', 'MOEX', 'MAGN', 'CHMF', 'RTKM', 'NLMK', 'MGNT', 'AKRN', 'PLZL', 'SIBN', 'AFKS',
            'AFLT', 'SNGS', 'HYDR', 'BELU', 'POSI', 'SMLT', 'PIKK', 'VTBR', 'TCSG', 'SGZH', 'MVID', 'OGKB', 'ENPG',
            'YNDX', 'OZON', 'LENT', 'TRNFP', 'FEES', 'SNGSP', 'FIVE', 'RASP', 'BANE', 'FIXP']
tickers2 = ['NKNCP', 'VKCO', 'UPRO', 'BANEP', 'LSNGP', 'MTLR', 'GLTR', 'FLOT', 'ETLN', 'CARM', 'AGRO', 'MDMG', 'LSRG',
            'NKNC', 'KMAZ', 'MRKP', 'KRKNP', 'BSPB', 'VSMO', 'MTLRP', 'CIAN', 'WUSH', 'MRKC', 'MSRS', 'MSNG', 'RENI',
            'KZOS', 'AQUA', 'TRMK', 'UGLD', 'HNFG', 'SVCB', 'ABRD', 'SELG', 'RNFT', 'ELFV', 'DSKY', 'ABIO', 'TGKA',
            'OKEY', 'APTK', 'MGTSP', 'LNZLP', 'ASTR', 'YAKG', 'POLY', 'DELI', 'LIFE', 'GCHE']
tickers3 = ['CNTLP', 'FESH', 'KAZT', 'MRKU', 'MGKL', 'KZOSP', 'UNKL', 'MRKV', 'AMEZ', 'KAZTP', 'NMTP', 'VEON-RX',
            'DIAS', 'LNZL', 'MSTT', 'LSNG', 'GEMC', 'SFIN', 'CNTL', 'KROT', 'SOFL', 'BLNG', 'ROLO', 'TTLK', 'MRKZ',
            'PMSBP', 'RKKE', 'PRFN', 'TGKBP', 'GECO', 'MRKY', 'PMSB', 'VRSB', 'UNAC', 'IRKT', 'KLSB', 'SVAV', 'NSVZ',
            'MRKS', 'EUTR', 'TGKN', 'DVEC', 'NKHP', 'TGKB', 'QIWI', 'CHMK', 'UWGN', 'GTRK']

request_url = ('https://iss.moex.com/iss/engines/stock/'
               'markets/shares/boards/TQBR/securities.json')
arguments = {'securities.columns': ('SECID,'
                                    'REGNUMBER,'
                                    'LOTSIZE,'
                                    'SHORTNAME')}

model_up = load('model.joblib')
profit = [0] * pr
vol = 0
res = dict()

with requests.Session() as session:
    iss = apimoex.ISSClient(session, request_url, arguments)

    for tick in tickers2:
        data = apimoex.get_market_candles(session=session, security=tick, interval=24, start='2023-03-10',
                                          end='2023-10-31', columns=('begin', 'open', 'close', 'high', 'low', 'volume'))
        data.sort(key=lambda x: x['begin'])
        data = data[-n:]
        data += apimoex.get_market_candles(session=session, security=tick, interval=24, start='2023-11-01',
                                           columns=('begin', 'open', 'close', 'high', 'low', 'volume'))

        tick_prof = 0
        tick_vol = 0
        res[tick] = [[], [], [], [], []]
        for i in range(n, len(data) - pr + 1):
            price = [[data[j]['close'] for j in range(i - n, i)]]
            ExpThScaler(price)

            volume = [[sum([data[j]['volume'] for j in range(i - vl, i - 1)])]]

            X = np.column_stack([price, volume])
            pred_up = model_up.predict(X)[0]

            pred_up = min(pred_up, 1.0 - (10 ** -16))
            target = (log((1 + pred_up) / (1 - pred_up), p_target)) / 100

            for tmp in range(pr):
                res[tick][tmp].append((target,
                                       (data[i + tmp]['close'] - data[i - 1]['close']) /
                                       data[i - 1]['close'] * 9995 - 10))

            if 0.034 <= target:
                print(tick, (data[i]['close'] - data[i - 1]['close']) / \
                      data[i - 1]['close'] * 9995 - 10)
                for tmp in range(pr):
                    profit[tmp] += (data[i + tmp]['close'] - data[i - 1]['close']) / \
                                   data[i - 1]['close'] * 9995 - 10
                vol += 10000
print()
for tmp in range(pr):
    print("Прибыль при " + str(tmp + 1) + "-дневной торговле: ", profit[tmp], "Profit / Volume =", profit[tmp] / vol)
print("Объём:", vol)
print()

# for tick in tickers1:
#     if len(res[tick][0]) <= 10:
#         continue
#     print(tick)
#     for tmp in range(5):
#         res[tick][tmp].sort()
#         '''
#         l0, r0, prof = 0, 0, 0
#         for l1 in range(len(res[tick][tmp])):
#             s = 0
#             for r1 in range(l1, min(l1 + 9, len(res[tick][tmp]))):
#                 s += res[tick][tmp][r1][1]
#             for r1 in range(l1 + 9, len(res[tick][tmp])):
#                 s += res[tick][tmp][r1][1]
#                 if s / (r1 - l1 + 1) > prof / (r0 - l0 + 1):
#                     prof, l0, r0 = s, l1, r1
#         print("Прибыль при " + str(tmp + 1) + "-дневной торговле: ", prof, "Profit / Volume =",
#               prof / (r0 - l0 + 1) / 10000, "Объём:", (r0 - l0 + 1) * 10000, "Границы:", res[tick][tmp][l0][0], '-',
#               res[tick][tmp][r0][0])
#         '''
#
#         # l0, prof = len(res[tick][tmp]) - 1, res[tick][tmp][-1][1]
#         # s = prof
#         # for l1 in range(len(res[tick][tmp]) - 1, 0, -1):
#         #     s += res[tick][tmp][l1][1]
#         #     if s / (len(res[tick][tmp]) - l1) > prof / (len(res[tick][tmp]) - l0) or s / (
#         #             len(res[tick][tmp]) - l1) > 100:
#         #         prof, l0 = s, l1
#         # print("Прибыль при " + str(tmp + 1) + "-дневной торговле: ", prof, "Profit / Volume =",
#         #       prof / (len(res[tick][tmp]) - l0) / 10000, "Объём:", (len(res[tick][tmp]) - l0) * 10000, "Границы:",
#         #       res[tick][tmp][l0][0], '-', res[tick][tmp][-1][0])
#
#         print("Прибыль при " + str(tmp + 1) + "-дневной торговле на " + tick + ": ", end="")
#         for d in range(1, 11):
#             print(" " * (0 if d == 1 else 40), "Прибыль:", res[tick][tmp][-d][1], "  Profit / Volume =",
#                   res[tick][tmp][-d][1] / 10000, "  Топ:", d, "  Граница:", str(res[tick][tmp][-d][0] * 100)[:6] + "%")
#
#     print()
