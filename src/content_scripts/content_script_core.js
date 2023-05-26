'use strict';

import { sd_extend_init } from './sd_extend.js';

// node inserting, ja translated text nodes
const insertJaNodeDanbooruTag = (dictionary, node) => {
	//if('IMG' === node.nodeName) return false;
	//if('SOURCE' === node.nodeName) return false;
	//if('SVG' === node.nodeName) return false;
	//if('PICTURE' === node.nodeName) return false;
	//if('ARTICLE' === node.nodeName) return false;

	if('A' !== node.nodeName) return false;

	let content = node.textContent;

	if('?' === content) return false; // TODO wikiページへのリンクにマッチしてしまうため一時無効
	if('' === content.trim()) return false;
	if(80 < content.length) return false;

	//console.log('node', node, `'${content}'`);

	if(/[\n\r]/.test(content)) return false;

	let matchesed = dictionary.queryComplexDanbooruTags(content);

	if( ! matchesed || 0 === matchesed.length ){
		if( ! node.classList.contains('search-tag') ){
			return false;
		}else{
			matchesed = [];
		}
	}
	//console.log('match ret', content, matchesed.length);

	let ja;
	let kind = ''
	if(0 == matchesed.length){
		kind = `?` // "<?*>"「知らないタグ」の表現(danbooruのサイト上の画像左のタグ表示にて)
	}else if(1 == matchesed.length){
		const rt = dictionary.queryTryJaFromRelatedTags(matchesed[0].related_tags);
		if(rt){
			ja = `<${rt}>`
		}else{
			kind = '#' //ja = '<#>'; // "<#*>"「タグはあるが翻訳がない」の表現
		}
	}
	// 翻訳が無ければ分割で探す
	if(! ja){
		if(['?','#'].includes(kind)){
			matchesed = dictionary.queryComplexSplitDanbooruTags(content);
			if(!matchesed){ matchesed = []; }
		}
		const jas = matchesed.map( (matched) => {
			if(typeof matched === 'string') return matched; // マッチしなかった場合、文字列が入っている
			const rt = dictionary.queryTryJaFromRelatedTags(matched.related_tags);
			return (rt) ? `${rt}`:`${matched.tag_name}`; 
		});
		ja = `<${kind}:${jas.join('+')}>`
	}
	let elem = document.createElement("span");
	elem.classList.add('dantagja__translated');
	elem.textContent = ja;
	elem.style.fontSize = "70%";
	//console.log('detected', node, elem, ja);
	node.appendChild(elem);
	return true;
};

const translatingNodeRecurse = (dictionary, node) => {
	if (node.nodeType === Node.TEXT_NODE) {
		if (node.parentNode && node.parentNode.nodeName === 'TEXTAREA') {
			return;
		}

		return;
	}

	//if (node.nodeType !== Node.ELEMENT_NODE) {
	//	return;
	//}

	for (let i = 0; i < node.childNodes.length; i++) {
		translatingNodeRecurse(dictionary, node.childNodes[i]);
	}

	// 自分や子供が翻訳済みであればそれを追加翻訳しない
	if(node.classList?.contains('dantagja__translated')){
		return;
	}
	const hasTranslatedClass = Array.from(node.childNodes).some(childNode => childNode.classList?.contains('dantagja__translated'));
	if(hasTranslatedClass){
		return;
	}

	const res = insertJaNodeDanbooruTag(dictionary, node);
	if(res){
		return;
	}
}

// ================

import Dictionary from './dictionary.js';

{
	const dictionary = new Dictionary();

	// Now monitor the DOM for additions and substitute danbooru_tag into new nodes.
	// @see https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver.
	const observer = new MutationObserver((mutations) => {
		mutations.forEach((mutation) => {
			if (mutation.addedNodes && mutation.addedNodes.length > 0) {
				// This DOM change was new nodes being added. Run our substitution
				// algorithm on each newly added node.
				for (let i = 0; i < mutation.addedNodes.length; i++) {
					const newNode = mutation.addedNodes[i];
					translatingNodeRecurse(dictionary, newNode);
				}
			}
		});
	});
	observer.observe(document.body, {
		childList: true,
		subtree: true
	});

	translatingNodeRecurse(dictionary, document.body);
	
	sd_extend_init(dictionary);
}
