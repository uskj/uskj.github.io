import json, hmac, hashlib, time
from pathlib import Path

BASE = Path(__file__).parent
CFG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))

# 卡密格式：  <hours>-xi<HMAC8>
# 与 server.py 的 verify_card 共享 config.cards 列表
def gen(hours, count=1):
    out = []
    for _ in range(count):
        raw = f"{hours}-{int(time.time()*1000)}-{_}"
        h = hmac.new(b"xi_secret_2026", raw.encode(), hashlib.sha256).hexdigest()[:8]
        out.append(f"{hours}-xi{h}")
    return out

if __name__ == "__main__":
    import sys
    # 用法： python gen_codes.py 24 3    -> 3张24h
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 72
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    codes = gen(hours, count)

    # 写回 config.json 的 cards（去重合并）
    cards = CFG.get("cards", [])
    codes = [c for c in codes if c not in [x["code"] for x in cards]]
    for c in codes:
        cards.append({"hours": hours, "code": c})
    CFG["cards"] = cards
    (BASE / "config.json").write_text(json.dumps(CFG, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"生成 {len(codes)} 张 {hours}h 卡密：")
    for c in codes:
        print("  ", c)
    print("已写入 config.json")
