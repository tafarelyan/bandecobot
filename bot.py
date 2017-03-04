#!/usr/bin/env python3
import os
from datetime import date

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, RegexHandler, ConversationHandler
from selenium import webdriver

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

MENU = range(1)

reply_keyboard = [['Fisica', 'Quimica'],
                  ['Central', 'Prefeitura'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

driver = webdriver.PhantomJS(executable_path=os.path.abspath('phantomjs'),
                             service_log_path=os.path.devnull)
driver.set_window_size(1120, 550)

u = Updater('YOUR-TOKEN')
dp = u.dispatcher


def get_menu(text, day):
    choices = {
        'Central': '6',
        'Prefeitura': '7',
        'Fisica': '8',
        'Quimica': '9'
    }

    website = 'https://uspdigital.usp.br/rucard/Jsp/cardapioSAS.jsp?codrtn='
    driver.get(website + choices[text])
    cardapio = driver.find_element_by_id('almoco' + day)
    print(cardapio.text)
    return cardapio.text


def start(bot, update):
    update.message.reply_text("Olá, aonde você quer comer hoje?", reply_markup=markup)

    return MENU


def menu(bot, update):
    try:
        weekdays = ['Segunda', 'Terca', 'Quarta', 'Quinta', 'Sexta']

        day = weekdays[date.today().weekday()]
        menu = get_menu(update.message.text, day)
        update.message.reply_text(menu)

        update.message.reply_text("Quer ver o cardápio de outro lugar?", reply_markup=markup)

        return MENU

    except IndexError:
        update.message.reply_text('O bandeco não abre hoje')

        return ConversationHandler.END


def done(bot, update):
    update.message.reply_text("Muito obrigado, até a próxima!")

    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "{}" caused error "{}"'.format(update, error))


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        MENU: [RegexHandler('^(Fisica|Quimica|Central|Prefeitura)$', menu)],
    },

    fallbacks=[RegexHandler('^Done$', done)]
)

dp.add_handler(conv_handler)

dp.add_error_handler(error)

u.start_polling()
u.idle()
