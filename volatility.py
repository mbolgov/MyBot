import requests

import json
import apimoex
import pandas as pd
from math import log

request_url = ('https://iss.moex.com/iss/engines/stock/'
               'markets/shares/boards/TQBR/securities.json')
arguments = {'securities.columns': ('SECID,'
                                    'REGNUMBER,'
                                    'LOTSIZE,'
                                    'SHORTNAME')}

volat = []

with requests.Session() as session:
    iss = apimoex.ISSClient(session, request_url, arguments)
    fact = iss.get()

    tickers = ["SBER", "YNDX", "LKOH", "MTLR", "GAZP", "CHMF", "MGNT", "VTBR", "TRNFP", "ROSN", "NLMK", "SVCB", "BSPB",
               "TCSG", "MAGN", "TATN", "SNGSP", "NVTK", "SNGS", "GMKN", "OZON", "MOEX", "MTSS", "FIVE", "ALRS", "FLOT",
               "SFIN", "MTLRP", "TRMK", "PLZL", "SIBN", "SGZH", "BANEP", "GTRK", "FIXP", "IRKT", "SBERP", "EUTR",
               "SOFL", "RUAL", "NMTP", "FESH", "RASP", "QIWI", "AFLT", "SMLT", "POSI", "GLTR", "TATNP", "AFKS", "KMAZ",
               "ASTR", "BELU", "RNFT", "WUSH", "UNAC", "FEES", "PHOR", "IRAO", "UPRO", "AGRO", "APTK", "POLY", "SVAV",
               "UGLD", "HYDR", "ROLO", "PIKK", "OGKB", "RTKM", "TGKN", "ELFV", "TGKA", "MRKY", "SELG", "LIFE", "MRKS",
               "MVID", "VSMO", "AQUA", "MSNG", "NKHP", "LSRG", "TGKB", "BANE", "ENPG", "ABIO", "KROT", "MGKL", "RTKMP",
               "RENI", "UWGN", "DVEC", "GECO", "MRKV", "HNFG", "BLNG", "AMEZ", "CBOM", "MRKZ", "CIAN", "LSNG", "KLSB",
               "CARM", "VRSB", "MDMG", "MRKP", "MSTT", "KZOSP", "MSRS", "ETLN", "MRKC", "RKKE", "GCHE", "TTLK", "YAKG",
               "CNTL", "LNZLP", "ABRD", "LSNGP", "NSVZ", "MRKU", "LENT", "NKNC", "MGTSP", "LNZL", "PRFN", "CNTLP",
               "KAZT", "AKRN", "KZOS", "NKNCP", "PMSB", "DSKY", "TGKBP", "OKEY", "CHMK", "KRKNP", "KAZTP", "UNKL",
               "PMSBP", "GEMC", "VEON-RX", "VKCO", "DELI", "DIAS"]

    for tick in tickers:
        data = apimoex.get_market_candles(session=session, security=tick, interval=24, start='2022-03-01',
                                          end='2023-10-31',
                                          columns=('begin', 'open', 'close', 'high', 'low', 'volume'))
        data.sort(key=lambda x: x['begin'])

        s = 0
        for i in range(len(data)):
            volat.append([((data[i]['high'] - data[i]['low']) / data[i]['low']) ** 3, tick])
            # s += ((data[i]['high'] - data[i]['low']) / data[i]['low']) ** 3
        # volat.append([s / len(data), tick])
a = [[], [], []]
volat.sort()
for i in range(len(tickers)):
    s, tick = volat[i]
    print(tick, s ** (1 / 3))
    a[i // 49].append(tick)
for el in a:
    print(el)
