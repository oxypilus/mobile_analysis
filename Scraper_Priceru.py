import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pd.set_option('display.max_columns', None)

html_text = requests.get('https://saratov.price.ru/mobilnye-telefony/', verify=False).text
soup = BeautifulSoup (html_text,'lxml')
Phones = soup.find_all("div", itemscope="itemscope")

last_page = soup.find("ul",class_="pagination wide")
last_page = last_page.find_all("a")
last_page = int(last_page[-2].text)

count_nout = soup.find("div", class_="category-products").text
count_nout = int(count_nout.split("  ")[-3])

database = pd.DataFrame()
database["name"]=np.nan
database["min_price"]=np.nan
database["max_price"]=np.nan
database["score"]=np.nan
database["count_scores"]=np.nan
database["url"]=np.nan

step = 0

for page in range(1, last_page + 1):

    url = "https://saratov.price.ru/mobilnye-telefony/?page=" + str(page)
    print("Страница:", page, " из ", last_page)
    html_text = requests.get(url, verify=False).text
    soup = BeautifulSoup(html_text, 'lxml')
    Phones = soup.find_all("div", class_="p-card p-card__model p-card__tile")

    for i in tqdm(range(len(Phones))):

        index = i + (page - 1) * 100
        phone = Phones[i]
        href = phone.find("a")["href"]
        website = "https://saratov.price.ru"
        url = website + href

        product_html = requests.get(url, verify=False).text
        site_product = BeautifulSoup(product_html, 'lxml')

        # name
        name = site_product.find("h1", itemprop="name").text

        # price
        price = site_product.find("div", class_="price").text
        price = price.replace("\n", "")
        price = price.replace(" ", "")
        price = price.replace("\xa0", "")
        price = price.replace("₽", "")
        price = price.split("—")
        min_price = int(price[0])
        max_price = int(price[1])

        # score
        score = site_product.find("div", itemprop="ratingValue")
        score = score.text
        score = score.replace("\n", "")
        score = score.replace("\t", "")
        score = float(score)

        count_scores = site_product.find("a", class_="reviews link")  # .text

        if count_scores != None:
            count_scores = count_scores.text
            count_scores = count_scores.replace("\n", "")
            count_scores = count_scores.replace(" ", "")[0]

        else:
            count_scores = 0

        database.loc[index, "name"] = name
        database.loc[index, "min_price"] = min_price
        database.loc[index, "max_price"] = max_price
        database.loc[index, "score"] = score
        database.loc[index, "count_scores"] = count_scores
        database.loc[index, "url"] = url

        types = site_product.find("div", class_="groups")
        values = types.find_all("div", class_="value")
        types = types.find_all("span", class_="white")

        for j in range(len(types)):

            type_nout = types[j].text.replace('\n', "")
            type_nout = type_nout.replace(" ", "")
            val = values[j].text.replace("\n", "")
            val = val.replace(" ", "")

            if not (type_nout in database):
                database[type_nout] = np.nan
            database.loc[index, type_nout] = val

import datetime
name = "Mobile_dataset " + str(datetime.datetime.now()).split(".")[-2]
database.to_csv(name, sep='\t', encoding='utf-8')