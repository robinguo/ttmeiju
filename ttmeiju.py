# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import urllib
from BeautifulSoup import BeautifulSoup
import MySQLdb
import cfscrape
import time

conn = MySQLdb.connect(host="localhost", user="root", passwd="bobobo", db="ttmeiju")
cur = conn.cursor()

urlprefix = "http://www.ttmeiju.com/meiju/Movie.html?page="
pagenum = 1
urlsuffix = ""

scraper = cfscrape.create_scraper()
while True:
    url = urlprefix + str(pagenum) + urlsuffix
    print url
    page = scraper.get(url).content
    # if page.find("出错了，您要查看页数不存在") > 0:
        # break;
    soup = BeautifulSoup(page)
    trs = soup.findAll("tr", attrs={"class":"Scontent"})
    print len(trs)
    if len(trs) == 0:
        break;
    for tr in trs:
        tds = tr.findAll("td")

        title = tds[1].text
        url = tds[1].find("a").get("href")
        id = url.split("/")[-1].split(".")[0]

        baidu_link = ""
        ed2k_link = ""
        bt_link = ""
        magnet_link = ""
        links = tds[2].findAll("a")
        for link in links:
            target_link = link.get("href")
            if "baidu" in target_link:
                baidu_link = target_link
            elif "ed2k" in target_link:
                ed2k_link = target_link
            elif "torrent" in target_link:
                bt_link = target_link
            elif "magnet" in target_link:
                magnet_link = target_link
            else:
                pass

        size = -1
        try:
            size = float(tds[3].text.split(" ")[0])
        except:
            pass

        unit = ""
        try:
            unit = tds[3].text.split(" ")[1]
        except:
            pass

        format = tds[4].text

        print id, title, url, baidu_link, ed2k_link, bt_link, magnet_link, size, unit, format
        cur.execute("SELECT id FROM movies WHERE id = %s", (id,))
        if cur.fetchone() is None:
            cur.execute('''INSERT INTO movies (id, title, url, baidu_link, ed2k_link, bt_link, magnet_link, size, unit, format, create_time, update_time)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (id, title, url, baidu_link, ed2k_link, bt_link, magnet_link, size, unit, format, int(time.time()), int(time.time())))
        conn.commit()
    pagenum += 1
    time.sleep(1)
