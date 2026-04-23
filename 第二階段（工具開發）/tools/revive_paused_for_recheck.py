#!/usr/bin/env python3
"""
2026-04-23 重新放寬標準：有推過任一案就收。
把名稱含「建設」或有可能推過案的 paused 恢復為 pending，讓排程依新 SOP 重新查證。
明顯不能收（名稱衝突、身分不明）的維持 paused。
"""
import json
from pathlib import Path

QUEUE_PATH = Path(__file__).parent / "builder-queue.json"

# 恢復 pending：讓排程用新 SOP 查證是否推過案
REVIVE_TO_PENDING = {
    "guobin":    "標準放寬至「曾推過任一案即收」，由排程查證國賓集團旗下建設公司推案紀錄",
    "nanyangjy": "標準放寬，查證南陽實業歷史上是否以本公司名義推過建案",
    "yongfeng":  "標準放寬，查證永逢企業歷史上是否推過建案",
    "zhongjie":  "標準放寬，查證中鋼建設／中鋼開發推案紀錄",
    "fumao":     "標準放寬，查證福懋集團本體或福懋建設推案紀錄",
    "weijing":   "威京集團推案主體為鼎越（已收），請 agent 改查威京本體或其他子公司推案",
}

# 維持 paused（明顯無法確定身分，不讓排程浪費 token）
KEEP_PAUSED_REASON_UPDATE = {
    "fubang":    "保留 paused：候選名稱「富邦建設中部」不確定是否為獨立公司；Kuan 另補「富邦建設」候選已在 pending",
    "yaxingke":  "保留 paused：「亞昕開發科技」與上市亞昕國際（5213 已收）可能混淆，名稱需釐清",
    "zhaifen":   "保留 paused：slug 對應不清，京城建設（kindom）已收",
}


def main():
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    revived = 0
    updated_paused = 0
    not_found = []

    for b in data["builders"]:
        slug = b.get("slug_hint")
        if slug in REVIVE_TO_PENDING and b["status"] == "paused":
            b["status"] = "pending"
            b["skip_reason"] = None
            b["notes"] = (b.get("notes") or "") + " [2026-04-23 標準放寬後恢復排程]"
            revived += 1
            print(f"  🔄 {b['name_zh']} ({slug}) paused → pending")
        elif slug in KEEP_PAUSED_REASON_UPDATE and b["status"] == "paused":
            b["skip_reason"] = KEEP_PAUSED_REASON_UPDATE[slug]
            updated_paused += 1
            print(f"  ⏸ {b['name_zh']} ({slug}) 保持 paused，理由更新")

    QUEUE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    from collections import Counter
    c = Counter(b["status"] for b in data["builders"])
    print()
    print(f"✅ 恢復 {revived} 家 paused → pending")
    print(f"   更新 {updated_paused} 家 paused 理由")
    print(f"   佇列現況：{dict(c)}")


if __name__ == "__main__":
    main()
