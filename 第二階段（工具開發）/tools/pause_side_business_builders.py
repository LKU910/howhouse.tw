#!/usr/bin/env python3
"""
把佇列中疑似「副業建設」的 pending 改為 paused 狀態。
排程 SOP 只會挑 status == "pending" 或 "in_progress"，所以 paused 的會被跳過。

執行：python3 pause_side_business_builders.py
"""
import json
from pathlib import Path

QUEUE_PATH = Path(__file__).parent / "builder-queue.json"

# 要 pause 的建商（slug_hint 精確匹配）及原因
# 這些是「集團本業非建設」或「建設僅為副業」的候選
TO_PAUSE = {
    # 飯店/觀光/樂園集團
    "guitian":   "桂田飯店集團副業建設；集團本業為飯店觀光，建設規模待確認為主業或副業",
    "guobin":    "國賓大飯店集團；本業為飯店營運，建設非主業",
    "lipao":     "麗寶集團旗下樂園+飯店+賽車場+建設；本體為集團控股性質，若要收應改為旗下建設子公司本體",

    # 汽車/零組件/工業集團
    "nanyangjy": "南陽實業以現代汽車代理為主業，建設非主業",
    "yongfeng":  "永逢企業以建材為主業，建設為副業",

    # 工業/國營/集團控股
    "zhongjie":  "中鋼集團；主業鋼鐵，僅工業園區開發非住宅建設",
    "fumao":     "福懋油脂集團；本業食用油，建設非主業",
    "weijing":   "威京集團為控股性質，沈慶京家族多角化投資；需改收旗下具體建設公司",

    # 名稱疑似但身分不明（先 pause 等查證）
    "fubang":    "中部中型建商但名稱易與富邦金控混淆，需先確認正確公司全名",
    "yaxingke":  "名稱類似亞昕國際（2546）但非同一公司，需查證是否為獨立建商",
    "zhaifen":   "slug 與描述對應不清（京城集團？）；需先釐清指哪一家",
}


def main():
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    # 更新 _meta 加入 paused 狀態值
    if "paused" not in data["_meta"]["status_values"]:
        data["_meta"]["status_values"].append("paused")

    paused_count = 0
    not_found = []
    for slug, reason in TO_PAUSE.items():
        found = False
        for b in data["builders"]:
            if b.get("slug_hint") == slug:
                if b["status"] == "pending":
                    b["status"] = "paused"
                    b["skip_reason"] = reason  # 暫用同一欄位記原因
                    paused_count += 1
                    print(f"  ⏸ {b['name_zh']} ({slug}) → paused")
                else:
                    print(f"  ⚠ {b['name_zh']} ({slug}) 當前狀態 {b['status']}，未變更")
                found = True
                break
        if not found:
            not_found.append(slug)

    if not_found:
        print(f"\n⚠ 以下 slug 在佇列中找不到：{not_found}")

    QUEUE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    from collections import Counter
    c = Counter(b["status"] for b in data["builders"])
    print(f"\n✅ 已 pause {paused_count} 家")
    print(f"   佇列狀態：{dict(c)}")


if __name__ == "__main__":
    main()
