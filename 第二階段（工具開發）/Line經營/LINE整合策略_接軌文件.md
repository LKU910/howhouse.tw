# 擇居 LINE 整合策略：從「買房教練」到「冷靜同行者」

> 制定日期：2026-04-14
> 用途：供新 Cowork 頻道接手 LINE 全線調整，無需回溯舊對話即可掌握全貌

---

## 一、現況總覽：兩套系統，一個帳號

目前 LINE 這塊分成兩個時期的產物，共用同一個 LINE Official Account（@howhouse），但定位、語氣、功能完全不同。

### 第一階段產物（已上線，需改造）

| 項目 | 現況 | 位置 |
|------|------|------|
| LINE OA 帳號 | @howhouse，名稱「好宅通」，定位「買房教練」 | LINE OA Manager |
| 歡迎訊息 | 教練語氣，三階段分流（🌱剛開始/🔍正在看/📝快簽約） | 已設定於 OA Manager |
| 關鍵字自動回應 | 12 組，涵蓋財務、看房、斡旋、驗屋等，全部用「好宅通」品牌 + 教練口吻 | 已啟用 |
| Rich Menu | 6 格（買房步驟/財務健檢/看房攻略/實價登錄/成交流程/問教練），標題「買房教練主選單」 | 已啟用，效期至 2027/12/31 |
| 漸進式訊息 | 2 步（Day1 歡迎 + Day3 深度提醒），教練式語氣 | ID: 297816，已啟用 |
| 商業簡介 | 「我們不賣房，只幫你買對」 | 已設定 |

**參考檔案（封存區，唯讀）：**
- `第一階段（內容站）/Line商業帳號/LINE_OA_好宅通_執行藍圖.md` — 完整文案與策略
- `第一階段（內容站）/Line商業帳號/LINE_OA_設定進度與手動步驟.md` — 設定清單
- `第一階段（內容站）/Line商業帳號/LINE_OA_自動回應_完整文案.md` — 12 組回覆全文
- `第一階段（內容站）/Line商業帳號/rich_menu_2500x1686.png` — 現有選單圖片

### 第二階段產物（剛完成，需測試）

| 項目 | 現況 | 位置 |
|------|------|------|
| LINE Login Channel | 「擇居」，Channel ID: 2009797886，Region: Taiwan | LINE Developers Console |
| LIFF App | 「我的買房地圖」，LIFF ID: 2009797886-geRkxqSN，Endpoint: howhouse.tw/progress.html | LINE Developers Console |
| Provider | 「擇居」，ID: 2005059589 | LINE Developers Console |
| LIFF SDK 整合 | v2.24.0 已載入 progress.html，含登入、頭像顯示、Flex Message 分享 | `第二階段/deploy/progress.html` |
| 雙人模式 | 配對碼產生 + Firestore pairCodes collection + 對方進度覆蓋 | `第二階段/deploy/progress.html` |
| Firestore 規則 | users/{userId} + pairCodes/{code}，需登入才能讀寫 | Firebase Console |

---

## 二、核心矛盾：品牌已轉型，LINE 還停在舊世界

網站正在從「好宅通 / 買房教練」全面轉為「擇居 / 冷靜同行者」（詳見 `第二階段/執行策略/品牌轉換與網站改版_執行規劃.md`），但 LINE OA 的所有觸點——名稱、歡迎語、自動回覆、Rich Menu、漸進式訊息——全部還是舊品牌、舊語氣。

同時，第二階段新建的 LINE Login Channel 和 LIFF App 已經用「擇居」命名，形成一個割裂的狀態：使用者在 LINE 裡看到「好宅通 / 買房教練」，點進 LIFF 網頁卻是擇居的介面。

**這份文件的目標：讓接手的頻道知道要做什麼、怎麼做、按什麼順序。**

---

## 三、需要做的事（分四個層次）

### Layer 1：品牌對齊（OA 基本面）

把 LINE OA 從「好宅通 / 買房教練」切換為「擇居」品牌，語氣從教練式改為同行者式。

**3-1. 帳號基本資料**

