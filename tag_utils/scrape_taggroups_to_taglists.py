
import os
import json
import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin


PAGECACHE_DIR = "pagecache.taggroups" # webページのキャッシュ


def sanitize_cache_filename(filename):
    # この関数ではSlashを潰すのでパスを渡さないこと
    # ex. 'subtaggroups/Thompson/center contender.json'
    dict = {
        '#': 'SHARP',
        '%': 'PERCENT',
        '/': 'SLASH',
        ':': 'COLON',
        '*': 'ASTERISK',
        '?': 'QUESTION',
        '"': 'QUOTE',
        '<': 'LESS',
        '>': 'GREATER',
        '|': 'PIPE'
    }
    for key in dict:
        filename = filename.replace(key, dict[key])
    return filename


# タグ情報を収集する関数
def get_tag_info(driver, taggroup):
        
    # キャッシュのファイル名を生成
    cache_filename = sanitize_cache_filename(taggroup["url"].split("/")[-1]) + ".html"
    cache_filepath = os.path.abspath(os.path.join(PAGECACHE_DIR, cache_filename))
    
    # ** キャッシュファイル読み込み
    is_cache_enabled = False
    # キャッシュファイルが存在する場合は、キャッシュをロードしてdriverに読み込む
    if os.path.exists(cache_filepath):
        path = f"file:///{cache_filepath}"
        
        try:
            driver.get(path)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'wiki-page-body')))
            is_cache_enabled = True
        except:
            print(f"<grup cache error {cache_filepath}>", flush=True)

    # ** Webから取得
    # キャッシュが読めなかった場合にWebから取得
    is_loaded = False
    if not is_cache_enabled:
        #print(f"\n get. nothing:{cache_filepath}")

        is_loaded = True

        # タググループのURLを開く
        driver.get(taggroup["url"])

        # "#wiki-page-body"の描画を待つ
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'wiki-page-body'))
        )

        # ページをHTMLとしてキャッシュに書き出す
        os.makedirs(PAGECACHE_DIR, exist_ok=True)
        with open(cache_filepath, 'w', encoding='utf-8') as cache_file:
            cache_file.write(driver.page_source)

    # ** ページの解析
    # タグのテーブル行を取得
    table = driver.find_element('css selector', "#wiki-page-body")

    # BeautifulSoupを使用してHTMLをパース
    soup = BeautifulSoup(table.get_attribute('innerHTML'), 'html.parser')

    tags = []        # タグの情報を格納するリスト

    # Aタグを収集する
    # タグの情報を取得してリストに追加
    for tag in soup.find_all('a'):
        #print(tag.text.strip(), tag['href'])
        tag_name = tag.text.strip()
        tag_url = urljoin(taggroup['url'], tag['href'])

        # 括弧で囲まれたAタグを除外する
        # ex. https://danbooru.donmai.us/wiki_pages/tag_group%3Adogs
        # の「犬キャラクタ（が登場する作品）」の部分を取り除く。
        # （他で登場すると期待し、taggroup_pathの混乱を避ける。）
        #pattern = r".*[(]"
        #prev_element = tag.previous_sibling
        ##print(f"prev:`{prev}`", flush=True)
        #if prev_element is not None:
        #    print(f"prev:`{prev_element}`", flush=True)
        #    prev = prev_element.text
        #    if prev.strip() != "" and re.match(pattern, prev):
        #        print(f"exclude `{tag_name}` `{prev_element}`", flush=True)
        #        continue

        # 直近のh5またはh4要素のテキストを取得
        #h5_or_h4_element = row.find_element(By.XPATH, "./preceding::[self::h5 or self::h4][1]")
        #h5_or_h4_text = h5_or_h4_element.text.strip()

        #tags.append({"tag_name": tag_name, "tag_url": tag_url, "more_info": h5_or_h4_text})
        tags.append({"tag_name": tag_name, "taggroup_path": [taggroup["group_name"]], "tag_url": tag_url})

    # ファイル出力
    OUTPUT_DIR = "taggroups"
    taggroup_name = taggroup["group_name"]
    output_filename = os.path.join(OUTPUT_DIR, f"{taggroup_name}_tags.json")
    #output_data = {"group_name": taggroup_name, "tags": tags}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump(tags, output_file, ensure_ascii=False, indent=4)

    return is_loaded


def process():
    # タググループのJSONファイルを読み込む
    with open("tag_groups.json", "r", encoding="utf-8") as file:
        taggroups = json.load(file)

        # タグ情報を収集してタググループごとにファイルに書き出す
        for index, taggroup in enumerate(taggroups):
            is_loaded = get_tag_info(driver, taggroup)
            print(f"success:`{taggroup['group_name']}` {index}/{len(taggroups)}", flush=True)
            if is_loaded:
                time.sleep(1)  # 1秒待機


# WebDriverを起動
driver = webdriver.Chrome()

try:
    #test
    #get_tag_info(driver, {
    #    "group_name": "Tag group:Dogs",
    #    "url": "https://danbooru.donmai.us/wiki_pages/tag_group%3Adogs",
    #    "more_info": "Creatures"
    #})

    # main
    process()

finally:
    # WebDriverを終了する
    driver.quit()
