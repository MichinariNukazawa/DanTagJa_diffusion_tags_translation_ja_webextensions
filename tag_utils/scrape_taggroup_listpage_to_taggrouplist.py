import json
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# タググループとURLのセットを取得する関数
def get_tag_groups():
    # Chrome WebDriverのオプションを設定
    options = Options()
    #options.add_argument('--headless')  # ヘッドレスモードで実行
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # WebDriverを起動
    driver = webdriver.Chrome(options=options)

    try:
        # タググループのページを開く
        driver.get("https://danbooru.donmai.us/wiki_pages/tag_groups")

        # タググループとURLのセットを格納するリスト
        tag_groups = []

        # タググループのテーブル行を取得
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'wiki-page-body'))
        )
        table = driver.find_element('css selector', "#wiki-page-body")
        rows = table.find_elements('css selector', ".dtext-wiki-link")

        # 各行からタググループとURLを取得してリストに追加
        for row in rows:
            group_name = row.text.strip()
            group_url = row.get_attribute("href")

            # 直近のh6要素の文字列を取得
            h6_element = row.find_element(By.XPATH, "./preceding::h6[1]")
            h6_text = h6_element.text.strip()

            tag_groups.append({"group_name": group_name, "url": group_url, "more_info": h6_text})

        return tag_groups

    finally:
        # WebDriverを終了する
        driver.quit()

# タググループとURLのセットを取得
tag_groups = get_tag_groups()

# 結果をJSONファイルに出力
with open("tag_groups.json", "w", encoding="utf-8") as file:
    json.dump(tag_groups, file, ensure_ascii=False, indent=4)
