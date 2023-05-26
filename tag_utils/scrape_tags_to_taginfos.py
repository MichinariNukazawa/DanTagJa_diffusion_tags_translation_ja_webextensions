import os
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import re
import copy
from urllib.parse import unquote


TAGGROUPS_DIR = "taggroups"  # taggroupsディレクトリのパスを指定する
SUBTAGGROUPS_DIR = "subtaggroups"  # subtaggroupsディレクトリのパスを指定する
TAGINFOS_DIR = "taginfos"  # taginfosディレクトリのパスを指定する
PAGECACHE_DIR = "pagecache.tagpages" # webページのキャッシュ


def sanitize_to_filename(filename):
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


def scrape_tag_info(driver, url, tag_name):

    # ** キャッシュファイル読み込み
    is_cache_enabled = False
    # キャッシュのファイル名を生成
    cache_filename = sanitize_to_filename(unquote(url.split("/")[-1])) + ".html"
    cache_filepath = os.path.abspath(os.path.join(PAGECACHE_DIR, cache_filename))
    # キャッシュファイルが存在する場合は、キャッシュをロードしてdriverに読み込む
    if os.path.exists(cache_filepath):
        path = f"file:///{cache_filepath}"
        
        try:
            driver.get(path)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'wiki-page-body')))
            is_cache_enabled = True
        except:
            print(f"<grup cache error {cache_filepath}>", flush=True)

        is_check_cache = False
        if is_check_cache:
            # (あくまで簡易なものとして)キャッシュがおかしくなっていないか確認する
            # <cache title missmatch `Spade (Shape) Wiki | Danbooru` `Spades`>
            # <cache title missmatch `Fate (Series) Wiki | Danbooru` `Fate series`>
            def removeBlacket(str):
                return re.sub(r'\([^()]*\)', '', str).strip()
            def removePlural(str):
                return re.sub(r'(s|es)$', '', str)
            tt = removePlural(removeBlacket(driver.title.replace(' ', '_').lower().strip()))
            tn = removePlural(removeBlacket(tag_name.replace(' ', '_').lower().strip()))
            if not tt.startswith(tn):
                print(f"<cache title missmatch `{driver.title}` `{tag_name}`>", flush=True)
                is_cache_enabled = False

    # ** Webから取得
    # キャッシュが読めなかった場合にWebから取得
    is_loaded = False
    if not is_cache_enabled:
        #print(f"\n get. nothing:{cache_filepath}")

        is_loaded = True
        # キャッシュファイルが存在しない場合は、URLのページを開く
        driver.get(url)

        # (ページ読み込み直後はまだscrapingしたいデータが書かれていないので) DOMが構築されるのを待つ
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'wiki-page-body')))

        # ページをHTMLとしてキャッシュに書き出す
        with open(cache_filepath, 'w', encoding='utf-8') as cache_file:
            cache_file.write(driver.page_source)

    # (ページ描画の完了待ちを兼ねる)
    # タグの説明を取得
    wpb_element = driver.find_element('css selector', "#wiki-page-body")
    
    # タグの説明の子要素を取得
    description_elements = wpb_element.find_elements(By.XPATH, './child::*')
    # 子要素を文字列化して配列に格納
    description_texts = [element.get_attribute('textContent').strip() for element in description_elements]

    # リンク元からでない本当のタグ名を取得
    true_tag_name = unquote(url.split("/")[-1]) 
    #true_tag_name = driver.find_elements(By.ID, 'wiki-page-title').text.strip()

    # タグの関連タグを取得
    elements = driver.find_elements(By.CLASS_NAME, 'wiki-other-name')
    other_names = [element.text.strip() for element in elements]

    # タグ情報を辞書として返す
    tag_info = {
        'tag_name': true_tag_name,
        'url': url,
        'tag_descriptions': description_texts,
        'related_tags': other_names
    }
    #print('debug', tag_info['url'], tag_info['related_tags'])

    # subtagsを探索
    subtag_links = wpb_element.find_elements(By.XPATH, './/a')
    subtags = []

    for link in subtag_links:
        subtag_name = link.text.strip()
        subtag_url = link.get_attribute("href")
        
        if not subtag_url.startswith("https://danbooru.donmai.us/wiki_pages/"):
            continue

        if subtag_url.startswith(url):
            continue

        # タググループ等は除外（新しいTagGroupの可能性もあるがキリがなくなるので）
        def is_blacklist(tag_url):
            pagename = tag_url.split("/")[-1]
            blacklist_starts = ["tag_group", "list_of", "help:"]
            for bl in blacklist_starts:
                if pagename.lower().startswith(bl):
                    return True
            return False

        if is_blacklist(subtag_url):
            continue

        subtag_object = {
            "tag_name": subtag_name,
            "tag_url": subtag_url
        }
        subtags.append(subtag_object)

    return (tag_info, is_loaded, subtags)


def is_blacklisted_by_tag_name(taggroup_name):
    blacklist = ["tag group:metatags", "Pool Groups", "List of Meta-Wikis", "help:"
                 "tag_groups", "tag_group:",
                "Pokémon ", "Pokémon card", "Pokémon Trading Card Game", 
                "List of Digimon", 'Tag group:Audio tags', 'List of disambiguation pages', 
                'Tag group:Companies and brand names', 'List of named drawfags', 
                'List of official mascots'
    ]  # ブラックリストのtag名先頭を指定する
    # pokemonは数が多いので...(?) カードはともかくポケモン自体は収録するべきとは思う
    # TODO audio以降はwebdriverがクラッシュしたので一旦避けただけ
    blacklist_tail = ["characters", "List of Meta-Wikis"]  # ブラックリストのtag名末尾を指定する

    for blacklisted_name in blacklist:
        if taggroup_name.startswith(blacklisted_name):
            return True
    for blacklisted_name in blacklist_tail:
        if taggroup_name.endswith(blacklisted_name):
            return True
    return False

