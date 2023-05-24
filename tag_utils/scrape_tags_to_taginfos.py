import os
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_tag_info(driver, url):
    # ページを開く
    driver.get(url)

    # タグの説明を取得
    tag_description = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'wiki-page-body'))
    )
    # タグの説明の子要素を取得
    child_elements = tag_description.find_elements(By.XPATH, './child::*')

    # 子要素を文字列化して配列に格納
    child_texts = [element.get_attribute('textContent').strip() for element in child_elements]

    # タグの関連タグを取得
    elements = driver.find_elements(By.CLASS_NAME, 'wiki-other-name')
    other_names = [element.text.strip() for element in elements]

    # タグ情報を辞書として返す
    tag_info = {
        'tag_descriptions': child_texts,
        'related_tags': other_names
    }

    return tag_info


def process_tag_groups():
    tag_groups_dir = "taggroups"  # taggroupsディレクトリのパスを指定する

    for file_name in os.listdir(tag_groups_dir):
        file_path = os.path.join(tag_groups_dir, file_name)

        if not file_name.endswith(".json"):
            continue  # JSONファイル以外はスキップ

        with open(file_path, "r", encoding="utf-8") as file:
            tag_group = json.load(file)
            group_name = tag_group["group_name"]
            tag_infos = []

            print(f"group:`{group_name}` count:{len(tag_group['tags'])}", end="", flush=True)

            if os.path.isfile(save_file_path(file_name)):
                print(f" skiped by already", flush=True)
                continue  # すでにあるファイルはスキップ

            if is_blacklisted(group_name):
                print(f" skiped by bkacklist", flush=True)
                continue  # ブラックリストに一致するタググループはスキップ

            for tag in tag_group["tags"]:
                tag_info = get_tag_info(driver, tag["tag_url"])
                tag_info["tag_name"] = tag["tag_name"]
                tag_info["taggroup"] = group_name
                tag_infos.append(tag_info)
                print(f".", end="", flush=True)
                time.sleep(2)

            save_tag_info(file_name, tag_infos)

        print(f" end", flush=True)
        time.sleep(5) # 1秒待機


def is_blacklisted(file_name):
    blacklist = ["tag group:metatags", "Pool Groups", "List of Meta-Wikis", "List of Pokémon",
     "List of Digimon", 'Tag group:Audio tags', 'List of disambiguation pages', 
     'Tag group:Companies and brand names', 'List of airplanes', 'List of named drawfags', 
     'List of official mascots']  # ブラックリストのファイル名先頭を指定する
    # TODO audio以降はwebdriverがクラッシュしたので一旦避けただけ
    blacklist_tail = ["characters", "List of Meta-Wikis"]  # ブラックリストのファイル名先頭を指定する

    for blacklisted_name in blacklist:
        if file_name.startswith(blacklisted_name):
            return True
    for blacklisted_name in blacklist_tail:
        if file_name.endswith(blacklisted_name):
            return True

    return False

def save_file_path(file_name):
    output_dir = "taginfos"  # taginfosディレクトリのパスを指定する
    output_file_name = os.path.splitext(file_name)[0] + ".json"
    output_path = os.path.join(output_dir, output_file_name)
    return output_path

def save_tag_info(file_name, tag_infos):
    output_path = save_file_path(file_name)

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(tag_infos, output_file, indent=4, ensure_ascii=False)
        print("Tag info saved to:", output_path)


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
    process_tag_groups()

finally:
    # WebDriverを終了する
    driver.quit()
