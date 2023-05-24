import os
import json
import sys

args = sys.argv

def process_tag_infos(tags_dir):
    tag_infos = []

    for file_name in os.listdir(tags_dir):
        file_path = os.path.join(tags_dir, file_name)

        if not file_name.endswith(".json"):
            continue  # JSONファイル以外はスキップ

        with open(file_path, "r", encoding="utf-8") as file:
            tags = json.load(file)
            
            for tag in tags:
                #print(tag)

                #
                if tag["tag_name"].lower().startswith('tag group'):
                    continue

                # ex. "List of style parodies",
                if tag["tag_name"].lower().startswith('list of '):
                    continue

                if 0 == len(tag['tag_descriptions']):
                    tag_description = ''
                elif tag['tag_descriptions'][0].startswith("This wiki page does not exist."):
                    tag_description = ''
                else:
                    tag_description = tag["tag_descriptions"][0]

                tag_info = {}
                tag_info["tag_name"] = tag["tag_name"]
                tag_info["taggroup"] = tag["taggroup"]
                tag_info["related_tags"] = tag["related_tags"]
                tag_info["tag_description"] = tag_description
                tag_infos.append(tag_info)

    save_tag_info(file_name, tag_infos)

def save_tag_info(file_name, tag_infos):
    output_path = os.path.join('./', 'dictionary_loader.js')

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("'use strict';\nfunction dictionary_loader(){\nreturn ")
        json.dump(tag_infos, output_file, indent=2, ensure_ascii=False)
        output_file.write("\n}")
        print("Tag info saved to:", output_path)

process_tag_infos(args[1])
