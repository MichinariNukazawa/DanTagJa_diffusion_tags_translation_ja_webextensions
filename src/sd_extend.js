'use strict';

let sec = 0;

export function sd_extend_init(dictionary){
    console.log('sd_extend init');

    let count = 0;
    const parentIds = ['txt2img_prompt', 'txt2img_neg_prompt']
    parentIds.forEach( (parentId) => {
        console.log('sd_extend', parentId);

        let parent = document.getElementById(parentId);
        if(! parent){
            console.log('nothing', parentId);
            return;
        }

        let olds = parent.getElementsByClassName('dantagja__translated')
        if(0 !== olds.length){
            console.log('sd_extend already', olds.length);
            Array.from( olds ).forEach(elem => {
                elem.remove()
            });
        }

        let prompt = parent.getElementsByTagName('textarea')[0];

        let translatedElem = document.createElement("textarea");
        translatedElem.classList.add('dantagja__translated');
        translatedElem.style = prompt.style;
        translatedElem.style.width = "100%";
        translatedElem.style.height = "160px";
        translatedElem.style.marginTop = "8px";
        translatedElem.style.borderRadius = "8px";
        translatedElem.style.fontSize = "70%";
        translatedElem.style.border = "solid 1px black"; 
        translatedElem.readOnly = true;
        parent.appendChild(translatedElem)

        const updateText = () => {
            let tranByLines = [];
            prompt.value.split(/[\n\r]/).forEach(lineStr => { // 改行で分割
                let tranBySemis = [];
                lineStr.split(',').forEach(semicolonStr => { // ','で分割(確実にワード境界)
                    if(/^[\s　]*$/.test(semicolonStr)){ return; }

                    let transByIdioms = [];
                    // TODO 本当はここで'joined-idiom'と'this is idiom?'を区別して対応したいが一旦置く。
                    // TODO このあたりで'()'などに囲われている単語の処理をする必要があるが一旦置く。
                    let words = semicolonStr.replace(/(:-?[0-9.]+)/g, '').replace(/[(){}]+/g, ' ').replace(/[\s]+/g, ' ').trim().split(' ');
                    words = words.map(word => dictionary.normalizing_key(word));
                    let i = 0;
                    while(i < words.length){
                        for(let t = Math.min(5, words.length - i); 0 < t; t--){
                            const idiom = words.slice(i, i+t).join(' ');
                            console.log('loop', parentId, i, t, `idiom:'${idiom}'`, words.length, words);
                            const matched = dictionary.querySimpleDanbooruTag(idiom);
                            if(matched){
                                let translated = dictionary.queryTryJaFromRelatedTags(matched.related_tags);
                                if(!translated){ translated = idiom;}
                                transByIdioms.push(`<${translated}>`)
                                i += t;
                                break;
                            }else if(1 == t){
                                transByIdioms.push(`<?${idiom}>`)
                                i++;
                                break;
                            }
                            // next
                        }
                    }
                    tranBySemis.push(transByIdioms.join(' '));
                });
                tranByLines.push(tranBySemis.join(','));
            });
            translatedElem.textContent = tranByLines.join('\n');
        }

        prompt.removeEventListener('input', updateText);
        prompt.addEventListener("input", updateText);

        updateText();

        count++;
    });
    if(30 < sec){
        console.log('sd_extent init exit', count, parentIds.length, sec)
    }else if(count < parentIds.length){
        setTimeout(sd_extend_init, 2000);
        sec+=2;
    }else{
        console.log('sd_extent init exit', count, parentIds.length, sec)
    }
}