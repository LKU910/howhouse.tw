# 擇居 Looker Studio 儀表板擴充指引

> 建立日期：2026-04-21
> 目的：提供三張儀表板的完整 chart 規格，以後有足夠資料（建議 1 週後）時可以快速擴充

---

## 目前已完成

**報表名稱**：擇居｜數據儀表板
**資料源**：zeju-howhouse（GA4 Property ID: 532825427）
**基礎骨架**：已建立第一頁 + 一個時間序列圖（每日頁面瀏覽量）

找得到這份報表：[lookerstudio.google.com](https://lookerstudio.google.com) → 我擁有的項目 → 擇居｜數據儀表板

---

## 重要前提

**Looker Studio 的 GA4 自訂事件顯示原則**：
- 你需要先在 GA4 設定「自訂維度」(Custom Dimensions) 才能在 Looker Studio 用事件參數當 dimension
- 對 `persona`、`builder_slug`、`step_id`、`burden_ratio` 等參數要能用，先去 GA4 → Admin → Custom Definitions 把它們註冊為自訂維度
- 註冊後，資料要 24 小時才開始流入

建議先等一週（2026-04-28 左右）：
1. 有足夠流量讓圖表不空白
2. 自訂維度註冊後已開始收集資料

---

## 儀表板 01｜總覽 + 工具漏斗（第一頁，當前頁）

**核心問題**：擇居每天有多少人用？工具完成率怎樣？

### 已建：每日頁面瀏覽時間序列 ✓

### 待建 Chart（建議 6 個）

| # | Chart 類型 | 標題 | Dimension | Metric | Filter |
|---|---|---|---|---|---|
| 1 | 評量卡 | 日活躍使用者（DAU） | — | activeUsers | 日期=今日 |
| 2 | 評量卡 | 週活躍使用者（WAU） | — | activeUsers | 日期=近 7 天 |
| 3 | 評量卡 | 月活躍使用者（MAU） | — | activeUsers | 日期=近 28 天 |
| 4 | 折線圖 | 活躍使用者趨勢 | date | activeUsers | 近 30 天 |
| 5 | 表格 | 流量來源 | sessionSource | users, sessions | — |
| 6 | 漏斗式表格 | 三工具完成率 | eventName | eventCount | eventName IN (quiz_started, quiz_completed, calculator_loaded, calculator_full_completed, progress_loaded, progress_step_status_changed) |

### 建立每張 chart 的步驟（統一流程）

1. 點頂部「新增圖表」→ 選對應類型
2. 在畫布上拖拉出一個區域
3. 右側「設定」面板：
   - 維度（Dimension）：填上表中的欄位
   - 指標（Metric）：填上表中的欄位
4. 右側「篩選」面板（如需要）：點「+ 新增篩選器」→ 設定條件

---

## 儀表板 02｜18 步熱度 + 建商熱度（第二頁）

**核心問題**：買房 18 步裡哪幾步最熱門？建商頁被哪幾家最多人查？

### 建立第二頁

1. 左側頁面面板點「+ 新增頁面」
2. 頁面名稱改為「儀表板 02｜18 步 + 建商熱度」

### 待建 Chart（建議 5 個）

| # | Chart 類型 | 標題 | Dimension | Metric | Filter |
|---|---|---|---|---|---|
| 1 | 橫向長條圖 | 18 步頁面瀏覽排行 | pageTitle | screenPageViews | pagePath 含 `/step/` |
| 2 | 表格 | 18 步滾動完成率 | step_id（自訂維度） | eventCount | eventName=`step_page_scroll_depth` AND depth=`100` |
| 3 | 橫向長條圖 | 建商熱度排行 | builder_slug（自訂維度） | eventCount | eventName=`builder_card_clicked` |
| 4 | 表格 | 建商完整版 vs 簡版切換 | builder_slug, is_full_version | eventCount | eventName=`content_page_viewed` AND page_type=`builder_detail` |
| 5 | 散佈圖 | 建商頁瀏覽 vs 停留時間 | builder_slug | screenPageViews, averageSessionDuration | pagePath 含 `/builder-` |

---

## 儀表板 03｜內容表現 + LINE 轉換（第三頁）

**核心問題**：Guide 文章哪篇最吸引？從哪些頁面最多人點 LINE？

### 建立第三頁

1. 左側頁面面板點「+ 新增頁面」
2. 頁面名稱改為「儀表板 03｜內容表現 + LINE」

### 待建 Chart（建議 5 個）

| # | Chart 類型 | 標題 | Dimension | Metric | Filter |
|---|---|---|---|---|---|
| 1 | 表格 | Guide 六篇表現 | guide_slug（自訂維度） | screenPageViews, averageSessionDuration | eventName=`content_page_viewed` AND page_type=`guide` |
| 2 | 橫向長條圖 | Guide 閱讀完成率 | guide_slug | eventCount | eventName=`guide_scroll_depth` AND depth=`100` |
| 3 | 圓餅圖 | LINE 加入來源分布 | location（location 參數） | eventCount | eventName=`line_add_friend_clicked` |
| 4 | 評量卡 | 本週 LINE 加入數 | — | eventCount | eventName=`line_add_friend_clicked` AND 日期=近 7 天 |
| 5 | 表格 | 跨工具跳轉路徑 | from_tool, to_tool | eventCount | eventName=`tool_to_tool_jump` |

---

## 需要先在 GA4 建立的自訂維度

進入 GA4 → Admin → Custom Definitions → Custom Dimensions → Create

| 維度名稱 | 範圍 | 事件參數 | 用途 |
|---|---|---|---|
| Persona | Event | persona | 測驗完成後的人格結果 |
| Step ID | Event | step_id | 18 步的步驟編號 |
| Builder Slug | Event | builder_slug | 建商識別（cathay、farglory 等） |
| Is Full Version | Event | is_full_version | 建商頁是否是完整版 |
| Guide Slug | Event | guide_slug | Guide 文章識別 |
| Scroll Depth | Event | depth | 滾動深度（25/50/75/100） |
| LINE CTA Location | Event | location | LINE 按鈕被點的頁面類型 |
| Burden Ratio Bucket | Event | bucket | 負擔比分級（high / very_high） |
| From Tool | Event | from_tool | 跨工具跳轉：來源 |
| To Tool | Event | to_tool | 跨工具跳轉：目標 |

**注意**：這些維度建立後 24 小時才會開始收集資料，已經發生的事件不會回溯。所以越早建越好。

---

## 建議時程

| 時機 | 做什麼 |
|---|---|
| **今天** | 建好以上 10 個自訂維度，讓 GA4 開始收集 |
| **第 1 週** | 用 GA4 內建報表觀察基本流量，確認事件有進來 |
| **第 8 天** | 一起擴充 Looker Studio 儀表板 01/02/03 的所有 chart（那時已有真實資料） |
| **每月** | 根據實際使用行為微調儀表板 |

---

## 如果要我（Claude）繼續擴充儀表板

告訴我：「繼續擴充 Looker Studio 儀表板」+ 哪個優先。我會根據這份指引接手建 chart。

但建議至少等到 2026-04-28 之後，資料夠多了擴充才有意義。

---

## 替代方案：用 GA4 內建報表

如果覺得 Looker Studio 太複雜，GA4 內建的「報表」+「探索」功能已經有 80% 的功能。

**每週只要看這三個 GA4 頁面：**

1. **報表 → 即時**：看現在有多少人在線上
2. **報表 → 參與 → 事件**：看每個事件的計數與使用者數
3. **探索 → 建立漏斗探索**：看 quiz_started → quiz_completed → calculator_loaded 的轉換率

這三個頁面無需任何建置，GA4 自動產生。

---

*擇居 Looker Studio 擴充指引 v1.0 — 2026-04-21*