| 欄位 | 現值 | 改為 |
|------|------|------|
| 顯示名稱 | 好宅通 | 擇居 |
| 狀態消息 | 我們不賣房，只幫你買對 | 先擇，後居 |
| 簡介 | …好宅通是台灣第一個「買方立場」的買房指導平台… | 重寫，擇居語氣（見下方文案指引） |
| 帳號 ID | @howhouse | 不變（SEO 資產） |

**3-2. 歡迎訊息重寫**

現有歡迎訊息用「嗨！歡迎來到好宅通🏠 我是你的買房教練」開場，搭配三階段選擇卡片。

擇居版本方向：
- 不用驚嘆號、不自稱教練
- 不急著分流，先讓人安定下來
- 語氣範例：「買房是一連串的選擇。不急，慢慢來。」
- 三階段卡片可保留結構，但按鈕文案從「🌱 剛開始想買房」改為更安靜的措辭
- 階段回覆內文全面改寫（移除「很好！」「我懂！」等教練語氣）

**3-3. 關鍵字自動回應（12 組）全面改寫**

這是工作量最大的部分。12 組回覆的事實內容可保留，但每一則都要：
1. 將「好宅通」替換為「擇居」
2. 移除教練語氣詞（「💪」「馬上」「教你」「攻略」）
3. 連結 URL 從 homerun-taiwan.com 改為 howhouse.tw
4. 結尾引導語改為擇居風格（「值得想清楚」取代「輸入 XXX 馬上開始」）
5. 加入工具入口（適當的回覆末尾加「我的買房地圖」或「我的決策性格」連結）

**具體改寫範例：**

| 原文 | 擇居版本 |
|------|---------|
| 「買房最怕的不是房價高，是不知道自己不知道什麼。」 | 「買房最難的不是找到好房子，是想清楚自己要什麼。」 |
| 「輸入「財務健檢」馬上開始第一步！」 | 「如果還沒算過，可以先從這裡開始 → howhouse.tw/calculator」 |
| 「我在這裡陪你，不用急，慢慢來 💪」 | 「不急，一步一步來。」 |
| 「好宅通目前是 AI + 人工混合回覆」 | 「擇居目前以 AI 回覆為主，個別問題會盡快處理。」 |

完整 12 組文案的原文在：`第一階段/Line商業帳號/LINE_OA_自動回應_完整文案.md`

**3-4. Rich Menu 重新設計**

現有 6 格設計反映的是「教練選單」邏輯（買房步驟/財務健檢/看房攻略/實價登錄/成交流程/問教練）。擇居版本應該以三大工具為核心重新規劃：

建議新版 Rich Menu 結構（2×3 六格）：

| 位置 | 內容 | 動作 |
|------|------|------|
| 左上 | 🧭 我的決策性格 | URI → howhouse.tw/quiz.html |
| 中上 | 📍 我的買房地圖 | URI → howhouse.tw/progress.html（LIFF URL） |
| 右上 | 💰 我的財務診斷 | URI → howhouse.tw/calculator.html |
| 左下 | 📖 買房 18 步 | 訊息 → 觸發「買房步驟」自動回應 |
| 中下 | 🏗️ 建商履歷 | URI → howhouse.tw/builders.html |
| 右下 | 💬 有疑問 | 訊息 → 觸發「問擇居」自動回應 |

視覺風格：延續擇居色彩系統——米白底 #FAFAFA、銅色 #B8956A accent、Noto 字體、不花俏。

**3-5. 漸進式訊息調整**

現有 2 步（Day1 + Day3）需要：
- 品牌名替換
- 語氣改寫
- 加入工具引導（Day1 提及「我的決策性格」，Day3 提及「我的買房地圖」）
- 考慮擴充到 5-7 步（原藍圖規劃了 10 步，可先做前半段）

---

### Layer 2：工具串接（讓 LINE 成為工具的入口）

第二階段的三個工具需要 LINE 作為流量入口和回訪機制。

**3-6. LIFF 入口整合**

已完成的 LIFF App「我的買房地圖」(ID: 2009797886-geRkxqSN) 需要：

