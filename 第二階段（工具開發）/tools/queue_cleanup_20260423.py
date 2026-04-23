#!/usr/bin/env python3
"""
2026-04-23 佇列清理：
1. 3 家 done → skipped（根基、工信、欣陸）
2. 麗寶、桂田從 paused 恢復 pending
3. 新增富邦建設（富邦金集團旗下，蔡明忠家族）
4. 把 existing_slugs 同步更新
"""
import json
from pathlib import Path

QUEUE_PATH = Path(__file__).parent / "builder-queue.json"

SKIP_REASONS = {
    "genji": "本體業別為營造廠（冠德集團自有）非建商；不自行推案 — 刪除 HTML 檔 2026-04-23",
    "gongxin": "本體業別為公共工程營造商 非住宅建商 — 刪除 HTML 檔 2026-04-23",
    "xinluzhijia": "投資控股公司本體不推案（推案的是大陸建設 continental） — 刪除 HTML 檔 2026-04-23",
}

REVIVE_SLUGS = ["lipao", "guitian"]

NEW_CANDIDATE = {
    "slug_hint": "fubon",
    "name_zh": "富邦建設",
    "name_en_hint": "Fubon Land Development",
    "stock_hint": None,
    "region_hint": "雙北豪宅",
    "notes": "富邦金集團旗下建設公司（非富邦金控本體）；蔡明忠家族持有；信義區大規模推案；豪宅高端路線。注意與「富邦建設中部」為不同公司",
    "status": "pending",
    "attempt_count": 0,
    "last_attempt": None,
    "skip_reason": None,
    "completed_at": None,
    "completed_slug": None,
}


def main():
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    # 1. 刪 3 家
    for b in data["builders"]:
        if b.get("completed_slug") in SKIP_REASONS:
            old_slug = b["completed_slug"]
            b["status"] = "skipped"
            b["skip_reason"] = SKIP_REASONS[old_slug]
            b["completed_slug"] = None
            print(f"  ❌ {b['name_zh']} ({old_slug}) done → skipped")

    # 2. 恢復 2 家
    for b in data["builders"]:
        if b.get("slug_hint") in REVIVE_SLUGS and b["status"] == "paused":
            b["status"] = "pending"
            b["skip_reason"] = None  # 清除先前填寫的 paused 理由
            print(f"  🔄 {b['name_zh']} ({b['slug_hint']}) paused → pending")

    # 3. 新增富邦建設
    existing_slugs_all = {b.get("slug_hint") for b in data["builders"]} | {b.get("completed_slug") for b in data["builders"] if b.get("completed_slug")}
    if NEW_CANDIDATE["slug_hint"] in existing_slugs_all:
        print(f"  ⚠ slug {NEW_CANDIDATE['slug_hint']} 已存在，跳過")
    else:
        data["builders"].append(NEW_CANDIDATE)
        print(f"  ➕ 新增：{NEW_CANDIDATE['name_zh']} ({NEW_CANDIDATE['slug_hint']})")

    # 4. 同步 existing_slugs（從已 done 的 completed_slug 重新計算，排除剛改成 skipped 的）
    data["_meta"]["existing_slugs"] = sorted({
        b["completed_slug"]
        for b in data["builders"]
        if b.get("completed_slug") and b["status"] == "done"
    })

    # 存檔
    QUEUE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    from collections import Counter
    c = Counter(b["status"] for b in data["builders"])
    print()
    print(f"✅ 佇列狀態：{dict(c)}")
    print(f"   existing_slugs 數量：{len(data['_meta']['existing_slugs'])}")


if __name__ == "__main__":
    main()
