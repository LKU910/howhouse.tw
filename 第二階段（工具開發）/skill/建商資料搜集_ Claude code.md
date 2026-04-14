# 好宅通建商輿情蒐集指引（Claude Code 專用）

> **執行環境**：Claude Code（本地終端機，需要完整網路存取）
> **目的**：為建商履歷頁面的「網路輿情」區塊蒐集可驗證的討論內容
> **產出**：直連 URL + archive.org 存檔 URL + 精確摘要 HTML

---

## 為什麼需要這份指引

好宅通的建商頁面有「網路輿情」區塊，摘要公開討論平台上對建商的評價。
過去的做法是連結到搜尋頁面，讀者點進去找不到對應內容，嚴重傷害信任。

新標準：**每一則摘要都必須直連到具體貼文，且有 archive.org 備份**。

---

## 執行流程

### 輸入

你會收到一個建商名稱和對應的 `builder-{slug}.html` 檔案路徑。

### Step 1：搜尋論壇貼文

依序搜尋以下平台，找包含建商名稱的討論：

```bash
# PTT home-sale 板
curl -s "https://www.ptt.cc/bbs/home-sale/search?q={建商名稱URL編碼}" \
  -H "Cookie: over18=1" | # PTT 需要 over18 cookie

# Mobile01 房屋板
curl -s "https://www.mobile01.com/search.php?search={建商名稱URL編碼}&type=0&category=455"

# Dcard 房屋板
curl -s "https://www.dcard.tw/search?query={建商名稱URL編碼}&forum=house"
```

### Step 2：篩選有價值的貼文

從搜尋結果中提取個別貼文 URL，逐篇讀取內容。篩選標準：

- **PTT**：≥10 推文，或 ≥5 個不同 ID 的實質回覆
- **Mobile01**：≥2 頁回覆，或 ≥10 則回覆
- **Dcard**：≥10 則回覆

排除：
- 純廣告文（代銷業配）
- 買賣文（只是掛售，沒有討論）
- 與建商品質/評價無關的貼文

### Step 3：讀取貼文內容並撰寫摘要

對每篇入選貼文：

```bash
# PTT 範例
curl -s "https://www.ptt.cc/bbs/home-sale/M.XXXXXXXXXX.A.XXX.html" \
  -H "Cookie: over18=1"

# Mobile01 範例
curl -s "https://www.mobile01.com/topicdetail.php?f=456&t=XXXXXXX"
```

讀取 HTML 後：
1. 解析原文標題、發文日期、內文
2. 解析推文/回覆
3. 判斷整體討論方向（正面/負面/中性/混合）
4. 撰寫 1-2 句摘要，**只描述該篇貼文實際討論的內容**，不加推測

### Step 4：建立 archive.org 存檔

對每個採用的貼文 URL：

```bash
# 送出存檔請求
curl -s "https://web.archive.org/save/{貼文完整URL}"

# 等候約 10-30 秒後，確認存檔完成
# 存檔 URL 格式：https://web.archive.org/web/{timestamp}/{原始URL}

# 驗證存檔可存取
curl -s -o /dev/null -w "%{http_code}" \
  "https://web.archive.org/web/2/{貼文完整URL}"
```

如果 archive.org 回傳 200，存檔 URL 為：
```
https://web.archive.org/web/2/{貼文完整URL}
```
（`/web/2/` 會自動導向最新的存檔版本）

### Step 5：產出 HTML

每則輿情卡片的 HTML 結構：

```html
<div class="sent-card">
  <div class="sent-meta">
    <span class="sent-platform">{平台名} · {板名}</span>
    <span class="sent-dot"></span>
    <span class="sent-date">{年份}</span>
    <span class="tone tone-{pos|neg|neu|mix}">{正面|負面|中性|混合}</span>
  </div>
  <div class="sent-body">{1-2 句精確摘要，只描述該貼文實際討論的內容}</div>
  <div class="sent-footer">
    <span class="sent-warning">⚠ 此為摘要，請點入原文自行判讀</span>
    <div style="display:flex;gap:12px">
      <a class="src" href="{原始貼文URL}" target="_blank">查看原文 ↗</a>
      <a class="src" href="{archive.org存檔URL}" target="_blank">存檔備份 ↗</a>
    </div>
  </div>
</div>
```

### Step 6：處理搜尋結果不足的情況

如果篩選後不到 3 篇有價值的貼文，**不要硬湊**。改用以下區塊：

```html
<div class="card">
  <div class="sec-label">輿情概況</div>
  <p style="font-size:14px;color:#666;line-height:1.7">
    {建商名稱} 在 PTT、Mobile01 等公開討論平台的討論數量極少，
    未達好宅通的收錄門檻（至少 3 篇含實質討論的貼文）。
    建議自行搜尋查閱。
  </p>
</div>
```

然後只放搜尋入口：

```html
<div class="search-links">
  <div class="sl-label">自行搜尋更多討論</div>
  <div class="sl-links">
    <a class="src" href="https://www.ptt.cc/bbs/home-sale/search?q={URL編碼}" target="_blank">PTT 搜尋「{建商名稱}」 ↗</a>
    <a class="src" href="https://www.mobile01.com/search.php?search={URL編碼}&type=0&category=455" target="_blank">Mobile01 房屋板 ↗</a>
  </div>
</div>
```

---

## 品質檢查清單

完成後逐項確認：

- [ ] 每則「查看原文」連結回傳 HTTP 200
- [ ] 每則「存檔備份」連結回傳 HTTP 200
- [ ] 摘要內容與貼文原文吻合（不張冠李戴）
- [ ] 沒有任何輿情卡片連結指向搜尋頁面
- [ ] 搜尋量不足時誠實標示，不硬湊

---

## 範例指令

在 Claude Code 中執行：

```
請為「京懋建設」(builder-jingmao.html) 執行輿情蒐集。

已知線索（Cowork 階段透過 Google 搜尋找到的候選 URL）：
- Mobile01 t=4966603「桃園 京懋一號」（12 頁以上討論）
- Mobile01 t=6035812「請教中路特區『京懋一號』二三事」
- Mobile01 t=5548139「京懋会」
- Mobile01 t=6284198「京懋一號與京懋頤和」
- PTT M.1586448711.A.F71「青埔建商請益」

請讀取這些貼文、篩選、撰寫摘要、建立 archive.org 存檔，
然後更新 builder-jingmao.html 的 sec-sentiment 區塊。
```

---

## Cowork ↔ Claude Code 分工總覽

| 步驟 | 環境 | 說明 |
|------|------|------|
| MOEA API 查詢 | Cowork（Chrome） | 透過 Chrome 瀏覽器導航 API |
| 頁面結構建立 | Cowork | 基於模板產出完整 HTML |
| 基本資料 / 建案 / 法律 | Cowork | WebSearch + Chrome |
| builders.html 更新 | Cowork | Edit 工具 |
| **輿情蒐集 + 存檔** | **Claude Code** | **curl 讀取論壇 + archive.org** |
| 品質檢查 | 兩邊各做一次 | Cowork 檢查結構，Code 檢查連結 |
