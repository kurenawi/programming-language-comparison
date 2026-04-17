import csv, json, sys
from collections import Counter
from pathlib import Path

def main(src: str, dst: str):
    rows = []
    with open(src, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            row['id'] = int(row['id'])
            row['estimate'] = int(row['estimate'])
            rows.append(row)

    summary = {
        'total_tasks': len(rows),
        'status_counts': dict(Counter(r['status'] for r in rows)),
        'points_by_priority': {
            p: sum(r['estimate'] for r in rows if r['priority'] == p)
            for p in ['high', 'medium', 'low']
        },
    }

    out = {'tasks': rows, 'summary': summary}
    Path(dst).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
