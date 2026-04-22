#!/usr/bin/env python3
"""
一次性腳本：把 100 家新候選 append 到 builder-queue.json。
執行：python3 append_candidates_100.py
執行後請檢查 git diff，OK 再讓排程自動跑。
"""
import json
from pathlib import Path

QUEUE_PATH = Path(__file__).parent / "builder-queue.json"

# 100 家新候選，依地區 / 知名度組織
# 格式：(slug_hint, name_zh, name_en_hint, stock_hint, region_hint, notes)
NEW_CANDIDATES = [
    # ─────────────────────────────────────────────
    # A. 雙北・知名上市／上櫃建商（之前漏收）約 12 家
    # ─────────────────────────────────────────────
    ("longbang", "龍邦國際興業", "Lung Pang International Industry", "2514", "雙北", "上市建商；富邦蔡家關係人；涉足建設、保險、金融"),
    ("guochan", "國產實業", "Goldsun Development and Construction", "2504", "雙北", "上市；預拌混凝土領導品牌兼建商；林家兄弟持股"),
    ("huajian", "華建企業", "Hua-Eng Wires and Cables Co.", "2515", "雙北", "上市；華新麗華集團建設部門"),
    ("sanfeng", "三豐建設", "San Fong Construction", "5514", "雙北", "上市；中型建商"),
    ("genji", "根基營造", "Genesis Engineering", "2546", "雙北", "上市；冠德集團旗下營造廠"),
    ("gongxin", "工信工程", "Kung Sing Engineering Corp.", "5521", "雙北", "上市；公共工程與建設"),
    ("yongxin", "永信建設", "Yong Xin Construction", "5508", "桃園·新竹", "上市；中小型建商"),
    ("shangyao", "上曜建設", "Shang Yao Construction", "1316", "雙北", "上市；中型建商"),
    ("dahan", "大漢建設", "Dahan Construction", "5520", "中部·北部", "上市；中部起家"),
    ("jixiangquan", "吉祥全建設", "Ji Xiang Quan Construction", "5484", "雙北", "上市；中小型建商"),
    ("haiyue", "海悅國際開發", "Hai Yue International Development", "3702", "雙北·全台", "上市；代銷龍頭；近年轉投資建案"),
    ("xinluzhijia", "欣陸投資控股", "Continental Holdings", "3703", "雙北", "上市；大陸工程+大陸建設母公司；集團控股"),

    # ─────────────────────────────────────────────
    # B. 雙北・知名未上市／上櫃建商 約 20 家
    # ─────────────────────────────────────────────
    ("zhongtai", "忠泰建設", "JUT Land Development Group", None, "雙北", "忠泰集團；信義計畫區豪宅指標；JUT 美術館、忠泰樂生活"),
    ("puyuan", "璞園建設", "Pu Yuan Construction", None, "雙北", "璞園建築團隊；北市中價位品牌；富藝術美學名聲"),
    ("dingyue", "鼎越開發", "Ding Yue Construction", None, "雙北", "以雙北都更與危老起家"),
    ("renxiang", "仁翔建設", "Jen Shang Construction", None, "雙北", "主打中價位建案"),
    ("ruiguang", "瑞光開發", "Rui Guang Development", None, "雙北", "雙北中大型建商"),
    ("sanmen", "三門建設", "San Men Construction", None, "雙北", "中型建商"),
    ("hanhuang", "漢皇建設", "Han Huang Construction", None, "雙北·桃園", "雙北中型建商"),
    ("longshanlin", "瓏山林建設", "Long Shan Lin Construction", None, "雙北·宜蘭", "雙北精緻住宅；宜蘭溫泉度假住宅"),
    ("xingzhong", "興中建設", "Hsing Chung Construction", None, "雙北", "中型建商"),
    ("shangpin", "上品建設", "Shang Pin Construction", None, "雙北", "中高端住宅"),
    ("nanyangjy", "南陽實業", "Nan Yang Corporation", None, "雙北", "現代汽車代理+建設事業"),
    ("jingqinglin", "清景麟建築", "Qing Jing Lin Architect Group", None, "雙北·桃園", "清景麟建築團隊；中高端建案"),
    ("hongzhu", "鴻築建設", "Hong Zhu Construction", None, "雙北", "中型建商"),
    ("yuanhong", "元宏建設", "Yuan Hong Construction", None, "雙北", "中型建商"),
    ("guanwei", "冠維建設", "Guan Wei Construction", None, "雙北", "中型建商"),
    ("fudu", "富都建設", "Fu Du Construction", None, "雙北", "中型建商"),
    ("jiancheng", "建誠建設", "Jian Cheng Construction", None, "雙北·桃園", "中型建商"),
    ("guoxiongtpe", "國雄建設", "Guo Xiong Construction", None, "雙北", "中型建商"),
    ("xinlong", "欣隆開發", "Xin Long Development", None, "雙北", "欣隆集團；中型建商"),
    ("jimeitpe", "吉美建設", "Ji Mei Construction", None, "雙北·桃園", "中型建商；北部深耕"),

    # ─────────────────────────────────────────────
    # C. 桃園・新竹 約 10 家
    # ─────────────────────────────────────────────
    ("haiwan", "海灣建設", "Haiwan Construction", None, "桃園·北部", "桃園大型建商"),
    ("kuancheng", "寬誠建設", "Kuan Cheng Construction", None, "桃園·新竹", "中型建商"),
    ("guitian", "桂田建設", "Gui Tian Construction", None, "桃園·台南", "桂田集團；酒店+建設"),
    ("lixin", "立信建設", "Li Xin Construction", None, "新竹", "新竹中型建商"),
    ("fuyu", "富宇建築團隊", "Fu Yu Construction Group", None, "桃園·新竹", "桃園中壢起家；近年擴及新竹"),
    ("dayan", "大硯建設", "Da Yan Construction", None, "新竹", "新竹科技業客群"),
    ("fengming", "楓明建設", "Feng Ming Construction", None, "新竹", "新竹中型建商"),
    ("zhanyuan", "展元建設", "Zhan Yuan Construction", None, "桃園", "桃園中型建商"),
    ("xinhuang", "欣皇建設", "Xin Huang Construction", None, "桃園·新竹", "桃園中型建商"),
    ("qianye", "千葉建設", "Qian Ye Construction", None, "新竹", "新竹中型建商"),

    # ─────────────────────────────────────────────
    # D. 台中・中部主力建商 約 20 家
    # ─────────────────────────────────────────────
    ("jingrui", "精銳建設", "Jing Rui Construction", None, "台中", "台中中高端豪宅指標；陳豐靖家族"),
    ("huiyu", "惠宇建設", "Hui Yu Construction", None, "台中", "台中老牌大型建商"),
    ("panyu", "磐鈺建設", "Pan Yu Construction", None, "台中", "台中中高端豪宅"),
    ("lianju", "聯聚建設", "Lian Ju Construction", None, "台中", "七期指標；僅蓋豪宅"),
    ("baohui", "寶輝建設", "Bao Hui Construction", None, "台中", "台中七期豪宅"),
    ("dacheng", "大城建設", "Da Cheng Construction", None, "台中", "中高端住宅；台中知名"),
    ("yunjiang", "允將建設", "Yun Jiang Construction", None, "台中", "中高端住宅"),
    ("lipao", "麗寶建設", "Lipao Group", None, "台中·北部", "麗寶集團建設部門；吳寶田家族"),
    ("fubang", "富邦建設中部", "Fu Bang Construction (Central Taiwan)", None, "台中", "中部中型建商（非富邦金）"),
    ("baoxi", "寶璽建設", "Bao Xi Construction", None, "台中", "台中中高端住宅"),
    ("fengyi", "豐邑建設", "Feng Yi Construction", None, "新竹·台中", "豐邑機構；新竹台中大型案"),
    ("panxing", "磐興建設", "Pan Xing Construction", None, "台中", "台中中型建商"),
    ("longbao", "龍寶建設", "Long Bao Construction", None, "台中", "台中七期；中高端"),
    ("yongfeng", "永逢建設", "Yong Feng Construction", None, "台中", "永逢企業集團；建材+建設"),
    ("ruifeng", "瑞豐建設", "Rui Feng Construction", None, "台中", "台中中型建商"),
    ("dayi", "大毅建設", "Da Yi Construction", None, "台中", "台中大型建商；早期知名"),
    ("qihong", "啟弘建設", "Qi Hong Construction", None, "台中·彰化", "中部中型建商"),
    ("dingyuntc", "鼎宇建設", "Ding Yu Construction", None, "台中", "台中中型建商"),
    ("zhongfu", "中福建設", "Zhong Fu Construction", None, "台中", "中部中型建商"),
    ("yuanchungc", "元鴻建設", "Yuan Hong (Central) Construction", None, "台中·彰化", "中部中型建商"),

    # ─────────────────────────────────────────────
    # E. 高雄・台南・南部 約 20 家
    # ─────────────────────────────────────────────
    ("changgu", "長谷建設", "Chang Gu Construction", "1493", "高雄", "上市；高雄老牌大型建商"),
    ("hechang", "合康建設", "He Kang Construction", None, "高雄", "高雄中大型"),
    ("xinye", "新業建設", "Xin Ye Construction", None, "高雄", "高雄指標建商；中高端品質路線"),
    ("qingchang", "慶昌建設", "Qing Chang Construction", None, "高雄", "高雄老牌大型建商"),
    ("chuangyi", "創意建設", "Chuang Yi Construction", None, "高雄", "高雄中型建商"),
    ("chengyang", "城揚建設", "Cheng Yang Construction", None, "高雄·屏東", "南部中大型建商"),
    ("fanqiao", "泛喬建設", "Fan Qiao Construction", None, "高雄", "高雄大型建商"),
    ("huayoulian", "華友聯開發", "Hua You Lian Development", "1436", "高雄", "上市；高雄指標建商"),
    ("guobin", "國賓大飯店建設", "Ambassador Hotels", None, "雙北·高雄", "國賓集團；飯店+建設"),
    ("qingxiu", "慶秀建設", "Qing Xiu Construction", None, "高雄·台南", "南部中型建商"),
    ("zhaifen", "京城集團", "Kindom Group (Kaohsiung)", None, "高雄", "京城集團旗下關係建商（不是京城建設本體）"),
    ("guofeng", "國豐興業", "Guo Feng Enterprise", None, "高雄", "高雄中型建商"),
    ("dayang", "大洋建設", "Da Yang Construction", None, "台南", "台南中型建商"),
    ("zuanshi", "鑽石建設", "Zuan Shi Construction", None, "台南", "台南中型建商"),
    ("jinghui", "璟慧建設", "Jing Hui Construction", None, "台南", "台南中型建商"),
    ("jinhua", "錦華建設", "Jin Hua Construction", None, "台南", "台南中型建商"),
    ("wuzhou", "五洲建設", "Wu Zhou Construction", None, "台南·高雄", "南部中型建商"),
    ("fumao", "福懋建設", "Fu Mao Construction", None, "高雄", "福懋集團；南部建商"),
    ("yaxingke", "亞昕開發科技", "Ya Xing Technology Development", None, "高雄", "高雄中型建商（非亞昕國際）"),
    ("zhongjie", "中鋼建設", "China Steel Construction", None, "高雄", "中鋼集團；工業園區開發"),

    # ─────────────────────────────────────────────
    # F. 其他補充 約 18 家
    # ─────────────────────────────────────────────
    ("weijing", "威京集團建設", "Wei Jing Group", None, "雙北", "威京集團；沈慶京家族；中華電信大樓地主"),
    ("guomei", "國美建設", "Kuo Mei Construction", None, "雙北·桃園", "老牌建商"),
    ("mingzhi", "明志建設", "Ming Zhi Construction", None, "雙北", "中型建商"),
    ("yongzai", "永在建設", "Yong Zai Construction", None, "雙北", "中型建商"),
    ("zhengxin", "正鑫建設", "Zheng Xin Construction", None, "雙北", "中型建商"),
    ("zhengju", "正鉅建設", "Zheng Ju Construction", None, "雙北", "中型建商"),
    ("hekang", "賀康建設", "He Kang Construction (North)", None, "雙北", "中小型建商（與高雄合康同名異司）"),
    ("haoran", "昊然機構", "Hao Ran Construction Group", None, "雙北", "中型建商"),
    ("qinmei", "勤美璞真", "Chin Mei Pu Chen Development", None, "雙北·台中", "勤美集團與璞真合資；信義區誠品松菸BOT旁"),
    ("hongyi", "鴻翊建設", "Hong Yi Construction", None, "雙北", "中型建商"),
    ("chengzhi", "誠之建設", "Cheng Zhi Construction", None, "雙北", "中型建商"),
    ("huayang", "華陽建設", "Hua Yang Construction", None, "雙北", "中型建商"),
    ("jinmaochang", "錦茂建設", "Jin Mao Construction", None, "雙北", "中型建商"),
    ("baoshi", "寶實建設", "Bao Shi Construction", None, "雙北", "中型建商"),
    ("hongyin", "宏銀建設", "Hong Yin Construction", None, "雙北", "中型建商"),
    ("jinwei", "晉緯建設", "Jin Wei Construction", None, "雙北", "中型建商"),
    ("chengyu", "誠宇建設", "Cheng Yu Construction", None, "雙北", "中型建商"),
    ("damao", "大茂建設", "Da Mao Construction", None, "雙北", "中型建商"),
]

