---
title: "AD 域滲透：DNS Spoofing 攻擊鏈深度分析"
date: "2026-04-07"
excerpt: "從 Kerberos「驗證」與「授權」之間的落差切入，帶你看懂 DNS Spoofing 如何在 AD 環境中被串成一條完整攻擊鏈，以及該如何偵測與防禦。"
tags: ["Active Directory", "DNS Spoofing", "Kerberos", "AD Security", "GSSAPI", "Cybersecurity"]
readTime: "14 min read"
slug: "ad-dns-spoofing-attack-chain-analysis"
---

## 前言：為什麼這條鏈值得被重視

在 Active Directory（AD）環境中，Kerberos 認證通常被視為一種可靠的身份保證機制。

然而，認證成功並不代表系統對該身份的解讀一定正確。

當身份在不同系統之間被解析、映射與授權時，只要缺乏一致的對應關係，就可能產生語意落差；而這種落差在特定條件下，會被放大為可利用的攻擊面。


本文關注的並不是單一漏洞，而是一條由多個正常機制所組成的攻擊路徑：

**DNS Spoofing → Kerberos 認證導向 → 授權映射偏移 → 身份被誤認**

這條鏈的關鍵在於每個環節本身都沒有異常。
但認證流程可以完全成立，系統元件也各自正常運作，而最終的身份判斷卻發生偏差。
問題不在單一漏洞，而在於不同系統對同一身份的解讀並不一致。

---

## 核心觀念：Kerberos 負責「你是誰」，不是「你能做什麼」

很多防守方會下意識把 Kerberos 當成「完整的身份保證」，  
但這其實是一個很常見的誤解。

Kerberos 真正在做的事情，其實很單純：

- Authentication（認證）→ 確認你是不是你
- Authorization（授權）→ 不決定你能做什麼

也就是說：
Kerberos 只證明「這個身份是真的」，但不保證「這個身份該不該做這件事」。

這直接導致一個關鍵結果：

即使整個認證流程顯示正常，後面的授權階段仍會失真。

例如：

- 身份被錯誤映射（mapping 錯）
- 名稱解析被污染或出現歧義（例如 DNS 問題）
- 服務端只用「名稱」而不是完整身份資訊做授權判斷

結果你是對的人，系統卻把你當成另一個人。


---

## DNS 為什麼是入口：Kerberos 極度依賴名稱服務

在 Kerberos 的流程中，它本身不負責記住服務位置，而是會先去查 DNS。

也就是說，Kerberos 會根據 DNS 的結果，決定「要跟誰溝通」。

這個依賴主要發生在兩個地方：

1. 查 `_kerberos._tcp.domain.com` 來找到 KDC
2. 將像 `cifs/server.domain.com` 這類 SPN 解析成實際主機

一旦 DNS 結果被操控，Kerberos 將被導向錯誤的目標。

攻擊者不需要破解 Kerberos，本質上只是改變請求的流向，使其落在非預期的服務上。

在這種情況下，認證流程表面上仍然成立，但實際的信任對象已經發生偏移。

這正是 DNS 能成為攻擊入口的原因：它決定了「你在跟誰建立信任」。


---

## Windows 與 Linux 的差異：同樣 Kerberos，不同安全語意

乍看之下，Windows 與 Linux 都在使用 Kerberos，  
但在「認證之後怎麼做授權」這件事上，兩者的安全模型其實差很多。

### Windows（LSASS / SSPI / Kerberos）

在 Windows 生態中，Kerberos 會搭配 PAC（Privilege Attribute Certificate）使用。  
PAC 裡面常見包含：

- SID
- 群組資訊
- Domain 屬性

關鍵點在於：

**Windows 的授權決策基於 PAC，而不是單純名稱。**

實務上常見是：

- 沒有有效 PAC -> 登入失敗，或只能拿到受限權限
- 有 PAC -> 依照 SID / 群組做較精確的授權

這代表只靠名稱字串去偽造身份，在 Windows 環境中的難度更高。