| 待辦 | 說明 |
|------|------|
| 實測 LIFF 登入流程 | 從 LINE 內開啟 howhouse.tw/progress.html → 自動觸發 LIFF init → 登入 → 顯示頭像 |
| 測試分享功能 | 📤 按鈕 → shareTargetPicker → Flex Message 是否正確顯示 |
| 測試雙人模式 | 兩支手機各自登入 → 產生配對碼 → 互相輸入 → 確認看到對方進度 |
| Rich Menu 連結 | 「我的買房地圖」格子的 URI 應該用 LIFF URL（line://app/2009797886-geRkxqSN）而非直接網址，這樣在 LINE 內開啟時會自動帶入 LINE 身分 |

未來「我的決策性格」和「我的財務診斷」也需要各自的 LIFF App（或共用同一個 LIFF，用 path 區分），讓 LINE 內開啟時自動識別身分。

**3-7. 新建 LIFF App（視開發進度）**

| 工具 | LIFF App 名稱 | Endpoint |
|------|---------------|----------|
| 我的決策性格 | 我的決策性格 | howhouse.tw/quiz.html |
| 我的財務診斷 | 我的財務診斷 | howhouse.tw/calculator.html |

在 LINE Developers Console → Provider「擇居」→ Channel「擇居」(2009797886) → LIFF 頁面新增。

---

### Layer 3：推播與回訪（Messaging API）

這是尚未啟動的部分，需要新建一個 Messaging API Channel。

**3-8. 建立 Messaging API Channel**

在 LINE Developers Console → Provider「擇居」下新建：
- Channel type: Messaging API
- Channel name: 擇居
- Description: 買房決策陪伴系統
- Category: 不動產
- 注意：Messaging API Channel 和 LINE Login Channel 是不同的東西，兩者共存於同一個 Provider 下

**⚠️ 重要：** LINE OA (@howhouse) 需要與 Messaging API Channel 連結（Link）。這在 LINE Developers Console 的 Messaging API Channel 設定頁面操作。連結後，OA 的推播就可以透過 API 程式化控制。

**3-9. 決策回顧推播**

這是「走到哪了」第三層功能的核心——定期提醒使用者回來看看自己的決策進度。

設計邏輯：
- 觸發條件：使用者超過 N 天沒有更新任何步驟狀態
- 推播內容：不是「你還沒完成喔！」的催促，而是「上次你在想 {步驟名稱}，現在想法有變嗎？」
- 頻率：最多每週一次，不騷擾
- 技術：需要 server-side 排程（Cloud Functions / Netlify Functions），用 Messaging API push message 發送
- 使用者 LINE userId 已儲存在 Firestore user document 的 lineProfile 欄位

推播訊息語氣範例：
```
上次你停在「第 7 步：格局動線怎麼看」。

看房是一件越看越有感覺的事。
如果最近有新的想法，可以回來記一下。

→ 看看你的買房地圖
```

**3-10. 雙人模式 LINE 通知**

現有雙人模式用 Firestore 做即時同步，但目前沒有通知機制——對方更新狀態時，你不會收到提醒。

可加入的推播：
- 對方將某步驟標記為「想清楚了」時，推送 Flex Message：「你的另一半在 {步驟名} 做了決定。要不要看看？」
- 技術：Firestore trigger (Cloud Functions) → Messaging API push
- 注意隱私：只推送「有更新」，不透露具體筆記內容

---

### Layer 4：進階整合（中長期）

**3-11. LINE 內嵌問答**

目前「問教練」回覆是預設文字。中長期可以接入 AI 回覆（透過 Messaging API webhook + GPT/Claude API），讓使用者在 LINE 內直接問買房問題，回覆帶擇居語氣。

**3-12. 人格結果 LINE 分享**

「我的決策性格」完成後的人格結果頁，需要 LINE 分享功能：
- Flex Message 呈現人格名稱 + 四維度圖表
- 分享連結帶個人結果參數，收到的人可以直接做測驗

**3-13. 進度圖片生成**