assert len(NEW_CANDIDATES) == 100, f"候選數應為 100，實為 {len(NEW_CANDIDATES)}"


def main():
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    existing_slugs_in_meta = set(data["_meta"]["existing_slugs"])
    existing_slugs_in_queue = {b.get("slug_hint") for b in data["builders"]} | {b.get("completed_slug") for b in data["builders"] if b.get("completed_slug")}
    all_existing = existing_slugs_in_meta | existing_slugs_in_queue

    # 檢查 slug 衝突
    seen_new = set()
    collisions = []
    for slug, name_zh, *_ in NEW_CANDIDATES:
        if slug in all_existing:
            collisions.append((slug, name_zh, "與現有衝突"))
        elif slug in seen_new:
            collisions.append((slug, name_zh, "新候選內重複"))
        else:
            seen_new.add(slug)

    if collisions:
        print("⚠ slug 衝突，請修改後重試：")
        for c in collisions:
            print(" ", c)
        return

    # Append
    for slug, name_zh, name_en, stock, region, notes in NEW_CANDIDATES:
        data["builders"].append({
            "slug_hint": slug,
            "name_zh": name_zh,
            "name_en_hint": name_en,
            "stock_hint": stock,
            "region_hint": region,
            "notes": notes,
            "status": "pending",
            "attempt_count": 0,
            "last_attempt": None,
            "skip_reason": null_to_none(None),
            "completed_at": None,
            "completed_slug": None,
        })

    # 寫回
    QUEUE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 統計
    from collections import Counter
    status_counter = Counter(b["status"] for b in data["builders"])
    print(f"✅ 已 append {len(NEW_CANDIDATES)} 家新候選")
    print(f"   佇列總計：{len(data['builders'])}")
    print(f"   狀態分布：{dict(status_counter)}")


def null_to_none(v):
    return v  # 純粹保留可讀性


if __name__ == "__main__":
    main()
