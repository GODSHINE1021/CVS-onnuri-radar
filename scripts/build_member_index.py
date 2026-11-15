#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""온누리 가맹점 색인(data/member_gs25.json) 생성.

배경
----
`data/merchants/{시도}.json`은 전국 온누리상품권 가맹점(22.5만건) 원본으로, 상호 표기가
제각각이다. 같은 매장이 가맹점 DB에는 "지에스25 대전노은역점", "지에스25(GS25)장대센트럴점",
"GS25 광주수완점"처럼, 점포 DB에는 "GS25대전노은역점"처럼 적혀 있어 문자열을 그대로
비교하면 이미 가맹 등록된 점포가 '미가맹'으로 분류된다.

이 스크립트는 원본에서 GS25 계열 행만 추려 가벼운 색인 파일을 만든다. 상호 정규화와
점포 매칭은 앱(index.html)의 `normBizName()` / `buildMemberIndex()`가 담당한다.
정규화 규칙을 한 곳(JS)에만 두어 색인과 런타임 판정이 어긋나지 않게 하려는 의도이므로,
여기서는 "GS25일 수 있는 행"을 넓게 통과시키고 브랜드 판별은 런타임에 맡긴다.

출력 형식
---------
[["상호", "상권명", "업종", "지류가맹 Y/N", "디지털가맹 Y/N", "등록연도", "시도"], ...]

실행
----
    python3 scripts/build_member_index.py

저장소 루트에서 실행하면 data/member_gs25.json 을 갱신한다.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "data", "merchants")
OUT = os.path.join(ROOT, "data", "member_gs25.json")

# 상호에 이 조각이 있으면 GS25 계열 후보로 본다(정규화·브랜드 판정은 런타임 담당).
BRAND_HINTS = ("지에스", "GS", "gs", "Gs", "gS")


def is_candidate(name: str) -> bool:
    return any(h in name for h in BRAND_HINTS)


def main() -> int:
    if not os.path.isdir(SRC_DIR):
        print(f"입력 폴더가 없습니다: {SRC_DIR}", file=sys.stderr)
        return 1

    rows = []
    files = sorted(f for f in os.listdir(SRC_DIR) if f.endswith(".json"))
    for fn in files:
        sido = fn[: -len(".json")]
        with open(os.path.join(SRC_DIR, fn), encoding="utf-8") as fh:
            data = json.load(fh)
        for m in data:
            name = m[0] if m else ""
            if not name or not is_candidate(name):
                continue
            rows.append([
                name,
                (m[1] if len(m) > 1 else "") or "",
                (m[2] if len(m) > 2 else "") or "",
                (m[3] if len(m) > 3 else "") or "",
                (m[4] if len(m) > 4 else "") or "",
                (m[5] if len(m) > 5 else "") or "",
                sido,
            ])

    rows.sort(key=lambda r: (r[6], r[0]))
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, separators=(",", ":"))

    size = os.path.getsize(OUT)
    print(f"저장: {os.path.relpath(OUT, ROOT)} · {len(rows):,}건 · {size / 1024:.1f} KB")
    by_sido = {}
    for r in rows:
        by_sido[r[6]] = by_sido.get(r[6], 0) + 1
    print("시도별:", ", ".join(f"{k} {v:,}" for k, v in sorted(by_sido.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
