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
    return bool(re.compile(r'[ぁ-んァ-ヶ一-龯]+').search(text))

def is_chinese(text):
    #chinese_regex = re.compile(r"[\u3400-\u4DBF\u20000-\u2A6DF\u2A700-\u2B73F\u2B740-\u2B81F\u2B820-\u2CEAF\uF900-\uFAFF]", re.UNICODE)
    #chinese_regex = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
    chinese_pattern = r'[\u4E00-\u9FFF]+'
    return bool(re.compile(chinese_pattern).search(text))
    #return bool(chinese_regex.search(text)) and not is_japanese(text)


r_en = r'^[A-Za-z0-9\!\"#$%&\'()*+,-./:;<=>?@[\\\]^_`{|}~]+$'
regex_en = re.compile(r_en)
r_numAndSymbol = r'^[0-9\!\"#$%&\'()*+,-./:;<=>?@[\\\]^_`{|}~]+$'
regex_numAndSymbol = re.compile(r_numAndSymbol)

# 辞書は先頭が擬音だったり微妙なので、並び替える。
def query_try_ja_from_edict(texts):
    if len(texts) == 0:
        return None


    regex_kanji = re.compile(r'[一-龯]')

    # 漢字のみ
    rts0 = list(filter(lambda rt: regex_kanji.match(rt), texts))
    if len(rts0) != 0:
        return rts0[0]
    # 漢字混じり
    rts1 = list(filter(lambda rt: regex_kanji.search(rt), texts))
    if len(rts1) != 0:
        return rts1[0]
    # 諦めて英数のみのものを取り除いた残り(ひらがなのみとか？)
    rts2 = list(filter(lambda rt: not regex_en.match(rt), texts))
    if len(rts2) != 0:
        return rts2[0]

    # 翻訳結果が英数字のみのものもありと有る模様
    #print('only 英数字', texts)
    return texts[0]


def query_try_ja_from_related_tags(related_tags):
    if len(related_tags) == 0:
        return None

    # 日本語判定
    # (Unicodeコードポイントでの判定は、まだらな入り混じりになっているため機能しない。)
    # (データベースを用意しないと無理)
    # かな漢字混じりならほぼ確実
    # -> というのをがんばってみたのだが、
    # diffを見る限り最初から日本語だった部分の結果が悪化している箇所のほうが多いので廃案
    #def kanakanji(txt):
    #    print(txt)
    #    return bool(re.compile(r'[ぁ-んァ-ヶ]').search(txt)) and bool(re.compile(r'[\u4E00-\u9FFF]').search(txt))
    #kks = list(filter(lambda rt: kanakanji(rt), related_tags))
    
    # かといって次の候補を「かなのみ」などにすると結果がヘンなことになると思われるが。
    # まだ中文漢字で結果が表示されるほうが格好がつくだろうという判断。

    # とりあえず英文記号のみのものを取り除く
    rts0 = list(filter(lambda rt: not regex_en.match(rt), related_tags))

    if len(rts0) != 0:
        return rts0[0]
    return related_tags[0]

def query_edict_simple(key):
    if 'the' == key: # 結果が「そん」で「ソニック+そん+ヘッジホッグ」みたいなことになるので...
        return None
    if 'a' == key:
        return None
    if 2 >= len(key):
        return None
    
    # 優先度設定によっては「綬」などになるので
    if 'ribbon' == key:
        return 'リボン'
    
    if key in edict:
        return edict[key]
    elif 2 < len(key) and key.endswith('es'):
        key2 = key.rstrip('es')
        if key2 in edict:
            return edict[key2]
    elif 1 < len(key) and key.endswith('s'):
        key2 = key.rstrip('s')
        if key2 in edict:
            return edict[key2]
    elif 2 < len(key) and key.endswith('ed'):
        key2 = key.rstrip('ed')
        if key2 in edict:
            return edict[key2]
    elif 2 < len(key) and key.endswith('ing'):
        key2 = key.rstrip('ing')
        if key2 in edict:
            return edict[key2]
    return None


def query_edict_split(keystr):
    # 戦闘機などがひどい結果になってしまうので、英数のみや数字の含まれるものは弾く。
    if regex_numAndSymbol.match(keystr):
        return []
    if re.compile(r'[0-9]').search(keystr):
        return []
    
    ja = query_edict_simple(keystr)
    if ja is not None:
        return [ja]

    # TODO 本当は2word連結などの検索が必要
    detected = False
    ret = []
    for key in keystr.split(' '):
        ja = query_edict_simple(key)
        if ja is not None:
            detected = True
            ret.append(ja)
        else:
            ret.append(key)

    if detected:
        return ret
    else:
        return []


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
                    #print(f"dup key:`{key}` already:`{already['tag_name']}` new:`{tag['tag_name']}`", flush=True)
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

        # 英語辞書を引く
        # 英語の割あたっているものを
        #if 0 == len(tag_info["related_tags"]) or regex_en.match(tag_info["related_tags"][0]):
        if 0 == len(tag_info["related_tags"]):
             key = dictionary_normalizing_key(tag["tag_name"])
             jas = query_edict_split(key)
             if 0 != len(jas):
                 #print('aa','+'.join(jas))
                 tag_info["related_tags"] = ['+'.join(jas)]

        tag_infos.append(tag_info)

    save_tag_info(tag_infos)

def save_tag_info(tag_infos):
    output_path = os.path.join('../src/content_scripts', 'dictionary_loader.js')

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("'use strict';\nexport function dictionary_loader(){\nreturn ")
        json.dump(tag_infos, output_file, indent=2, ensure_ascii=False)
        output_file.write("\n}")
        print("Tag info saved to:", output_path)


edict = {}
with open("dictionary_edict.json", "r", encoding="utf-8") as file:
    arr = json.load(file)
    for data in arr:
        key = dictionary_normalizing_key(data[0])
        edict[key] = query_try_ja_from_edict(data[1].split(';'))

process_tag_infos(args[1])

# test
#print(query_try_ja_from_related_tags('単純;お安い;さっぱり;た易い;ちょろい;わけが無い;シャシャ;シンプル;チョロい;ラクチン;安易;安直;易々;易しい;易易;楽;楽ちん;楽チン;簡易的;簡素;簡単;簡短;簡端;簡略;軽い;軽易;御安い;雑作もない;雑作も無い;事無し;疾い;質素;手っ取り早い;手軽;柔婉;淳朴;純朴;醇朴;捷い;生やさしい;生易しい;素朴;素樸;早い;造作ない;造作もない;造作も無い;造作無い;速い;単;単なる;単一;淡々;淡淡;淡泊;淡白;地味;直線的;惇朴;惇樸;敦朴;敦樸;馬鹿でもチョンでも;卑近;平たい;平ちゃら;平ったい;平易;平淡;平明;朴とつ;朴訥;無技巧;無雑作;無造作;木訥;訳がない;訳が無い;訳ない;訳無い;容易;容易い;扁たい;洒々;洒洒;澹々;澹泊;澹澹'.split(';')))
#print(query_try_ja_from_related_tags(["脸红", "赤面", "頬染め"]))
#print(query_try_ja_from_related_tags(['G43/K43', 'ワルサーGew43半自動小銃', 'ワルサーGew43']))
#print(is_chinese("red"), is_chinese("脸红"), is_chinese("赤面"), is_chinese("頬染め"))
#print(is_japanese("red"), is_japanese("脸红"), is_japanese("赤面"), is_japanese("頬染め"))
