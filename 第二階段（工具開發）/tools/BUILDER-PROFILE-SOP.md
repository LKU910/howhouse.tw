# 建商履歷自動建置 SOP

本文件給「排程任務」使用。排程每 30 分鐘觸發一次（00:00–08:30），每次執行完成 **一家** 建商履歷，或整家略過。

---

## 0. 絕對原則

1. **100% 查證**：核心六欄缺一不可。查不到就整家 skipped。
2. **本體業別必須為建設公司**：不收營造廠、代銷公司、投資控股、建材公司等非建設為主業者（詳見步驟 2.5）。
3. **一次只處理一家**：不要貪心、不要批次。
4. **不捏造、不推論**：所有事實必須有可點擊的來源連結寫在 HTML 的 `<a class="src">` 標籤中。
5. **Token 逼近上限時請停手**：把當前建商 status 改回 "pending"（不要卡在 in_progress），立即結束。

---

## 1. 路徑對照

所有路徑以 repo 根目錄（擇居/）為基準。在 bash 中使用當前 session 的掛載路徑前綴（每次 session 不同，請用 `find /sessions -name "CLAUDE.md" -path "*/擇居/*" 2>/dev/null` 定位）。

| 用途 | 路徑 |
| --- | --- |
| 佇列檔 | `第二階段（工具開發）/tools/builder-queue.json` |
| 本 SOP | `第二階段（工具開發）/tools/BUILDER-PROFILE-SOP.md` |
| 建商頁產出目錄 | `第二階段（工具開發）/deploy/` |
| 建商列表頁 | `第二階段（工具開發）/deploy/builders.html` |
| sitemap | `第二階段（工具開發）/deploy/sitemap.xml` |
| 模板參考（完整版） | `第二階段（工具開發）/deploy/builder-huaku.html` |
| 模板參考（有集團子公司寫法） | `第二階段（工具開發）/deploy/builder-baojia.html` |

---

## 2. 執行流程

### 步驟 1 — 讀取佇列並挑選標的

讀 `builder-queue.json`，找第一筆符合以下條件之一：

- `status == "pending"` 且 `attempt_count < _meta.max_attempts_before_skip`
- `status == "in_progress"`（代表上次排程中斷，要接續或重做）

**`status == "paused"` 要跳過**，代表 Kuan 暫時擱置；除非 Kuan 手動改回 pending，不要處理。
**`status == "done"`／`"skipped"`** 當然也跳過。

若找不到，直接回報「佇列已空，無需處理」並結束。

**將該筆改為 `status: "in_progress"`**、`attempt_count` +1、`last_attempt` 填入當前 ISO 時間（請用 bash `date -u +%Y-%m-%dT%H:%M:%SZ`）。**立刻把佇列檔存回**，再繼續下一步。

### 步驟 2 — 核心資料查證（六欄必達）

用 WebSearch + WebFetch（或 MCP 瀏覽器工具）找到下列每一欄，且每欄至少兩個獨立來源交叉比對：

| 欄位 | 建議來源（優先序） |
| --- | --- |
| 公司全名 | 經濟部商業司／台灣公司網 (twincn.com)／證交所公開資訊觀測站 |
| 統一編號 | 台灣公司網／商業司 |
| 成立年份 | 公司登記公告／公司官網 about |
| 實收資本額 | 台灣公司網／最新股東會年報 |
| 公司代表人 | 台灣公司網／最新年報董監事名單 |
| 登記地址 | 台灣公司網／商業司 |

**驗證邏輯**：
- 兩個獨立來源數字／文字一致 → 通過。
- 只有單一來源、或兩個來源打架 → 判定為「無法驗證」。
- 來源過舊（3 年以上）→ 標為 "skipped"，skip_reason 填 "公開資料過舊"。

若任一欄無法驗證：
- 改 `status: "skipped"`，填 `skip_reason`（例：「統編查無（台灣公司網、商業司均無匹配項）」）
- 立即存回佇列，**不要產出 HTML**，結束本次執行。

### 步驟 2.5 — 建商身分核查（重點：曾否推過案）

**唯一判準**：該公司**歷史上曾否以本公司名義推出過任何可賣給消費者的預售屋或成屋建案**。

- ✅ **收**：曾推過（即使只有 1 案、即使是 30 年前、即使現在已不推了）
- ❌ **不收**：從來沒有以本公司名義推出過建案

**典型該排除的身分**（這些通常從未以本公司名義推案）：

- **純營造廠**：只承攬建築工程、不自行掛名推案（例：根基營造、工信工程、大陸工程、中華工程）
- **純代銷公司**：只賣別人的建案、從不自投資建案（例：甲山林廣告、新聯陽）
- **純投資控股公司**：推案都用旗下子公司名義（例：欣陸投控推案用大陸建設名義，本體不算）
- **純建材／水泥／鋼鐵**：只賣建材，從未自己當建商（例：嘉新水泥若從未推案）
- **純其他業別**（汽車代理、食品、保險、電子代工等）：公司成立至今從未有任何建案

**收錄的典型情境**：

