#!/usr/bin/env python3
"""
2026-04-26 將所有短版（< 1500 行）標記為 pending_upgrade，準備升級為長版。
- 佇列中已 done 的 57 家短版：status done → pending_upgrade
- 第一階段 9 家短版（不在佇列）：append 為 pending_upgrade

執行：python3 mark_upgrades_20260426.py
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEPLOY = ROOT / "deploy"
QUEUE_PATH = ROOT / "tools" / "builder-queue.json"

# 第一階段 9 家短版（不在佇列）的 slug → 中文名（從 builders.html 陣列取）
PHASE_ONE_SHORTS = {
    "continental": ("大陸建設", "Continental Development Corp."),
    "dachien":     ("達欣工程", "Da-Cin Construction Co."),
    "huaku":       ("華固建設", "Huaku Development Co."),
    "hungkuo":     ("宏國建設", "Hung Kuo Construction"),
    "hungpai":     ("鴻柏建設", "Hong Bai Construction"),
    "kindom":      ("京城建設", "Kindom Construction Corp."),
    "nanguocc":    ("南國建設", "Nankuo Construction"),
    "ruentex":     ("潤泰創新", "Ruentex Development Co."),
    "yungching":   ("永慶建設", "Yung Ching Construction"),
}


def get_short_files():
    """回傳所有 < 1500 行、不含 -full 的 builder-*.html 檔對應的 slug 集合"""
    shorts = set()
    for f in sorted(os.listdir(DEPLOY)):
        if not (f.startswith("builder-") and f.endswith(".html")) or "-full" in f:
            continue
        path = DEPLOY / f
        with open(path) as fp:
            n = sum(1 for _ in fp)
        if n < 1500:
            slug = f.replace("builder-", "").replace(".html", "")
            shorts.add(slug)
    return shorts


def main():
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    short_slugs = get_short_files()
    print(f"📋 偵測到短版 HTML 檔 {len(short_slugs)} 個")

    # 1. 佇列中已 done 的短版：done → pending_upgrade
    upgraded_in_queue = 0
    for b in data["builders"]:
        if b["status"] == "done" and b.get("completed_slug") in short_slugs:
            b["status"] = "pending_upgrade"
            # 保留 completed_slug、completed_at 作為「升級前資訊」
            # attempt_count 不重置，但 last_attempt 標記新時間意義較不清，先不動
            upgraded_in_queue += 1

    print(f"✅ 佇列中 {upgraded_in_queue} 家 done → pending_upgrade")

    # 2. 第一階段 9 家短版加入佇列（status = pending_upgrade）
    existing_slugs_in_queue = {b.get("slug_hint") for b in data["builders"]} | \
                              {b.get("completed_slug") for b in data["builders"] if b.get("completed_slug")}
    appended = 0
    for slug, (zh, en) in PHASE_ONE_SHORTS.items():
        if slug in short_slugs and slug not in existing_slugs_in_queue:
            data["builders"].append({
                "slug_hint": slug,
                "name_zh": zh,
                "name_en_hint": en,
                "stock_hint": None,
                "region_hint": None,
                "notes": "[第一階段建商，本次升級為長版] 既有 builder-{slug}.html 為短版（< 800 行），需以 baojia 長版模板覆寫".replace("{slug}", slug),
                "status": "pending_upgrade",
                "attempt_count": 0,
                "last_attempt": None,
                "skip_reason": None,
                "completed_at": None,
                "completed_slug": slug,  # 已存在的 HTML 對應 slug，升級時要刪舊檔
            })
            appended += 1

    print(f"✅ 加入第一階段 {appended} 家短版到佇列為 pending_upgrade")

    # 同步 _meta.status_values
    if "pending_upgrade" not in data["_meta"]["status_values"]:
        data["_meta"]["status_values"].append("pending_upgrade")

    # 寫回
    QUEUE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    from collections import Counter
    c = Counter(b["status"] for b in data["builders"])
    print()
    print(f"📊 佇列現況：{dict(c)}")
    print(f"   總計 {len(data['builders'])}")


if __name__ == "__main__":
    main()
