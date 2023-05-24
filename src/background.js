chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['content_script.js']
  });
});

chrome.tabs.onActivated.addListener(({ tabId }) => {
  chrome.scripting.executeScript({
    target: { tabId },
    files: ['content_script.js']
  });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.active) {
    chrome.scripting.executeScript({
      target: { tabId },
      files: ['content_script.js']
    });
  }
});

// ====
// エラーは解消しないが２個から１個に減る？

chrome.runtime.onInstalled.addListener(() => {
  chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds: [1]
  });
});

chrome.runtime.onStartup.addListener(() => {
  chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds: [1]
  });
});

chrome.runtime.onSuspend.addListener(() => {
  chrome.declarativeNetRequest.updateDynamicRules({
    addRules: [
      {
        id: "1",
        priority: 1,
        action: {
          type: "block"
        },
        condition: {
          urlFilter: {
            schemes: ["chrome"]
          }
        }
      }
    ]
  });
});

chrome.runtime.onSuspendCanceled.addListener(() => {
  chrome.declarativeNetRequest.updateDynamicRules({
    addRules: [
      {
        id: "1",
        priority: 1,
        action: {
          type: "block"
        },
        condition: {
          urlFilter: {
            schemes: ["chrome"]
          }
        }
      }
    ]
  });
});