- ✅ 建設為主業的公司（絕大多數候選）
- ✅ 建材／預拌混凝土集團但本公司**有推過建案**（例：國產實業推「國產真擁」系列）
- ✅ 代銷公司但**有自投資建案**（例：海悅近年自地自建）
- ✅ 以保險旅宿為主業的集團但**本公司歷史上推過案**（例：龍邦曾推過建案）
- ✅ 曾為電子業但已轉型建設的公司（例：新美齊 2010 轉型後推過多案，即使早年非建商也算）
- ✅ 飯店集團本體只要**歷史上以本公司名義推過 1 案**就收；若本公司完全沒推過但旗下有建設子公司，**改收子公司本體**

**核查方法**（優先序）：
1. 公司官網「建案實績」「作品」「推案紀錄」頁面
2. 公司名義的建案出現在：591 新建案／住展雜誌／ETtoday 房產／蘋果地產／好房網／內政部實價登錄「預售屋資訊」
3. 公司年報／公開說明書中「不動產開發」「建案銷售」收入項目（即使只占 5%）
4. 媒體報導該公司推案（以公司名為主體的新聞稿）

**若 WebSearch／WebFetch 翻遍以上 4 項都找不到任何推案證據**：
- 改 `status: "skipped"`，`skip_reason` 填：「遍查未見本公司名義之建案紀錄（公司官網／591／住展／實價登錄／媒體報導皆無）」
- 結束本次執行

**若找到 1 案以上的推案證據**：
- 繼續後續步驟產出完整版履歷
- 在 HTML 的「基本資料」或「集團規模與市場地位」欄位，如實寫明該公司建設事業的規模（例：「本公司自 1985 年起推過 3 案，現已少有推案」、「建設為集團副業，最近一案為 2018 年」）
- 不美化、不隱藏「建設非主業」的事實

**灰色地帶處理**：
- 同名但不同公司（例：「富邦建設」vs「富邦建設中部」）：以統編為準，不同統編就是不同家，若用戶指定某家就只做該家
- 集團旗下多家建設公司（例：麗寶有多個建設子公司）：以佇列 `name_zh` 對應的那家為準；若查證後發現佇列名稱和實際公司名不符，改 `status: "skipped"`，`skip_reason` 寫明衝突並建議 Kuan 更正候選名稱

### 步驟 3 — 決定 slug

- 優先使用 `slug_hint`
- 若該 slug 已在 `_meta.existing_slugs` 或 `/deploy/` 下有 `builder-{slug}.html` 檔案衝突，改用英文名首單字或新拼音
- slug 規則：全小寫、連字符、僅 a-z 0-9-
- 確定後把 slug 記起來，產出檔名為 `builder-{slug}.html`

### 步驟 4 — 第二層資料查證（可容忍「未查到」）

以下資料如查得到就寫上，查不到就明確標註「未查到公開紀錄」（不影響整家發布）：

1. **股票代號／上市狀態**：公開資訊觀測站（mops.twse.com.tw）
2. **集團關係**：公司官網、維基百科
3. **司法紀錄**：司法院裁判書查詢系統（judgment.judicial.gov.tw）以公司全名關鍵字查。若搜尋結果為 0，HTML 中寫「司法院裁判書查詢系統目前未見以本公司為當事人之公開判決書」
4. **公平會處分**：公平交易委員會決策查詢（ftc.gov.tw/internet/main/decision/）
5. **PTT home-sale 輿情**：`https://www.ptt.cc/bbs/home-sale/search?q={公司名}` 若有 3 年內可引用的實質討論串，選 3-5 則摘要（摘要必須如實反映原文語氣）
6. **Mobile01 房屋板**：`https://www.mobile01.com/search.php?search={公司名}&type=0&category=455`
7. **主要合作營造廠**：從證交所年報、工程公開採購資訊整理
8. **建案數量**：住展雜誌 / 591 新建案 / 公司官網

### 步驟 5 — 產出 HTML

複製 `builder-huaku.html` 為模板（1558 行結構已含完整版所有區塊），逐欄替換內容。**不要更動 <style>、<nav>、<footer>、<script> 區塊**。

關鍵替換點（對應 baojia 參考）：
- `<title>{name_zh} 建商履歷｜擇居</title>`
- meta description / keywords / og / twitter 一起改
- `<link rel="canonical" href="https://howhouse.tw/builder-{slug}.html">`
- `.hero-name` 改公司中文名
- `.hero-en` 改英文名 + 股份類型
- `.hero-tags` 至少 3 個（上市狀態、成立年、區域）
- `.hero-bento` 4 張卡片（統一編號、實收資本額、公司代表人、登記地址），每張都要有來源連結
- `#sec-reg` 基本資料表（公司全名、統編、成立日、股票狀態、資本額、代表人、地址、市場地位），每行最後 `<a class="src">` 連結到來源
- `#sec-legal` 法律相關：若無紀錄就放一個說明卡片，明示「擇居目前未查到以本公司為當事人之公開司法紀錄」；若有紀錄則逐案依 baojia 格式展開（含嚴重度顏色、狀態標籤、外部連結）
- `#sec-sentiment` 網路輿情：若 PTT/Mobile01 查得到實質討論就寫 3-5 張卡片；若無則寫「討論量低，未建立個別輿情摘要」並放搜尋連結讓使用者自查
- `#sec-quality` 品質相關四個子區塊：預售屋履約擔保方式、品質認證、集團規模與市場地位、主要合作營造廠。查不到的子區塊明確標示「未查到公開紀錄」
- 頁尾 `.page-footer`：本頁最後更新：2026 年 4 月（用當前實際月份）

