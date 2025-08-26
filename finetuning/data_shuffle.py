import json, random, re
from pathlib import Path

# ===== 설정 =====
QA_PATH         = "/home/a2024712006/qualcomm/fine_tuning/data/train_en_qa.jsonl"
CASE_PATH       = "/home/a2024712006/qualcomm/fine_tuning/data/train_en_case.jsonl"
GUIDE_PATH      = "/home/a2024712006/qualcomm/fine_tuning/data/train_en_guide.jsonl"
OUT_ALL_PATH    = "/home/a2024712006/qualcomm/fine_tuning/data/train_en_all.jsonl"

SEED            = 42

def read_jsonl(path: str):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            data.append(json.loads(line))
    return data


def main():
    random.seed(SEED)

    qa = read_jsonl(QA_PATH)
    gl = read_jsonl(GUIDE_PATH)
    case = read_jsonl(CASE_PATH)
    merged = qa + gl + case 
    random.shuffle(merged)


    # save
    with open(OUT_ALL_PATH, "w", encoding="utf-8") as f:
        for ex in merged:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # log
    print(f"Saved: {OUT_ALL_PATH}  |  total={len(merged)}")

if __name__ == "__main__":
    main()