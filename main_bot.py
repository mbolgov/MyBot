import telebot
from telebot import types
import requests

import apimoex
import numpy as np
from joblib import load
from math import log
from datetime import datetime

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


TOKEN = '7038523131:AAFVrNZFigYvU3jCXiADAOmNV9oHXiCdhKY'
bot = telebot.TeleBot(TOKEN)
users = {851859274: '3000-01-01', 1383515457: '3000-01-01', 5885081488: '3000-01-01', 418916363: '3000-01-01',
         562257536: '2024-06-01'}

request_url = ('https://iss.moex.com/iss/engines/stock/'
               'markets/shares/boards/TQBR/securities.json')
arguments = {'securities.columns': ('SECID,'
                                    'REGNUMBER,'
                                    'LOTSIZE,'
                                    'SHORTNAME')}

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

not_iir = 'Не является индивидуальной инвестиционной рекомендацией.'

main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_markup.add(types.KeyboardButton('Получить прогноз по отдельной акции'))
main_markup.add(types.KeyboardButton('Получить прогноз на день вперёд'))
main_markup.add(types.KeyboardButton('Получить прогноз по неделю вперёд'))
main_markup.add(types.KeyboardButton('Информация о моделях'))


# Функция для получения прогноза на завтра
def predict(type: str, tickers: list):
    model = load('model' + type + '.joblib')
    ans = ''

    predict = []
    with requests.Session() as session:
        for tick in tickers:
            data = apimoex.get_market_candles(session=session, security=tick, interval=24, start='2023-05-10',
                                              columns=('begin', 'open', 'close', 'high', 'low', 'volume'))

            data.sort(key=lambda x: x['begin'])
            data = data[-n:]

            if len(data) != n:
                continue
            price = [[data[j]['close'] for j in range(n)]]
            ExpThScaler(price)

            volume = [[sum([data[j]['volume'] for j in range(n - vl, n - 1)])]]

            X = np.column_stack([price, volume])
            pred_up = model.predict(X)[0]

            pred_up = min(pred_up, 1.0 - (10 ** -16))
            target = (log((1 + pred_up) / (1 - pred_up), p_target)) / 100
            predict.append([target, data[-1]['close'], tick])

    predict.sort(reverse=True)
    for target, p, tick in predict[:10]:
        ans += 'Цель по ' + tick + ': ' + str(p * (1 + target))[:7] + ' рублей, +' + str(
            target * 100)[:4] + '%\n'
    ans += '\n'
    return ans


