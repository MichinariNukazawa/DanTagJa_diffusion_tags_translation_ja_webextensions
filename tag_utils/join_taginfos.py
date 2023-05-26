import os
import json
import sys
import re

args = sys.argv


# 「廃止されたタグ」は収集しない
def is_enable_page_by_tag_descriptions(tag_descriptions):
    for txt in tag_descriptions:
        if 'Ambiguous tag.' in txt:
            return False
        if 'This tag is deprecated' in txt:
            return False
    return True
#if not is_enable_page_by_tag_descriptions(tag_info['tag_descriptions']):
#    print(f"<deprecated tag `{true_tag_name}`>", flush=True)


def dictionary_normalizing_key(tag):
    return re.sub(r'[_-]', ' ', tag.lower())


def is_japanese(text):
    japanese_regex = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]", re.UNICODE)
    return bool(japanese_regex.search(text))


def is_chinese(text):
    #chinese_regex = re.compile(r"[\u3400-\u4DBF\u20000-\u2A6DF\u2A700-\u2B73F\u2B740-\u2B81F\u2B820-\u2CEAF\uF900-\uFAFF]", re.UNICODE)
    chinese_regex = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")

    return bool(chinese_regex.search(text)) and not is_japanese(text)


def query_try_ja_from_related_tags(related_tags):
    if len(related_tags) == 0:
        return None

    regex_en = re.compile(r"^[A-Za-z0-9]+$")
    rts0 = list(filter(lambda rt: not regex_en.match(rt), related_tags))
    rts1 = list(filter(is_chinese, rts0))
    rts2 = list(filter(lambda rt: not is_japanese(rt), rts1))
    print(rts0, rts1, rts2);

    if len(rts2) != 0:
        return rts2[0]
    if len(rts1) != 0:
        return rts1[0]
    if len(rts0) != 0:
        return rts0[0]
    return related_tags[0]


def process_tag_infos(tags_dir):
    tag_dict = {}


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

                # fix old data
                if ('taggroup_path' in tag):
                    taggroup = tag["taggroup_path"][0]
                elif ('taggroup' in tag):
                    taggroup = tag["taggroup"]
                    tag['taggroup_path'] = [taggroup]
                elif ('group_path' in tag):
                    taggroup = tag["group_path"][0]
                    tag['taggroup_path'] = tag["group_path"]
                else:
                    print('Error', tag["tag_name"], tag)
                    continue

                def is_blacklist_taggroup(taggroup):
                    blacklist = ['List of tagged songs', 'List of uniforms']
                    return taggroup in blacklist

                if is_blacklist_taggroup(taggroup):
                    continue

                key = dictionary_normalizing_key(tag["tag_name"])
                if key in tag_dict:
                    already = tag_dict[key]
                    print(f"dup key:`{key}` already:`{already['tag_name']}` new:`{tag['tag_name']}`", flush=True)
                    #print(f" :{already['taggroup_path']} :{tag['taggroup_path']}", flush=True)
                    if len(tag['taggroup_path']) < len(already['taggroup_path']):
                        tag_dict[key] = tag
                else:
                    tag_dict[key] = tag

    tag_infos = []
    for tag in tag_dict.values():
        tag_info = {}
        tag_info["tag_name"] = tag["tag_name"]
        #tag_info["taggroup"] = taggroup
        #tag_info["related_tags"] = tag["related_tags"]
        #tag_info["tag_description"] = tag_description
        # しばらく使用する予定がないので、related_tagsの候補を予め１つに絞り込んでしまう
        ja = query_try_ja_from_related_tags(tag["related_tags"])
        tag_info["related_tags"] = [ja] if ja is not None else []

        tag_infos.append(tag_info)

    save_tag_info(tag_infos)

def save_tag_info(tag_infos):
    output_path = os.path.join('../src/content_scripts', 'dictionary_loader.js')

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("'use strict';\nexport function dictionary_loader(){\nreturn ")
        json.dump(tag_infos, output_file, indent=2, ensure_ascii=False)
        output_file.write("\n}")
        print("Tag info saved to:", output_path)

process_tag_infos(args[1])

# test
#print(query_try_ja_from_related_tags(["脸红", "赤面", "頬染め"]))
#print(is_chinese("脸红"), is_japanese("脸红"))
#print(is_chinese("赤面"), is_japanese("赤面"))
