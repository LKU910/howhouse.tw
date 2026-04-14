# 擇居（howhouse.tw） — 遷移至 GitHub + Vercel 操作指南

> 執行日期：2026-04-14  
> 從：Cloudflare Pages  
> 到：GitHub + Vercel

---

## 概覽：你需要做什麼

| 步驟 | 動作 | 在哪裡做 |
|------|------|----------|
| 1 | 清理 git lock、初始化 repo、push 到 GitHub | Terminal（Mac） |
| 2 | 在 Vercel 匯入 GitHub repo | vercel.com |
| 3 | 在 Vercel 設定 howhouse.tw 自訂網域 | Vercel Dashboard |
| 4 | 在 Cloudflare DNS 改 CNAME 指向 Vercel | Cloudflare Dashboard |
| 5 | 確認 homerun-taiwan.com 轉址（可選） | Vercel Dashboard |
| 6 | 停用 Cloudflare Pages 專案（可選） | Cloudflare Dashboard |

---

## 步驟 1：初始化 GitHub Repo（Terminal）

打開 Terminal，執行以下指令：

```bash
# 進入擇居資料夾
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude\ Cowork/擇居
# （或你的實際路徑，視你把 Claude Cowork 資料夾放在哪）

# 清除損壞的 git 初始化（如果有的話）
rm -rf .git

# 重新初始化
git init -b main
git config user.email "lku910@gmail.com"
git config user.name "Kuan"

# 加入所有檔案（.gitignore 會自動排除 node_modules 等）
git add -A

# 初次 commit
git commit -m "初始化擇居（howhouse.tw） — 遷移至 GitHub + Vercel"
```

接著在 GitHub 建立一個新的私有 repo（建議命名 `howhouse`），然後：

```bash
# 把剛才建立的 GitHub repo 網址替換進去
git remote add origin https://github.com/你的帳號/howhouse.git
git push -u origin main
```

> 提示：如果你用 GitHub Desktop，也可以直接「Add Existing Repository」選擇這個資料夾。

---

## 步驟 2：在 Vercel 匯入 GitHub Repo

1. 前往 [vercel.com](https://vercel.com) → **Add New Project**
2. 選擇剛才 push 的 `howhouse` repo
3. Vercel 會自動偵測到根目錄的 `vercel.json`，build 設定會自動帶入：
   - **Build Command**: `cd '第二階段（工具開發）' && npm install && bash build-css.sh`
   - **Output Directory**: `第二階段（工具開發）/deploy`
4. 不需要設定 Environment Variables
5. 按下 **Deploy** — Vercel 會自動 build 並給你一個 `*.vercel.app` 預覽網址

> 先用這個預覽網址確認網站正常運作，再進行下一步。

---

## 步驟 3：在 Vercel 設定 howhouse.tw 自訂網域

1. Vercel Dashboard → 你的 `howhouse` 專案 → **Settings** → **Domains**
2. 點 **Add Domain**，輸入 `howhouse.tw`
3. Vercel 會顯示需要設定的 DNS 記錄（通常是 CNAME）

---

## 步驟 4：在 Cloudflare DNS 更改指向

**重要**：Cloudflare Email Routing 不受影響，你只需要改網站的 DNS 記錄。

前往 Cloudflare Dashboard → 你的 `howhouse.tw` zone → **DNS**：

找到目前指向 Cloudflare Pages 的記錄（通常是 CNAME），改成 Vercel 告訴你的值：

| 類型 | 名稱 | 值 |
|------|------|----|
| CNAME | `@` | `cname.vercel-dns.com` |
| CNAME | `www` | `cname.vercel-dns.com` |

> ⚠️ 注意：不要動 `MX` 記錄（Email Routing 用的）！只改 A/CNAME。

DNS 生效時間通常幾分鐘內（因為 Cloudflare 的 TTL 很短）。

---

## 步驟 5：設定 homerun-taiwan.com 轉址（舊域名）

`vercel.json` 已內建轉址規則，但 Vercel 需要知道 homerun-taiwan.com 屬於你的帳號。

1. Vercel → **Settings** → **Domains** → **Add Domain**
2. 加入 `homerun-taiwan.com` 和 `www.homerun-taiwan.com`
3. 在 Cloudflare（homerun-taiwan.com 的 DNS 管理處）：
   - 把 CNAME 改指向 `cname.vercel-dns.com`
   - 這樣 homerun-taiwan.com 的流量就會進 Vercel，然後被 301 轉到 howhouse.tw

---

## 步驟 6：停用 Cloudflare Pages 舊專案

確認 howhouse.tw 在 Vercel 正常運作後，可選擇性停用：

1. Cloudflare Dashboard → **Pages** → 找到舊的 `howhouse` 或 `homerun` 專案
2. **Settings** → **Delete project**

> 不急著刪，等 1-2 週確認一切正常再刪。

---

## 日後更新網站

只需在本機修改檔案，然後：

```bash
git add -A
git commit -m "更新內容說明"
git push
```

Vercel 會自動偵測到 GitHub push，重新 build 並部署。**完全不需要手動操作 Vercel。**

---

## 技術對照表（Cloudflare → Vercel）

| 功能 | Cloudflare Pages | Vercel |
|------|-----------------|--------|
| Build command | Dashboard 設定 | `vercel.json` |
| Output dir | Dashboard 設定 | `vercel.json` |
| `_headers` | Cloudflare 格式 | `vercel.json` headers |
| `_redirects` | Cloudflare 格式 | `vercel.json` redirects |
| `robots.txt` | 不變 | 不變 |
| `sitemap.xml` | 不變 | 不變 |
| 自動部署 | ✅ | ✅ |
| PR 預覽網址 | ✅ | ✅（每個 branch 有獨立網址）|
| Email Routing | Cloudflare 繼續保留 | ← 不受影響 |

---

## 已完成的配置檔案（AI 已建立）

- ✅ `vercel.json` — Build 設定 + Cache headers + 安全 headers + homerun 轉址
- ✅ `.gitignore` — 排除 node_modules、.DS_Store、.env 等
- ✅ `CLAUDE.md` — 已更新技術棧說明
