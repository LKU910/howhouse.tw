# 擇居（howhouse.tw）專案指引

## 專案階段（2026-04-11 起）

本專案已進入 **第二階段（工具開發）**。

### 資料夾結構

```
擇居/
├── 第一階段（內容站）/     ← 備份封存，勿修改
│   ├── deploy/              （第一階段完成時的網站快照）
│   ├── docs/                （早期策略文件）
│   ├── tools/               （資料更新腳本）
│   ├── archive/             （舊版前後端程式碼）
│   ├── FB粉專經營/          （FB 內容排程與策略）
│   ├── TIPO商標/            （商標申請文件）
│   ├── Line商業帳號/        （LINE OA 設定文件）
│   ├── 自我檢驗/
│   ├── _partials/
│   └── (build 工具鏈檔案)
│
├── 第二階段（工具開發）/    ← **主要工作區，所有產出放這裡**
│   ├── deploy/              （正式網站，GitHub + Vercel 部署）
│   ├── 執行策略/            （第二階段策略文件）
│   ├── tools/               （資料更新腳本）
│   ├── _partials/           （HTML 共用元件）
│   └── (build 工具鏈檔案)
│
└── CLAUDE.md               （本檔案）
```

### 工作規則

1. **所有新開發、修改、產出都在 `第二階段（工具開發）/` 進行**
2. `第一階段（內容站）/` 是封存備份，除非特別指示否則不要動
3. 部署到 Vercel 的檔案位於 `第二階段（工具開發）/deploy/`
4. FB 貼文等行銷產出也放在第二階段資料夾下（需要時建立子資料夾）

### 第二階段核心目標

將擇居從「內容站」升級為「互動式買房決策系統」，開發三個核心工具：

1. **我的決策性格** — 選擇之前，先認識自己（入口工具，首頁 Hero，MVP 難度 1/5）
2. **我的買房地圖** — 看看你走到 18 步的哪了（18 步產品化，建立回訪黏性，MVP 難度 1.5/5）
3. **我的財務診斷** — 看清楚這個決定的代價（最高痛點，名單轉換引擎，MVP 難度 2.5/5）

開發順序：我的決策性格 → 我的買房地圖 → 我的財務診斷

### 技術棧

- 純前端 HTML/CSS/JS（無後端框架）
- Tailwind CSS（透過 build-css.sh 編譯）
- **GitHub + Vercel** 靜態部署（howhouse.tw）← 2026-04-14 從 Cloudflare Pages 遷移
- 建商資料：deploy/data-config.json

### Vercel 部署設定（vercel.json 已配置）

- **GitHub Repo root**：`擇居/`（即本 CLAUDE.md 所在資料夾）
- **Build Command**：`cd '第二階段（工具開發）' && npm install && bash build-css.sh`
- **Output Directory**：`第二階段（工具開發）/deploy`
- **vercel.json**：位於 repo 根目錄，包含 headers / redirects / build config

### 注意事項

- 網站品牌名稱：**擇居**
- 網站域名：howhouse.tw（PChome 網域）+ Vercel 託管
- DNS：需將 Cloudflare DNS 的 A/CNAME 記錄改指向 Vercel（詳見遷移指南）
- Email 轉寄：Cloudflare Email Routing → Gmail（繼續保留，不受影響）
- 舊域名 homerun-taiwan.com 301 轉址：在 Vercel dashboard 加入 homerun-taiwan.com 後，vercel.json 已設好轉址規則
- Kuan 負責審閱、法規、合作洽談；AI 負責開發、內容、LINE 營運
- **禁止在路徑中使用 HOMERUN 或 好宅通**：這些都是已淘汰的舊品牌名。專案統一稱「擇居」，所有工作統一在 `擇居/第二階段（工具開發）/` 進行。
