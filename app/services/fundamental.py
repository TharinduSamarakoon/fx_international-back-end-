import datetime
import json

import pandas as pd
import nltk

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from collections import defaultdict

pages = 3
news_list = []
target_url = 'https://www.investing.com/news/forex-news/'

eng_stopwords = stopwords.words('english')

with open('app/resources/fx-bear-terms.csv', 'r') as bears:
    bear_words = bears.read()

with open('app/resources/fx-bull-terms.csv', 'r') as bulls:
    bull_words = bulls.read()

with open('app/resources/5min.csv', 'r') as fivemin:
    fivemin_words = fivemin.read()

with open('app/resources/1hr.csv', 'r') as onehr:
    onehr_words = onehr.read()

with open('app/resources/1day.csv', 'r') as oneday:
    oneday_words = oneday.read()

pair_list = pd.read_csv('app/resources/fx-pairs-collection.csv', header=0, )

pair_vocabulary = pd.read_csv('app/resources/fx-pairs-slang.csv', header=0, parse_dates=[2])


def pair_to_dictionary(pair_vocabulary):
    pair_vocab_dic = defaultdict(dict)
    for i in pair_vocabulary.columns:
        pair_vocab_dic[i] = pair_vocabulary[i].to_list()

    return pair_vocab_dic


def pairs_lematizer(pair_vocabulary):
    for x in pair_vocabulary.keys():

        for word in pair_vocabulary[x]:
            word = lem.lemmatize(word, 'n')

    return pair_vocabulary


def pairs_tokenize(pair_vocabulary):
    for x in pair_vocabulary.keys():
        for word in pair_vocabulary[x]:
            word = word_tokenize(word)

    return pair_vocabulary


pair_vocabulary = pair_to_dictionary(pair_vocabulary)
lem = WordNetLemmatizer()
stem = PorterStemmer()

bear_words = lem.lemmatize(bear_words, 'v')
bull_words = lem.lemmatize(bull_words, 'v')
fivemin_words = lem.lemmatize(fivemin_words, 'v')
onehr_words = lem.lemmatize(onehr_words, 'v')
oneday_words = lem.lemmatize(oneday_words, 'v')

pair_vocabulary = pairs_lematizer(pair_vocabulary)

bear_words = word_tokenize(bear_words)
bull_words = word_tokenize(bull_words)
fivemin_words = word_tokenize(fivemin_words)
onehr_words = word_tokenize(onehr_words)
oneday_words = word_tokenize(oneday_words)

pair_vocabulary = pairs_tokenize(pair_vocabulary)

bear_words = [word for word in bear_words if word not in eng_stopwords]
bull_words = [word for word in bull_words if word not in eng_stopwords]
fivemin_words = [word for word in fivemin_words if word not in eng_stopwords]
onehr_words = [word for word in onehr_words if word not in eng_stopwords]
oneday_words = [word for word in oneday_words if word not in eng_stopwords]


async def scrape_data():
    for page_no in range(1, pages):
        url = target_url + str(page_no)

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        webpage = urlopen(req).read()

        soup = bs(webpage, "html.parser")

        div_navigation = soup.find('div', id='paginationWrap')

        navigation = div_navigation.find('div', class_='sideDiv inlineblock text_align_lang_base_2').text

        if len(navigation) != 1:

            div = soup.find('div', class_='largeTitle')

            now = datetime.datetime.now()
            date = datetime.datetime

            for news_div in div.find_all('div', class_='textDiv'):
                news_title_a = news_div.find('a', class_='title')
                news_body = news_div.find('p')
                news_date = news_div.find('span', class_='date')
                news_href = news_title_a.get('href')

                if news_date is not None:
                    news_date = news_date.text

                    if 'hours' in news_date:
                        news_date = now.strftime("\xa0-\xa0%b %d, %Y")
                    if 'hour' in news_date:
                        news_date = now.strftime("\xa0-\xa0%b %d, %Y")
                    if 'minutes' in news_date:
                        news_date = now.strftime("\xa0-\xa0%b %d, %Y")

                    if '-' in news_date:
                        date_news_date = date.strptime(news_date, "\xa0-\xa0%b %d, %Y")

                        news_list.append([page_no, date_news_date, news_title_a.text, news_body.text])

                    news_dataset = pd.DataFrame(news_list, columns=['page', 'date', 'title', 'body'])

            page_no += 1

        else:
            continue

    return news_dataset