# Обработчик команды '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Получить прогноз!'))
    markup.add(types.KeyboardButton('Информация о моделях'))
    bot.send_message(message.chat.id, "Привет! Я бот-трейдер, можете получить прогноз на цены акций на завтра или на неделю вперёд.",
                     reply_markup=markup)


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    now = datetime.now().strftime('%Y-%m-%d')
    id = message.from_user.id
    if id not in users or users[id] < now:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Получить прогноз!'))
        markup.add(types.KeyboardButton('Информация о моделях'))
        if message.text == 'Информация о моделях':
            bot.reply_to(message,
                         "Модели обучались на данных с 01.03.2022 по 31.10.2023 и тестировались на данных с 01.11.2023 по 25.04.2024.\n"
                         "Тестирование моделей проходило по следующей стратегии: если в конце торговой сессии прогноз по акции больше x%, "
                         "то совершается покупка этой акции; продажа акции совершается в конце торговой сессии в день окончания прогноза "
                         "(через день или через неделю после покупки).\nОцениваемым параметром является число y% – средняя доходность за "
                         "сделку с учётом комиссии брокера 0,05%. Также подтверждением стабильной работы модели является параметр n – "
                         "число совершённых сделок (от 50).", reply_markup=markup)
            with open('res.jpg', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.reply_to(message,
                         "Ваша подписка недействительна. Для получения доступа к функционалу бота напишите @MikhailTheBest", reply_markup=markup)
        return

    if message.text == "Получить прогноз!":
        bot.reply_to(message, "Выберите одну из опций", reply_markup=main_markup)
        return

    if message.text == 'Информация о моделях':
        bot.reply_to(message,
                     "Модели обучались на данных с 01.03.2022 по 31.10.2023 и тестировались на данных с 01.11.2023 по 25.04.2024.\n"
                     "Тестирование моделей проходило по следующей стратегии: если в конце торговой сессии прогноз по акции больше x%, "
                     "то совершается покупка этой акции; продажа акции совершается в конце торговой сессии в день окончания прогноза "
                     "(через день или через неделю после покупки).\nОцениваемым параметром является число y% – средняя доходность за "
                     "сделку с учётом комиссии брокера 0,05%. Также подтверждением стабильной работы модели является параметр n – "
                     "число совершённых сделок (от 50).", reply_markup=main_markup)
        with open('res.jpg', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    elif message.text == 'Получить прогноз по отдельной акции':
        bot.reply_to(message, "Пожалуйста, введите тикер ценной бумаги заглавными буквами, например: SBER, OZON")
        bot.register_next_step_handler(message, get_current_stock_predict)
    else:
        days = 0
        if message.text == 'Получить прогноз на день вперёд':
            days = 1
        if message.text == 'Получить прогноз по неделю вперёд':
            days = 7
        if days == 0:
            bot.reply_to(message, "Я вас не разобрал. При проблемах в работе с ботом напишите @MikhailTheBest",
                         reply_markup=main_markup)
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Получить прогноз по акциям низкой волатильности'))
        markup.add(types.KeyboardButton('Получить прогноз по акциям средней волатильности'))
        markup.add(types.KeyboardButton('Получить прогноз по акциям высокой волатильности'))
        bot.reply_to(message, "Выберите волатильность акции", reply_markup=markup)
        bot.register_next_step_handler(message, get_best_predicts, days=days)


def get_current_stock_predict(message):
    tick = message.text
    id, tickers = 0, []
    if tick in tickers1:
        id, tickers = 1, [tick]
    if tick in tickers2:
        id, tickers = 2, [tick]
    if tick in tickers3:
        id, tickers = 3, [tick]
    if id == 0:
        bot.reply_to(message,
                     "В наших списках не найден указанный тикер. Возможно, Вы ошиблись в написании или написали строчными буквами.\n"
                     "При проблемах в работе с ботом напишите @MikhailTheBest", reply_markup=main_markup)
    else:
        bot.reply_to(message, "Занимаемся расчётом для акции " + tick + ". Это займёт около минуты.")
        ans = 'По нашему мнению, ' + tick + ' - акция ' + (
            'низкой' if id == 1 else ('средней' if id == 2 else 'высокой')) + ' волатильности\n\n'
        ans += 'Прогноз на день вперёд:\n' + predict(str(id) + "-1", tickers)
        ans += 'Прогноз на неделю вперёд:\n' + predict(str(id) + "-7", tickers)
        ans += not_iir
        bot.reply_to(message, ans, reply_markup=main_markup)


def get_best_predicts(message, days):
    if message.text == 'Получить прогноз по акциям низкой волатильности':
        bot.reply_to(message, "Занимаемся расчётом. Это займёт около минуты.")
        ans = 'Прогноз по акциям низкой волатильности на ' + ('день' if days == 1 else 'неделю') + ' вперёд:\n'
        ans += predict("1-" + str(days), tickers1) + not_iir
        bot.reply_to(message, ans, reply_markup=main_markup)
    elif message.text == 'Получить прогноз по акциям средней волатильности':
        bot.reply_to(message, "Занимаемся расчётом. Это займёт около минуты.")
        ans = 'Прогноз по акциям средней волатильности на ' + ('день' if days == 1 else 'неделю') + ' вперёд:\n'
        ans += predict("2-" + str(days), tickers2) + not_iir
        bot.reply_to(message, ans, reply_markup=main_markup)
    elif message.text == 'Получить прогноз по акциям высокой волатильности':
        bot.reply_to(message, "Занимаемся расчётом. Это займёт около минуты.")
        ans = 'Прогноз по акциям высокой волатильности на ' + ('день' if days == 1 else 'неделю') + ' вперёд:\n'
        ans += predict("3-" + str(days), tickers3) + not_iir
        bot.reply_to(message, ans, reply_markup=main_markup)
    else:
        bot.reply_to(message, "Я вас не разобрал. При проблемах в работе с ботом напишите @MikhailTheBest",
                     reply_markup=main_markup)


bot.polling(none_stop=True)
