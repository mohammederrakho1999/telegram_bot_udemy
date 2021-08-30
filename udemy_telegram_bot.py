import os
import telebot
import re


with open('credentils.txt') as f:
    API_KEY = f.readlines()[0].split("=")[1]

bot = telebot.TeleBot(API_KEY)


def find_url(text):
    """
    find all the urls format present in a string.

    parameters:
         text: string from where the urls should be extracted.

    output:
         list of urls.


    """
    return re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', text)


def crawl_url(urls):
    """
    crawl the given url
    """
    pass


@bot.message_handler(func=lambda m: True)
def great(message):
    urls = find_url(str(message))
    bot.reply_to(message, urls)


bot.polling()
