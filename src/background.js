'use strict';

const insertContentScript = (tab) => {
	const tabUrl = tab.url;
	if(! tabUrl){return;}
	if (tabUrl.startsWith('http://') || tabUrl.startsWith('https://') || tabUrl.startsWith('file://')) {
		chrome.scripting.executeScript({
				target: { tabId: tab.id },
				files: ['content_script.js']
		});
	};
}

chrome.action.onClicked.addListener((tab) => {
	insertContentScript(tab);
});

chrome.tabs.onActivated.addListener(({ tabId }) => {
	chrome.tabs.onActivated.addListener(({ tabId }) => {
		chrome.webNavigation.getFrame({ tabId, frameId: 0 }, (details) => {
			if (details && details.errorOccurred) {
				console.log('Error page is displayed');
				// エラーページの表示が検出された場合の処理をここに追加する
			} else {

				chrome.tabs.get(tabId, (tab) => {
					if(!tab){console.warn('aa');}
					insertContentScript(tab);
				});
			
			}
		});
	});
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
	if (changeInfo.status === 'complete' && tab.active) {
		// エラーページでないことを確認する
		chrome.scripting.executeScript({
			target: { tabId: tabId },
			function: () => {
				return document.documentURI !== "about:blank";
			}
		}).then((result) => {
		if (result[0]) {
			// エラーページでない場合の処理をここに追加する
			insertContentScript(tab);
		}
		}).catch((error) => {
			// "Error: Frame with ID 0 is showing error page"
			// "Error: Cannot access a chrome:// URL"
			console.log(error);
		});
	}
});
