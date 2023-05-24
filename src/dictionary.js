'use strict';

import { dictionary_loader } from './dictionary_loader.js';


function dictionary_normalizing_key(word){
    return word.toLowerCase().replace(/[-_]/, ' ');
}

export default class dictionary {

    constructor(name) {
        const array = dictionary_loader();
        this.dictionary_data = array.reduce(
            (a,x) => {
                const key = dictionary_normalizing_key(x.tag_name)
                a[key] = x
                return a
            }, {}
        );

        console.log('dantagja initialized');
        console.log(this.dictionary_data);
    }

    normalizing_key(word){
        return dictionary_normalizing_key(word);
    }

    isChinese(text) {
        const chineseRegex = /[\u3400-\u4DBF\u{20000}-\u{2A6DF}\u{2A700}-\u{2B73F}\u{2B740}-\u{2B81F}\u{2B820}-\u{2CEAF}\u{F900}-\u{FAFF}]/u;
        const japaneseRegex = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]/u;
    
        return chineseRegex.test(text) && !japaneseRegex.test(text);
    }

    // できるだけ日本語なrelated_tagを返す
    queryTryJaFromRelatedTags(related_tags){
        if(0 === related_tags.length) return undefined;

        const regexEn = /^[A-Za-z0-9]+$/;
        const rts0 = related_tags.filter( (rt) => (! regexEn.test(rt)) );

        const rts1 = rts0.filter( (rt) => this.isChinese(rt) );

        if(0 !== rts1.length){
            return rts1[0];
        }
        if(0 !== rts0.length){
            return rts0[0];
        }
        return related_tags[0];
    }

    querySimpleDanbooruTag(str){
        const key = dictionary_normalizing_key(str);
        return this.dictionary_data[key];
    }

    queryComplexDanbooruTags(str){
        const key = dictionary_normalizing_key(str);

        // **単語まるごとでヒットしたらそれを返す
        const res = this.dictionary_data[key];
        if(res){
            return [res];
        }

        // **そうでなかった場合、単語の分割を試す

        // 半角英数以外の変なものが混じっていたら、ここでチェック
        // (単語まるごとヒットした場合はともかくとする)
        // 顔文字は記号を含むが、フルマッチすれば弾かれない、という想定
        if( ! /^[a-zA-Z0-9\s]+$/.test(key)){
            //console.log('ext', key);
            return undefined;
        }

        // 分割
        let subKeys = key.replace(/\s+/, ' ').split(' ');
        if(2 > subKeys.length){
            return undefined;
        }
        subKeys = [subKeys[0], subKeys.slice(1).join(' ')]
        //console.log('SK', `'${str}'`, subKeys)
        // 本当は分割・連結を諸々試すべきだが簡単のため略。
        // 色＋モノ程度を想定
        // ex.'black sailor collar'
        // また、本来はこの分割・合成でマッチした場合、
        // 「その合成したタグがdanbooruに存在するか」チェックが必要だが、
        // 親データがないので今回は略とした。
        //
        // 分割マッチの場合、結果表示にマッチした文字列が必要なので、マッチしなかった文字列は文字列を返す。
        const matches = subKeys.map( (key) => {
            const res = this.dictionary_data[key];
            return (res) ? res : key;
        });
        // 分割queryで１つでもヒットすればマッチ・非マッチ混在で返す。
        // 全くヒットしていなければ非ヒットで返す
        if(!matches.some(element => typeof element !== 'string')){
            return undefined;
        }

        return matches;
    }
}