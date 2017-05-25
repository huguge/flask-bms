# -*- coding: utf-8 -*-
# 模块用于从jd.com上提取图书的图片，根据用户的书籍名称获取对应的200*200以及350*350的图片

from bs4 import BeautifulSoup
from random import choice
import requests
import string
import shutil
import os
import json
import sys
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
    img_200_200_src = first_match.find('img').get('src')
    if img_200_200_src.startswith('//'):
        return (link,"http:"+img_200_200_src)
    else:    
        return (link,img_200_200_src)
    return (link,img_200_200_src)
def get_detail(link):
    if link.startswith('//'):
        link='http:'+link
    soup = get_url_html(link)
    if soup==None:
        return None
    img_350_350=soup.find(id='preview').find('img').get('src')
    if img_350_350.startswith('//'):
        return "http:"+img_350_350
    else:    
        return img_350_350
def get_images_url_from_bookname(bookname):
    _img_200_200=None
    _img_350_350=None
    try:
        result = get_book_list(bookname)
        if result!=None:
            detail_link,_img_200_200 = result
        try:
            _img_350_350 = get_detail(detail_link)
            id = detail_link.split("/")[-1].split('.')[0]
        except Exception as e:
            return (_img_200_200,None,None)
        else:
            return (_img_200_200,_img_350_350,id)
    except Exception as e:
        return (None,None,None)

def save_imges(url,path):
    r = requests.get(url,stream=True)
    if r.status_code == 200:
        with open(path,'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw,f)

def download_images_from_bookname(bookname,path):
      img_200_200_path=None
      img_350_350_path=None
      local_img_200_200,local_img_350_350,id = get_images_url_from_bookname(bookname)
      if local_img_200_200 is not None:
          _, file_extension = os.path.splitext(local_img_200_200)
          img_200_200_path = path+bookname+'_200_200'+file_extension
          save_imges(local_img_200_200,img_200_200_path)
      if local_img_350_350 is not None:
          _, file_extension = os.path.splitext(local_img_350_350)
          img_350_350_path = path+bookname+'_350_350'+file_extension
          save_imges(local_img_350_350,img_350_350_path)
      return (id,img_200_200_path,img_350_350_path)

def get_detail_info(id):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(content_jsonp_url.format(id),headers=headers)
        r.encoding='gbk'
        data = r.text
        startidx = data.find('(')
        endidx = data.rfind(')')
        info = json.loads(data[startidx + 1:endidx])
        # print info
        content = BeautifulSoup(info['content'],"html.parser")
        description = content.find("div", class_="book-detail-content").get_text().encode('utf-8')
        return (description,)
    except:
        return ("",)


def main():
    filename = u'微服务设计'
    path='./'
    id,_,_=download_images_from_bookname(filename,path)
    description = get_detail_info(id)[0]
if __name__ == '__main__':
    main()    
