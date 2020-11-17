import os
import random
import re
import time

import html2text
import requests
from bs4 import BeautifulSoup
from qiniu import Auth, put_data

# todo 修改本地存储的地址
blog_folder_path: str = "D://gitclonepackage//blog//source//_posts"
# todo 修改用户名
user_name: str = "qq_32296307"
# 计数器
count = 0
# todo 修改七牛云prefix
img_prefix = "http://qjrzrivoh.hd-bkt.clouddn.com/"
# todo 修改七牛云access_key
qi_niu_access_key = "七牛access_key"
# todo 修改七牛云secret_key
qi_niu_secret_key = "七牛secret_key"
time_format = '%Y-%m-%d %H:%M:%S'


def init_global_variables():
    global blog_folder_path
    global user_name
    global count
    global img_prefix
    global qi_niu_access_key
    global qi_niu_secret_key
    global time_format


def upload_file(file_url):
    """
    download file from csdn,and upload to qiniu
    :param file_url: file_url like 'https://google.com/a.jpg'
    :return: new file url
    """
    q = Auth(qi_niu_access_key, qi_niu_secret_key)
    bucket_name = 'huskyui'
    key = str(time.time()) + str(random.randint(0, 10000)) + ".png"
    token = q.upload_token(bucket_name, key, 3600)
    # file = requests.get(file_url).content
    try:
        request = requests.get(file_url)
        if request.status_code != 200:
            return file_url
        file = request.content
        put_data(token, key, file)
        return img_prefix + key
    except:
        return file_url


def get_content(url):
    """
    get content from url
    :param url: resource url
    :return: raw
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.198 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content


def init_folder():
    """
    init local folder to save blog
    """
    # create folder
    directory = os.path.dirname(blog_folder_path)
    if not os.path.exists(directory):
        with os.mkdir(directory):
            pass


def validate_title(title):
    """
    validate title ,replace illegal character to _
    :param title: file_name
    :return: legal character
    """
    pattern = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(pattern, "_", title)
    return new_title


def build_markdown_file(url):
    """
    根据博客url生成md文件
    :param url: 博客url
    """
    html_content = get_content(url).decode("utf-8")
    # create file
    soup = BeautifulSoup(html_content, features="html.parser")
    create_time_str = soup.find_all('span', {"class": "time"})[0].text
    tags = soup.find_all('a', {"class": "tag-link"})
    markdown_tag = ''
    for tag in tags:
        markdown_tag = markdown_tag + "\n" + "- " + tag.text
    title = soup.find(id="articleContentId").contents[0]
    title = validate_title(str(title))
    article = soup.find('article')
    for img in article.find_all("img"):
        img['src'] = upload_file(img['src'])
    article = BeautifulSoup.prettify(article)
    content = html2text.html2text(article)
    hexo_prefix_template = "---\n" + "title: " + title + "\n" + "date: " + create_time_str + "\n" + "tags:" + markdown_tag + "\n---\n"
    content = hexo_prefix_template + content

    file_path = blog_folder_path + os.sep + title + ".md"
    if not os.path.exists(file_path):
        with open(file_path, 'w'):
            pass
    file = open(file_path, "a", encoding="utf-8")
    file.write(content)
    file.close()


def loop_page():
    """
    依次从第一页遍历，如果第一个存在博客，就继续遍历下一个博客
    """
    index = 1
    while loop_blog_model_in_page(index):
        index = index + 1


def loop_blog_model_in_page(page_num):
    """
    根据页数，获取是否存在博客，如果存在，就将博客下载
    :param page_num: page_num
    :return: exist blog
    """
    global count
    html_content = get_content("https://blog.csdn.net/" + user_name + "/article/list/" + str(page_num))
    soup = BeautifulSoup(html_content, features="html.parser")
    blog_model_list = soup.find_all("div", "article-item-box csdn-tracking-statistics")
    if len(blog_model_list) > 0:
        for blog_model in blog_model_list:
            blog_url = blog_model.a['href']
            print(blog_url)
            build_markdown_file(blog_url)
            count = count + 1
            print("success html to text :" + str(count))
        return True
    else:
        return False


if __name__ == '__main__':
    init_global_variables()
    loop_page()