### Linux / Unix（MIT Kerberos 或 Heimdal + GSSAPI）

在 Linux / Unix 環境中，Kerberos 透過 GSSAPI 提供給應用程式使用。  
MIT/Heimdal 在 AD 場景可支援 PAC，但是否拿 PAC 做授權，取決於應用層實作。

常見流程是：

Kerberos 驗證成功 -> 取得 Client Name（`cname`）-> 應用自行做授權（LDAP / 本地 ACL / mapping）

風險點在於：

- `cname` 會進入應用的 mapping 邏輯，而 mapping 不是唯一且可被混淆
- 應用只把 `cname` 當名稱字串，沒有對應到唯一識別（如 SID / `objectGUID`）
- 沒有驗證「名稱 -> 實際帳號」之間的強一致性

真正問題不是「Linux 沒有 PAC」，而是 **應用層沒有強制使用 PAC / 唯一識別來做授權。**

結論：**認證成功不必然等於身份可信。**


---

## 攻擊基礎：Kerberos Principal 與名稱解析

攻擊的起點，在於 Kerberos 對「名稱」的處理，並不是單純的字串比對，而是一個可被解析與轉換的結構。

在 Kerberos 中，我們日常看到的帳號是：

`username@REALM`

它很直覺，像是一個「唯一身份」。  
在協定內部，事情沒有這麼簡單。

Kerberos 在處理身份時，使用的是 Principal 結構。  
而 Principal 並不是單純一段字串，而是 ASN.1 定義的資料格式，裡面會拆成：

- `name-type`（名稱類型）
- `name-string`（名稱本身）

也就是說，系統在判斷「你是誰」時，不只是看字串，  
還會看「這個名字被當成什麼類型來解讀」。

這就帶出一個關鍵問題：  
同一個看起來一樣的名稱，在不同情境下會代表不同身份。

例如：

- 在某個流程裡，它會被當成「使用者」
- 在另一個流程裡，它會被當成「服務」或「電腦帳號」

而這個差異，不會直接顯示在你看到的 `username@REALM` 上。

為什麼這很重要？  
因為一旦「名稱」和「實際身份」之間不是一對一關係，中間就會出現解讀空間。

而攻擊的本質，就是利用這個空間。

換句話說，Kerberos 表面上用名稱識別身份，實際上依賴的是更複雜的結構；只要不同系統或流程對這套結構解讀不一致，名稱歧義就會出現，而這正是攻擊能切入的地方。


---

### AD 名稱查詢歧義：`samAccountName`  VS  `userPrincipalName`

在 Active Directory 裡，查一個帳號其實不只一種方式，最常見的是這兩個：

- `samAccountName`：傳統帳號名稱（NetBIOS 相容）
- `userPrincipalName`：類似 email 的登入識別（Kerberos / 現代登入）

這兩者在語意與用途上並不完全等價，且在實務環境中不一定一致。
為了維持相容性，系統在查詢失敗時，可能會進行名稱補償（fallback），例如：

- 查詢失敗時，自動附加 `$` 再嘗試解析

這就會出現一種很微妙的情況：

- `USER` -> 一般使用者帳號
- `USER$` -> 電腦帳號

在部分查詢或授權流程中，這兩者可能被視為「相關甚至可替代」的識別。

此時，名稱已不再對應唯一身份，而是進入可被解讀的空間。

這種「名稱相似但身份不同」的模糊地帶，已在實務中被具體化為漏洞，例如：