**禁止**：貼假連結（如把搜尋頁連結冒充成原文連結）、捏造推文內容、將「可能」寫成「確定」。

### 步驟 6 — 更新 builders.html 資料陣列

在 `builders.html` 的 `const builders = [` 陣列中 push 新筆，欄位規格比照現有：

```js
{ name: '{name_zh}', en: '{name_en}', file: 'builder-{slug}.html', year: {成立年4位數}, capital: {資本額億數 *10 的整數}, capitalLabel: 'NT$ {X} 億', chairman: '{代表人}', listed: {true|false}, stock: '{代號}', strokes: {首字筆畫數}, scale: {建案數}, approx: {true|false}, tags: ['...', '...', '...'], warn: false }
```

- `capital` 單位是「億 × 10」（例：32.7 億 → 327；5.15 億 → 52）。查現有筆可驗證。
- `strokes` 是中文名**首字**的**繁體筆畫數**（不確定就用 Unicode 名查詢，通用就抓 Unihan）。若不確定可先放 10，加 `// TODO: verify strokes`。
- `scale` 建案數：若為概估請同時設 `approx: true`；若查到精確數字則 `approx: false`。查不到建案數時放 `scale: 0, approx: true, tags: [..., '建案數未查到']` 即可（不致命）。

### 步驟 7 — 更新 sitemap.xml

在 `<!-- 建商個別頁面 -->` 註解之後的 `<url>` 區段末端（或依建商字母順序插入）加一筆：

```xml
  <url>
    <loc>https://howhouse.tw/builder-{slug}.html</loc>
    <lastmod>{YYYY-MM-DD}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
```

### 步驟 8 — 更新佇列

改該筆為：
- `status: "done"`
- `completed_at: {ISO 時間}`
- `completed_slug: "{slug}"`

存回佇列檔。

### 步驟 9 — Git commit（停用）

**不要執行 git commit。** 排程環境的 session 路徑每次不同，且缺少 GitHub push 權限，強行 commit 容易殘留 `.git/index.lock` 導致後續所有 git 操作失敗。

建商頁面的 git commit 與 push 由 Kuan 手動執行，或在互動 session 中由 Claude 協助完成。

### 步驟 10 — 回報

在回應最後用以下格式輸出（便於通知看）：

```
✅ 建商履歷新增完成
建商：{name_zh}（{stock_hint or '未上市'}）
slug：{slug}
核心資料：統編 {no}、資本 {label}、代表人 {name}、成立 {year}
產出：builder-{slug}.html
```

或（略過時）：

```
⏭ 略過：{name_zh}
原因：{skip_reason}
已嘗試次數：{attempt_count}
```

---

## 3. 常見狀況處理

### A. WebSearch 或 WebFetch 被限制、卡住
視為「查證失敗」。將 status 改回 `pending`，**不要** 改為 `skipped`，這樣下次排程再試。若連續 3 次皆失敗（`attempt_count` 達 3），才自動改 `skipped`，`skip_reason: "連續查證失敗（WebSearch/WebFetch 無法取得資料）"`。

### B. Token 用量逼近上限
- 已經在處理的建商：status 改回 `pending`，`attempt_count` **不遞增**（因為這次不是真的失敗）
- 存檔後立即結束，不要產 HTML
- 下次排程（30 分後）會再試

### C. 佇列全部 done/skipped
回報「佇列已空，無需處理」。若要持續擴充，Kuan 會在佇列裡追加候選。

### D. 遇到已經存在的 slug 或 HTML 檔
先查 `deploy/builder-{slug}.html` 是否存在。若存在，改 slug（加後綴如 `-2`），或回報衝突並 `status: "skipped"`，`skip_reason: "slug 衝突：{slug} 已存在"`。

### E. 建商已在 builders.html 陣列中
代表之前做過了。將佇列該筆直接標 `status: "done"`，`completed_slug` 填已存在的 slug，不要重做。

---

## 4. 禁止事項

- ❌ 不要刪除現有建商的頁面
- ❌ 不要改動 _partials/ 或 build 工具鏈
- ❌ 不要觸碰 `第一階段（內容站）/` 任何檔案
- ❌ 不要自行部署（Vercel 透過 GitHub 自動部署；只要 commit 到 main 即可）
- ❌ 不要一次處理多家建商
- ❌ 不要為了湊頁面而寫推測性內容（例：「估計該公司應該⋯」）

---

最後更新：2026-04-21  
負責人：Kuan（審閱）／排程 Claude（執行）