def lemmatizer(text):
    return [WordNetLemmatizer().lemmatize(word, 'v') for word in text]


def setup_and_token(dataframe):
    del dataframe['body']
    eng_stopwords = stopwords.words('english')

    dataframe.title = dataframe.title.str.replace("- ()", "")
    dataframe.title = dataframe.title.str.replace("[()\"{:,;%]", "")

    news_title = dataframe.title.astype(str)
    news_title = news_title.str.lower()

    # tokenize
    news_title = news_title.apply(word_tokenize)
    # remove stop words
    news_title = news_title.apply(lambda x: [item for item in x if item not in eng_stopwords])
    # lemmatize
    news_title = news_title.apply(lemmatizer)

    dataframe['tokenized'] = news_title

    return dataframe


def found_char(char, lst):
    the_pair = ''
    for word in lst:
        if char in word:
            the_pair = word

    return the_pair


def search_pairs(lst):
    found_pair = ''
    for trade_pair in pair_list['pairs']:
        if lst[0] in trade_pair and lst[1] in trade_pair:
            found_pair = trade_pair
    return found_pair


def sentimental_calculator(news):
    some_news = []

    for i in range(0, news.shape[0]):
        currency_pair = []

        action = 'na'
        duration = '1hr'

        bull_counter = 0
        bear_counter = 0
        duration_counter = {
            "5min": 0,
            "1hr": 0,
            "1day": 0
        }
        for word in news.tokenized[i]:
            if word in bull_words:
                bull_counter += 1

            if word in bear_words:
                bear_counter += 1

            if word in fivemin_words:
                duration_counter["5min"] += 1

            if word in onehr_words:
                duration_counter["1hr"] += 1

            if word in oneday_words:
                duration_counter["1day"] += 1

            if '/' in word:
                for trade_pair in pair_list['pairs']:
                    if word in trade_pair:
                        if trade_pair not in currency_pair:
                            currency_pair.append(trade_pair)

            else:
                for x in pair_vocabulary.keys():
                    if word.startswith(x.lower()):
                        if x.lower() not in currency_pair:
                            currency_pair.append(x.lower())

                    if word.endswith(x.lower()):
                        if x.lower() not in currency_pair:
                            currency_pair.append(x.lower())

                    else:
                        for trade_pair_vocab in pair_vocabulary[x]:
                            if word == trade_pair_vocab:
                                if x.lower() not in currency_pair:
                                    currency_pair.append(x.lower())

        x = found_char('/', currency_pair)
        if x != '':
            currency_pair = found_char('/', currency_pair)

        else:
            if len(currency_pair) > 1:
                if len(currency_pair) < 3:
                    currency_pair = search_pairs(currency_pair)

        sentiment = bull_counter - bear_counter
        if sentiment > 0:
            action = 'buy'

        else:
            if sentiment < 0:
                action = 'sell'

        duration_sentiment = max(duration_counter, key=duration_counter.get)

        some_news.append(
            [news.page[i], news.date[i], news.title[i], news.tokenized[i], action, currency_pair, duration_sentiment])

    some_news = pd.DataFrame(some_news, columns=['page', 'date', 'title', 'tokenized', 'action', 'pair', 'duration'])

    return some_news


async def tokenize():
    scraped_news_df = await scrape_data()
    news_dataframe_processed = setup_and_token(scraped_news_df)
    return pd.DataFrame(sentimental_calculator(news_dataframe_processed),
                        columns=['page', 'date', 'title', 'tokenized', 'action', 'pair', 'duration'])


async def get_fundamental_analysis():
    df = await tokenize()
    sorted_orders = []
    for i in range(0, df.shape[0]):
        for pair in df.pair[[i]]:
            if df.action[i] != 'na':
                if type(pair).__name__ != 'float':
                    if '/' in pair:
                        sorted_orders.append(
                            [df.page[i], df.date[i], df.title[i], df.action[i], df.pair[i], df.duration[i]])

    sorted_orders = pd.DataFrame(sorted_orders, columns=['page', 'date', 'title', 'action', 'pair', 'duration'])

    print('sorting completed')
    del sorted_orders["page"]
    sorted_orders.to_csv("sorted.csv",index=False)
    # sorted_json = sorted_orders.to_json(orient="records", date_format="iso")
    return sorted_orders