def is_blacklisted_by_taggroup_path(taggroup_path):
    for taggroup_name in taggroup_path:
        if is_blacklisted_by_tag_name(taggroup_name):
            return True
    return False


def process_tag(tag):
    #print(f"Start tag:`{tag['tag_name']}` path:{tag['taggroup_path']}", end="", flush=True)

    if is_blacklisted_by_tag_name(tag['tag_name']):
        print(f" skiped by bkacklist tag_name", flush=True)
        return (None, False) # ブラックリストに一致するタグはスキップ
    if is_blacklisted_by_taggroup_path(tag['taggroup_path']):
        print(f" skiped by bkacklist taggroup_path", flush=True)
        return (None, False) # ブラックリストに一致するタググループはスキップ

    # 入れ子を検出した場合、同じグループに戻る無限ループに入っているのでスキップ
    if len(tag['taggroup_path']) != len(set(tag['taggroup_path'])):
        print(f" skiped by duplicated in taggroup_path", flush=True)
        return (None, False)

    # 再帰が深すぎるので抜ける
    # （無限ループを検出できていないのかもしれないので）
    # （他で見つかることを期待して）
    if 4 < len(tag['taggroup_path']):
        print(f" skiped by deep taggroup_path", flush=True)
        return (None, False)
    
    # 独立ページではないと判断してスキップ
    last_url = tag["tag_url"].split('/')[-1]
    if "#" in last_url or "?" in last_url:
        print(f" skiped by subpage url `{tag['tag_url']}`", flush=True)
        return (None, False)

    (taginfo, is_loaded_, subtags) = scrape_tag_info(driver, tag["tag_url"], tag["tag_name"])
    taginfo["taggroup_path"] = tag['taggroup_path']
    if is_loaded_:
        print(f"+", end="", flush=True)
    else:
        print(f"-", end="", flush=True)

    # 再帰的探索(ページ内で見つけたtagsをページ毎に保存)
    if 0 != len(subtags):
        subgroup_path = copy.deepcopy(tag['taggroup_path'])
        subgroup_path.append(tag["tag_name"])
        subtagsinfo = {'group_path': subgroup_path, 'tags': subtags}
        stsi_path = os.path.join(SUBTAGGROUPS_DIR, sanitize_to_filename(tag["tag_name"]) + ".json")
        save_to_json(stsi_path, subtagsinfo)

    return (taginfo, is_loaded_)


def process_tag_group(file_path):
    gname = file_path.split('/')[-1].split('.')[0]

    output_path = save_file_path(gname)
    #if os.path.isfile(output_path):
    #    print(f" skiped by already", flush=True)
    #    return # すでにあるファイルはスキップ

    is_loaded = False
    with open(file_path, "r", encoding="utf-8") as file:
        tags = json.load(file)
        print(f"group:`{gname}` count:{len(tags)}", flush=True)

        taginfos = []
        for tag in tags:
            (taginfo, is_loaded_) = process_tag(tag)
            is_loaded = is_loaded & is_loaded_
            if taginfo is not None:
                taginfos.append(taginfo)
            # sleep
            if is_loaded_:
                time.sleep(0.5) # Webアクセスした場合は待機

    # タグ情報をファイル書き出し
    if 0 == len(taginfos):
        print(f"<tag_infos nothing>", flush=True)
    else:
        save_to_json(output_path, taginfos)

    print(f"\n successed. group:`{gname}` `{output_path}`", flush=True)

    if is_loaded:
        time.sleep(5)


def process_tag_groups():
    for taggroup_file_name in os.listdir(TAGGROUPS_DIR):
        file_path = os.path.join(TAGGROUPS_DIR, taggroup_file_name)

        if not taggroup_file_name.endswith(".json"):
            continue  # JSONファイル以外はスキップ

        process_tag_group(file_path)

def process_subtag_groups():
    for taggroup_file_name in os.listdir(SUBTAGGROUPS_DIR):
        file_path = os.path.join(SUBTAGGROUPS_DIR, taggroup_file_name)

        if not taggroup_file_name.endswith(".json"):
            continue  # JSONファイル以外はスキップ

        process_tag_group(file_path)

def save_file_path(group_name):
    file_name = sanitize_to_filename(group_name) + ".json"
    output_path = os.path.join(TAGINFOS_DIR, file_name)
    return output_path

def save_to_json(output_path, tag_infos):
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(tag_infos, output_file, indent=4, ensure_ascii=False)
        #print("Tag info saved to:", output_path)


options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
# 画像を非表示にする（おそらくダウンロードはする）
options.add_argument('--blink-settings=imagesEnabled=false')
# おそらく画像のダウンロードをブロックできる
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

# WebDriverを起動
driver = webdriver.Chrome(options=options)

try:
    # test
    #process_tag_group('./taggroups/Tag group:Ears tags_tags.json')
    #process_tag_group('./taggroups/Tag group:Dogs_tags.json')
    #process_tag_group('./taggroups/List of airplanes_tags.json')

    # main
    process_tag_groups()
    # TODO
    #process_subtag_groups()

finally:
    # WebDriverを終了する
    driver.quit()
