from custom_exception import *
import os
import telebot
import re
import requests
import tldextract
from bs4 import BeautifulSoup


with open('credentils.txt') as f:
    API_KEY = f.readlines()[0].split("=")[1]
dictionary = {"objectives": [], "course_content": [], "modules": []}
bot = telebot.TeleBot(API_KEY)


def find_url(text):
    """extract the target url from text.

    Parameters
    ----------

    text : str
        String from which url to be extracted.

    Returns
    -------
    Optional[str]
        Return url if present in the given string.
    """

    return re.findall(
        '(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', str(text))


def crawl_url(url):
    """crawl the given url.

    Parameters
    ----------
    url : str
        The url to be crawled.

    Returns
    -------
    return a Beautifulsoup object

    """

    try:
        res = requests.get(url)

        if tldextract.extract(res.url).domain != "udemy":
            raise InvalidUdemyUrl(f"'{url}' invalid udemy url!")
    except Exception as e:
        raise InvalidUrlError(f"{url} not a valid url")

    return BeautifulSoup(res.text, 'html.parser')


@bot.message_handler(commands=["title"])
def title_response(message):
    """get user information about course.

    Parameters
    ----------
    url : str
        message object from telegram.

    Returns
    -------
    reply object from telegram.

    """
    try:
        bot.send_chat_action(message.chat.id, "typing")

        soup = crawl_url(dictionary["url"])
        title = soup.find_all("h1", "udlite-heading-xl")[0].string
        objectives = soup.find_all(
            "span", "what-you-will-learn--objective-item--ECarc")

        for objective in objectives:
            dictionary["objectives"].append(objective.string)

        course_content = soup.find(
            "span", "curriculum--content-length--1XzLS").get_text().split("•")

        for i in range(len(course_content)):
            course_content[i-1].replace(u'\xa0', u' ')
            dictionary["course_content"].append(course_content[i])

        modules = soup.find_all(
            "span", "section--section-title--8blTh")

        for module in modules:
            dictionary["modules"].append(module.string)

        description = soup.find(
            attrs={"data-purpose": "safely-set-inner-html:description:description"}).get_text()

        dictionary["description"] = description

        # sentiment analysis of reviews

        bot.reply_to(message, title)
    except Exception as e:
        raise InvalidUdemyUrl("some sort of probleme")


@bot.message_handler(commands=["begin"])
def welcome_message(message):
    """reply to the user.

    """
    bot.send_chat_action(message.chat.id, "typing")
    bot.reply_to(
        message, "Hi There, \nWelcome to udemy bot, \nWhat can i do for you today?")


@bot.message_handler(commands=["objectives"])
def objectives_response(message):
    try:
        if len(dictionary["objectives"]) >= 2:
            list_of_messages = dictionary["objectives"]
            msg = '.\n\n•'.join(list_of_messages)
            bot.reply_to(
                message, msg)
        else:
            text = "Hi, The list of objectives is not too long, Just don't invest in this course"
            bot.send_message(message.chat.id, text)
    except Exception as e:
        InvalidUrlError("some sort of error related to the url")


@bot.message_handler(commands=["help", "start"])
def send_instructions(message):
    bot.send_chat_action(message.chat.id, "typing")
    msg = f"Hi {message.from_user.first_name}, \n below are the instruction in order to use this bot. \n\n /begin: to start the conversation with the bot. \n /title: give you the title of the course. \n /objectives: give you the materials that you gonna learn from the provided course."
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["content"])
def course_content(message):
    bot.send_chat_action(message.chat.id, "typing")
    list_of_content = dictionary["course_content"]
    msg = '.\n\n•'.join(list_of_content)
    bot.reply_to(
        message, msg)


@bot.message_handler(commands=["modules"])
def course_modules_snapshot(message):
    bot.send_chat_action(message.chat.id, "typing")
    list_of_content = dictionary["modules"]
    msg = '.\n\n•'.join(list_of_content)
    bot.reply_to(
        message, msg)


@bot.message_handler(commands=["description"])
def course_description(message):
    bot.send_chat_action(message.chat.id, "typing")
    description = dictionary["description"]
    msg = description
    bot.reply_to(
        message, msg)


@bot.message_handler(func=lambda m: True)
def second_response(message):
    url = find_url(str(message))[0]
    dictionary["url"] = url
    bot.reply_to(
        message, "okey i see what can i do, \nwhat exaclty you wanna know")


bot.polling()
