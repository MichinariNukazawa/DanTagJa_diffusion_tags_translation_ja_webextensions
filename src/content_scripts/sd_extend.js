'use strict';

function sd_extend_inserting(dictionary){
    const parentIds = ['txt2img_prompt', 'txt2img_neg_prompt', 'img2img_prompt', 'img2img_neg_prompt']
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
        //translatedElem.style.backgroundColor = prompt.style.backgroundColor;
        //translatedElem.style.color = prompt.style.color;
        translatedElem.style.backgroundColor = "#111c";
        translatedElem.style.color = "#ddd";
        translatedElem.style.width = "100%";
        translatedElem.style.height = "160px";
        translatedElem.style.marginTop = "8px";
        translatedElem.style.borderRadius = "8px";
        translatedElem.style.fontSize = "70%";
        translatedElem.style.border = "solid 2px #777"; 
        translatedElem.readOnly = true;
        parent.appendChild(translatedElem)

        const updateText = () => {
            console.log('sd_extend updateText', parentId);
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
                            //console.log('loop', parentId, i, t, `idiom:'${idiom}'`, words.length, words);
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

        // 定期検出のみで十分だし処理が重複してしまうが、これもあったほうが反応が早くなるので
        prompt.removeEventListener('input', updateText);
        prompt.addEventListener("input", updateText);

        // 定期的に値の変更を確認することで、jsによる書き換えを検出（保存済みstyleのpromptへの書き出し）
        // (MutationObserverはtextarea.valueに対しては機能しない)
        {
            let prevValue = prompt.value;
            function checkTextareaChange() {
                const currentValue = prompt.value;
                if (currentValue !== prevValue) {
                    // 値の変更を検出した後の処理をここに記述します
                    updateText();
                    prevValue = currentValue; // 監視用の変数を更新
                }
            }
            setInterval(checkTextareaChange, 1000);
        }

        updateText();
    });
}

export function sd_extend_init(dictionary){
    console.log(`sd_extend init '${document.title}'`);
    // SDであることの判定を、titleで行っている。
    // SDはページのロード中はtitleが空文字で、完了すると'Stable Diffusion'になる。

    if('Stable Diffusion' === document.title){
        console.log('sd_extend detected');
        sd_extend_inserting(dictionary);
    }else{
        console.log('sd_extend set oveserve');
        new MutationObserver(function(mutations) {
            console.log('sd_extend mutate', mutations[0].target.nodeValue, document.title);
            if('Stable Diffusion' === document.title){
                sd_extend_inserting(dictionary);
            }
        }).observe(
            document.querySelector('title'),
            { subtree: true, characterData: true, childList: true }
        );
    }
}