- [CVE-2021-42278](https://support.microsoft.com/zh-tw/topic/kb5008102-active-directory-security-accounts-manager-%E5%BC%B7%E5%8C%96%E8%AE%8A%E6%9B%B4-cve-2021-42278-5975b463-4c95-45e1-831a-d120004e258e)
- [CVE-2021-42287](https://support.microsoft.com/zh-tw/topic/kb5008380-%E9%A9%97%E8%AD%89%E6%9B%B4%E6%96%B0-cve-2021-42287-9dafac11-e0d0-4cb8-959a-143bd0201041)

然而，這些漏洞並非根本原因。

真正的問題在於：系統無法保證「名稱 → 身份」之間的強一致對應。

當名稱與實際身份之間不是一對一關係時，查詢、解析與授權之間就會產生語意落差，而這正是攻擊得以成立的條件。

**結論：只要名稱與身份無法嚴格綁定，混淆就能被武器化。**


---

## 完整攻擊鏈（Kill Chain）拆解

###  Step 1：MITM foothold（取得中間人位置）

**ATT&CK：**

- T1557 → Adversary-in-the-Middle
- T1557.002 → ARP Cache Poisoning
- T1557.003 → DHCP Spoofing

**常見手法（概念）：**

- **L2/L3 轉送劫持**：讓受害者的預設閘道/名稱解析流量經過攻擊者
- **IPv6 路徑注入**：利用雙棧環境讓流量走到非預期的解析/代理

**常見工具（僅列名）：**

- ARP / L2：`bettercap`、`ettercap`（或同類型工具）
- DHCP：`yersinia`（或同類型工具）
- IPv6 MITM：`mitm6`（或同類型工具）

**防守觀測重點：**

- **交換器/端點**：ARP 表異常變動、同一 IP 對應 MAC 突變
- **網路基線**：不該出現的 DHCP Server、RA（Router Advertisement）來源


###  Step 2：DNS Spoofing（污染名稱解析）

**ATT&CK：**

- T1557（延伸 MITM）
- T1557.001 → Data Manipulation: Stored Data（可用來描述「污染解析結果/快取」的效果）

**目標解析點（概念）：**

- `_kerberos._tcp.<domain>`（KDC SRV）
- 服務主機名（例如 `cifs/<host>` 這類 SPN 對應的主機解析）

**常見工具（僅列名）：**

- DNS spoof / proxy：`bettercap`、`dnsspoof`（或同類型工具）
- 名稱解析/認證誘導整合：`Responder`（或同類型工具）

**防守觀測重點：**

- **DNS 事件**：SRV 回覆異常（KDC 指到非 DC）、TTL 不合理、同名不同答案頻繁切換
- **網段隔離**：客戶端是否被允許向「非公司 DNS」查詢（Rogue DNS）


###  Step 3：Credential Interception / Coercion（攔截或強制觸發認證）

**ATT&CK：**

- T1557 → Adversary-in-the-Middle
- T1187 → Forced Authentication
- T1550 → Use of Alternate Authentication Material（視後續是否利用替代材料而定）

**常見行為（概念）：**

- 讓受害者對「假服務」送出 Kerberos/NTLM 驗證
- 在 Kerberos 失敗時觸發協定降級或替代路徑（取決於客戶端與服務設定）

**常見工具（僅列名）：**

- 認證攔截：`Responder`
- Relay / 協議轉送：`impacket` 套件中的相關工具（例如 NTLM relay 家族）
- 強制認證家族：`PetitPotam`（或同類型 coercion 技術）

**防守觀測重點：**

- **網域/端點**：突發的大量驗證請求、同一端點對多服務的短時間認證嘗試
- **封包面**：針對 88/TCP/UDP（Kerberos）與 53（DNS）做關聯（時間窗內 DNS 異常 -> Kerberos/NTLM 異常）


###  Step 4：授權層濫用（Name-based trust flaw）

**ATT&CK：**

- T1078 → Valid Accounts（若最終以「看似合法帳號」取得存取）
- T1550 → Use of Alternate Authentication Material（若使用替代材料完成存取）

**核心問題（重點）：**

在部分 Linux / Unix 的服務授權流程中，只用 `cname`（字串）做身份映射，卻沒有做強一致性驗證，例如：

- 不核對 PAC / SID（或等價的強身份屬性）
- 不將「Kerberos principal」與「目錄中的唯一識別（objectSID / objectGUID）」綁定
- 應用端授權決策只依賴「同名字串」查到的 LDAP 物件

**輔助驗證與盤點（偏防守/稽核）：**

- LDAP 枚舉/盤點（用於確認目錄中的命名與屬性分佈）
- Kerberos 票據行為觀察（用於比對 principal 與服務端授權結果是否一致）


###  Step 5：名稱歧義（Name Confusion / Masquerading）

**ATT&CK：**

- T1036 → Masquerading
- T1036.005 → Match Legitimate Name or Location

**常見混淆點（概念）：**

- `admin` vs `admin$`（使用者/電腦帳號）
- `samAccountName` 與 `userPrincipalName` 的查詢優先順序差異
- 服務主機名 / SPN 對應的非預期解析（導致授權查詢落在錯物件）

**防守觀測重點：**

- **命名治理**：避免可混淆命名（尤其是 `$` 邊界）
- **服務端日誌**：同一 principal 在短時間內對應到不同目錄物件（或不同 SID）的異常


###  Step 6：橫向移動 / 權限濫用

**ATT&CK：**

- T1021 → Remote Services
- T1021.002 → SMB
- T1021.006 → WinRM
- T1047 → WMI
- T1087 → Account Discovery

**常見目標（概念）：**

- 檔案服務（SMB/CIFS）、遠端管理（WinRM/WMI/SSH）、目錄查詢（LDAP）

**防守觀測重點：**

- **橫移基線**：非典型工作站對伺服器的管理通道連線突增
- **帳號行為**：同一帳號在多主機上的短時間登入爆量、異常服務存取路徑


### 快速總覽：攻擊鏈與防守觀測對照

| Step | 攻擊目的 | 代表性 ATT&CK | 防守方關鍵觀測訊號 |
|------|----------|----------------|----------------------|
| 1 | 取得可影響流量導向的位置（MITM） | T1557 | ARP/MAC 對應異常、Rogue DHCP 或 IPv6 RA |
| 2 | 污染名稱解析，將 KDC / 服務導向錯誤目標 | T1557.001 | `_kerberos._tcp` SRV 異常、KDC 指向非 DC、DNS 回應頻繁變動 |
| 3 | 誘導或強制受害者送出認證 | T1187、T1550 | 短時間大量認證請求、DNS 異常後緊接 Kerberos / NTLM 行為 |
| 4 | 利用名稱導向的授權邏輯造成錯誤映射 | T1078（情境式） | principal 與實際授權物件不一致（SID/UID 差異、同名不同實體） |
| 5 | 觸發名稱混淆（例如 `$` 邊界） | T1036 | `name` / `name$` 查詢或授權異常、命名策略缺口 |
| 6 | 擴展初始存取為橫向移動能力 | T1021 | SMB / WinRM / WMI / SSH 使用量突增、跨主機登入異常 |

---

## 什麼環境下最容易成立

這條攻擊鏈並非依賴單一條件，而是多個因素交互作用的結果。  
其中部分條件屬於必要前提，部分則會顯著提高成功率。

### 關鍵前提（缺一則難以成立）

- 攻擊者可影響名稱解析或流量導向（如 MITM 或 DNS 操控）  
- 目標環境存在依賴 Kerberos 認證的服務  

### 成功率放大因素

- 服務端授權依賴名稱 mapping（例如以 `cname` 對應帳號），且未綁定唯一識別（SID / objectGUID）  
- DNS 缺乏完整保護（如未部署 DNSSEC、缺乏異常監控或允許 Rogue DNS）  
- 網段允許未受限制的名稱解析或流量重導（ARP / DHCP / IPv6 等）


當上述條件同時存在時，攻擊者即可在不破壞認證流程的情況下，影響最終的身份解讀與授權結果。

前提越完整，攻擊越穩定；即使僅部分成立，仍有機會發動，但需要更精確的時機與控制能力。

---
## 一個實戰情境：名稱映射導致的授權錯位

假設某內網存在一個以 Active Directory 作為身份來源的 Linux 檔案服務，其登入與授權流程如下：

- 接收 Kerberos 驗證成功結果  
- 取得 client principal（`cname`）  
- 以名稱字串向 LDAP 查詢對應帳號  
- 根據查詢結果套用檔案存取權限（ACL）  

在此模型中，授權決策依賴的是「名稱 → 帳號」的映射，而非與唯一識別（如 SID / objectGUID）的強綁定。


若名稱解析流程可被影響（例如透過 DNS Spoofing），使驗證或查詢路徑偏離原始預期，則可能產生以下情況：

- 應用端取得的 `cname` 在語法上仍然合法  
- 該名稱在後續查詢中被解析為不同的目錄物件  
- 授權所依據的帳號，與原始驗證主體不一致  


在整個過程中：

- Kerberos 認證本身未失敗  
- 票據與憑證皆為有效  
- 系統元件依既有邏輯運作  

但身份在授權階段發生偏移，導致 ACL 判斷錯誤。

這種情境的本質在於：當名稱被用作身份代理，但缺乏與實際身份的強一致綁定時，授權結果將取決於解析結果，而非原始認證主體。

---

## 防守觀點：你該監控哪些異常訊號

可優先建立以下偵測面向：

- DNS 層：異常 SRV 回覆、短時間大量 `_kerberos._tcp` 查詢偏移
- AD 層：帳號查詢命中模式異常（`name` / `name$` 快速切換）
- 服務層：同一連線中 principal 與最終授權物件不一致
- 網路層：ARP 表頻繁變動、可疑 DHCP / IPv6 鄰居行為

如果你在 SOC，先從「DNS -> 認證 -> 授權結果」三段關聯規則開始做。


---

## 防禦清單

### DNS 防護

- 對關鍵區段啟用 DNSSEC（至少先從核心 AD 區開始）
- 阻擋未授權 DNS 回應來源（Rogue DNS）
- 針對 Kerberos 相關 SRV 查詢做基線與告警

### Kerberos 與服務端授權

- 服務端授權不要只信任 `cname` 字串
- 核對 PAC / SID 或唯一目錄識別
- 拒絕無法完成強身份綁定的 token / ticket
- 強制要求 PAC 驗證（Windows 端已於 [KB5008380](https://support.microsoft.com/zh-tw/topic/kb5008380-%E9%A9%97%E8%AD%89%E6%9B%B4%E6%96%B0-cve-2021-42287-9dafac11-e0d0-4cb8-959a-143bd0201041) 修補；對應 CVE-2021-42278）
- 應用層使用 SSSD 並啟用 `krb5_store_password_if_offline` 或 PAC 相關選項
- 監控 Kerberos KDC 相關新 Event ID（KB5008380 之後新增的稽核事件）

### AD 身份與命名治理

- 避免可混淆命名（尤其是 `USER` / `USER$` 類型）
- 盤點舊系統相容行為與名稱解析 fallback 邏輯
- 套用既有安全更新並定期稽核

### 網路層

- 啟用 ARP 防護與交換器安全機制（如動態 ARP 檢查）
- 重要伺服器區域做 VLAN 隔離
- 佈署 IDS / IPS 觀測 MITM 前兆


---

## 這條鏈的本質：不是 bug，而是邊界設計錯位

這條攻擊鏈的本質，其實不是單一漏洞，而是邊界設計上的錯位。

問題也不在 Kerberos 是否安全，而是在於認證結果被不同系統解讀的方式並不一致。

當一個已通過驗證的身份，跨越不同平台、服務，甚至目錄查詢邏輯時，如果缺乏強一致性的授權綁定（例如：名稱、Principal、實際對象之間的嚴格對應），系統之間就會出現語意落差。

而攻擊，正是發生在這個落差之中。


---

## 結語
在 Active Directory 的攻擊場景中，DNS Spoofing 的價值不在於直接突破防護，而在於它以相對低噪音的方式重塑整條信任路徑。

當名稱解析被控制後，後續的影響其實是連鎖的：


**名稱解析被控制 -> 認證流程被引導 -> 授權判斷出現落差 -> 最終導致身份被錯誤解讀，甚至被偽造與橫向利用**


這整個過程不像傳統漏洞利用那樣「明顯」，但影響更深，因為它發生在系統之間的邊界。