「我的買房地圖」的進度可以生成一張圖片（7 階段 × 3 狀態的視覺化），用 liff.shareTargetPicker 或直接在 Messaging API 推播中附帶，作為社群分享素材。

---

## 四、LINE Developers Console 帳號結構

```
Provider: 擇居 (ID: 2005059589)
├── LINE Login Channel: 擇居 (ID: 2009797886)
│   └── LIFF App: 我的買房地圖 (ID: 2009797886-geRkxqSN)
│   └── [待建] LIFF App: 我的決策性格
│   └── [待建] LIFF App: 我的財務診斷
│
└── [待建] Messaging API Channel: 擇居
    └── → 連結至 LINE OA @howhouse

LINE Official Account: @howhouse
├── 歡迎訊息 → 需改寫
├── 自動回應 12 組 → 需改寫
├── Rich Menu → 需重新設計
└── 漸進式訊息 → 需改寫
```

---

## 五、Firebase 相關

| 資源 | 用途 | 狀態 |
|------|------|------|
| Firestore: users/{uid} | 使用者進度 + LINE profile + 筆記 | 已上線 |
| Firestore: pairCodes/{code} | 雙人模式配對碼 → UID 對應 | 已上線 |
| Firestore Rules | 需登入才能讀寫自己的 user doc；pairCodes 需登入即可讀寫 | 已發布 |
| [待建] Cloud Functions | 推播排程、Firestore trigger → Messaging API | 未建立 |

---

## 六、建議執行順序

### Phase A：測試現有功能（先確認第二階段的東西能動）
1. 在手機 LINE 中開啟 howhouse.tw/progress.html
2. 測試 LIFF 登入 → 頭像顯示
3. 測試「📤 分享」→ Flex Message
4. 測試「👫 雙人」→ 配對碼 → 雙人同步
5. 記錄任何 bug
6. 確認「我的買房地圖」LIFF App 正常運作

### Phase B：OA 品牌切換（影響所有現有好友）
1. 更新帳號名稱、狀態消息、簡介
2. 重寫歡迎訊息
3. 逐一改寫 12 組自動回應
4. 設計新版 Rich Menu 圖片並上傳
5. 調整漸進式訊息

### Phase C：Messaging API 建立
1. 在 LINE Developers Console 建立 Messaging API Channel
2. 連結至 @howhouse OA
3. 設定 webhook URL（指向 Cloud Functions 或 Netlify Functions）
4. 實作決策回顧推播邏輯
5. 實作雙人模式通知

### Phase D：工具入口優化
1. 新建 LIFF App（我的決策性格、我的財務診斷）
2. Rich Menu 連結改為 LIFF URL
3. 自動回應末尾加入工具入口連結

---

## 七、語氣轉換速查

在改寫任何 LINE 文案時，參照這張表：

| 不要用 | 改用 |
|--------|------|
| 好宅通 | 擇居 |
| 買房教練、教練 | （不自稱，或用「擇居」） |
| 必看、攻略、懶人包 | 值得了解、可以參考 |
| 馬上開始、立即查看 | 可以先從這裡開始 |
| 💪、🎉、！！ | 不用 emoji 強調，句號結尾 |
| 「很好！」「我懂！」 | 省略，直接進入內容 |
| 「教你」「告訴你」 | 「整理了」「這裡有」 |
| homerun-taiwan.com | howhouse.tw |
| 「問教練」 | 「有疑問」 |
| 「陪你走完每一步」 | 「陪你想清楚每個決定」 |

---

## 八、需要 Kuan 參與的環節

| 項目 | 原因 |
|------|------|
| Messaging API Channel 建立 | 需要在 LINE Developers Console 操作，可能需要 Kuan 登入授權 |
| OA 名稱修改為「擇居」 | LINE OA Manager 操作，需管理員權限 |
| Rich Menu 圖片設計方向確認 | 6 格內容是否採用建議方案 |
| 推播頻率與語氣確認 | 決策回顧推播的節奏需要 Kuan 定調 |
| Cloud Functions 費用 | Firebase Blaze plan 需確認是否已升級 |

---

*擇居 LINE 整合策略 v1.0 — 2026.04.14*
