# -*- coding: utf-8 -*-
# 模块用于从jd.com上提取图书的图片，根据用户的书籍名称获取对应的200*200以及350*350的图片

from bs4 import BeautifulSoup
from random import choice
import requests
import string
import shutil
import os
url = "https://search.jd.com/Search?keyword={}&enc=utf-8&book=y&wq=go&pvid={}"

# http://dx.3.cn/desc/12063121?callback=showdesc
content_jsonp_url = "http://dx.3.cn/desc/{}?callback=showdesc"


def pvid_generator():
    return ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(32))
    
def get_url_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url,headers=headers)
    r.encoding='UTF-8'
    data = r.text
    if r.status_code == 200:
        return BeautifulSoup(data,"html.parser")
    else:
        return None

def get_book_list(bookname):
    search_url = url.format(bookname.encode('utf8'),pvid_generator())
    soup = get_url_html(search_url)
    if soup==None:
        return None
    # print soup.prettify()
    first_match = soup.find("li", class_="gl-item")
    if first_match == None:
        return None

    link = first_match.find('a').get('href')
    img_200_200 = first_match.find('img').get('src')
    if img_200_200.startswith('//'):
        return (link,"http:"+img_200_200)
    else:    
        return (link,img_200_200)
    return (link,img_200_200)
def get_detail(link):
    if link.startswith('//'):
        link='http:'+link
    soup = get_url_html(link)
    if soup==None:
        print "Lost..."
        return None
    img_350_350=soup.find(id='preview').find('img').get('src')
    if img_350_350.startswith('//'):
        return "http:"+img_350_350
    else:    
        return img_350_350
def get_images_url_from_bookname(bookname):
    try:
        result = get_book_list(bookname)
        if result!=None:
            detail_link,img_200_200 = result
        try:
            img_350_350 = get_detail(detail_link)
        except expression as identifier:
            return(img_200_200,None)
        else:
            return (img_200_200,img_350_350)
    except expression as identifier:
        return(None,None)

def save_imges(url,path):
    r = requests.get(url,stream=True)
    if r.status_code == 200:
        with open(path,'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw,f)

def download_images_from_bookname(bookname,path):
      img_200_200,img_350_350 = get_images_url_from_bookname(bookname)
      if img_200_200 is not None:
          _, file_extension = os.path.splitext(img_200_200)
          save_imges(img_200_200,path+bookname+'_200_200'+file_extension)
      if img_350_350 is not None:
          _, file_extension = os.path.splitext(img_350_350)
          save_imges(img_350_350,path+bookname+'_350_350'+file_extension)    
def main():
    filename = u'微服务设计'
    path='./'
    download_images_from_bookname(filename,path)

if __name__ == '__main__':
    main()    
