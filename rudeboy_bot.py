import time

import telebot
from telebot import TeleBot

from config import TELEGRAM_TOKEN
from utils import BotUtils

bot = TeleBot(
    token=TELEGRAM_TOKEN,
    skip_pending=True
)

methods = BotUtils()


def is_message_from_admin(message):
    return message.from_user.id in [x.user.id for x in bot.get_chat_administrators(message.chat.id)]


@bot.message_handler(func=lambda m: m.text == 'ping')
def test(message):
    bot.send_message(message.chat.id, 'pong')


@bot.message_handler(func=lambda m: m.chat.type == 'supergroup', commands=['me'])
def me_irc(message):
    if message.chat.id == methods.RUDE_QA_CHAT_ID:
        try:
            query = methods.prepare_query(message)

            if query:
                bot.send_message(message.chat.id, '*{}* _{}_'.format(message.from_user.first_name, query),
                                 parse_mode='Markdown')
                bot.delete_message(message.chat.id, message.message_id)
            else:
                bot.delete_message(message.chat.id, message.message_id)
        except (telebot.apihelper.ApiException, IndexError):
            bot.send_message(
                message.chat.id, 'Братиш, наебнулось. Посмотри логи.')


@bot.message_handler(func=lambda m: m.text.startswith('!ro') and m.chat.type == 'supergroup')
def read_only(message):
    ban_duration = 5  # TODO: Move to configs
    try:
        if message.chat.id == methods.RUDE_QA_CHAT_ID and is_message_from_admin(message):
            user_id = message.reply_to_message.from_user.id
            message_args = message.text.split()
            if len(message_args) > 1:
                if not message_args[1].isdigit():
                    bot.send_message(
                        message.chat.id, '*Неправильный аргумент*', parse_mode='Markdown')
                    return

                ban_duration = int(message_args[1])

                if ban_duration > 1440:
                    bot.send_message(message.chat.id, '*Maксимальное время read-only: 24 часа*', parse_mode='Markdown')
                    return
                elif ban_duration < 1:
                    bot.send_message(message.chat.id, '*Минимальное время read-only: 1 минута*', parse_mode='Markdown')
                    return

            bot.restrict_chat_member(
                message.chat.id, user_id, until_date=int(
                    time.time() + ban_duration * 60),
                can_send_messages=False
            )
            ban_message = f'*{message.reply_to_message.from_user.first_name} ' \
                f'помещен в read-only на {BotUtils.minutes_ending(ban_duration)}*'
            bot.send_message(
                message.chat.id, ban_message, parse_mode='Markdown')
    except AttributeError:
        pass


@bot.message_handler(func=lambda m: m.text == '!rw' and m.chat.type == 'supergroup')
def read_write(message):
    try:
        if message.chat.id == methods.RUDE_QA_CHAT_ID and is_message_from_admin(message):
            user_id = message.reply_to_message.from_user.id
            bot.restrict_chat_member(
                message.chat.id, user_id,
                can_send_messages=True
            )
            ban_message = f'*С {message.reply_to_message.from_user.first_name} снят read-only*'
            bot.send_message(
                message.chat.id, ban_message, parse_mode='Markdown')
    except AttributeError:
        pass


@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    bot.send_message(message.chat.id, 'UI это API?', reply_to_message_id=message.message_id)


if __name__ == '__main__':
    bot.polling()
