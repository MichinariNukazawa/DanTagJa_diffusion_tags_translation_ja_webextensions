import json
import time
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# タグ情報を収集する関数
def get_tag_info(tag_group):
    # WebDriverを起動
    driver = webdriver.Chrome()

    try:
        # タググループのURLを開く
        driver.get(tag_group["url"])

        # "#wiki-page-body"の描画を待つ
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'wiki-page-body'))
        )

        # タグの情報を格納するリスト
        tags = []

        # タグのテーブル行を取得
        table = driver.find_element('css selector', "#wiki-page-body")
        rows = table.find_elements('css selector', ".dtext-wiki-link")

        # 各行からタグの情報を取得してリストに追加
        for row in rows:
            tag_name = row.text.strip()
            tag_url = row.get_attribute("href")

            # 直近のh5またはh4要素のテキストを取得
            #h5_or_h4_element = row.find_element(By.XPATH, "./preceding::[self::h5 or self::h4][1]")
            #h5_or_h4_text = h5_or_h4_element.text.strip()

            #tags.append({"tag_name": tag_name, "tag_url": tag_url, "more_info": h5_or_h4_text})
            tags.append({"tag_name": tag_name, "tag_url": tag_url})

        return tags

    finally:
        # WebDriverを終了する
        driver.quit()


# タググループのJSONファイルを読み込む
with open("tag_groups.json", "r", encoding="utf-8") as file:
    tag_groups = json.load(file)

# タグ情報を収集してタググループごとにファイルに書き出す
for tag_group in tag_groups:
    tags = get_tag_info(tag_group)
    group_name = tag_group["group_name"]
    output_filename = f"{group_name}_tags.json"
    output_data = {"group_name": group_name, "tags": tags}
    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)
    time.sleep(1)  # 1秒待機
