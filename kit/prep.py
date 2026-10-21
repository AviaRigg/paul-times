"""Everything the run needs to know before research starts, in ONE call.

Usage:  TPT_PASSWORD=xxxx python kit/prep.py <issue id> [taps.json]

  taps.json (optional): the rows of the "Paul Times taps" Google Sheet saved by the editor.
Writes (all gitignored) to issues/<id>/:
  history.txt   do-not-repeat digest (picks, stock, radar, tool, tips, words, quotes) + claims that fall due today
  skeleton.txt  structure of the previous issue, so nobody has to read its 35k-token source
  taps.txt      SEEN / MY LIST / NOT FOR ME lists, feedback flags and notes, language, sudoku progress (needs taps.json)
Prints a short summary: previous issue, how many claims are due, Paul's feedback, language.
"""
import json, os, subprocess, sys
import tptlib

iid = sys.argv[1]
taps = sys.argv[2] if len(sys.argv) > 2 else None
folder = os.path.join(tptlib.ROOT, "issues", iid)
os.makedirs(os.path.join(folder, "parts"), exist_ok=True)
kit = os.path.join(tptlib.ROOT, "kit")


def capture(name, *cmd):
    r = subprocess.run([sys.executable, *cmd], cwd=tptlib.ROOT, capture_output=True, text=True)
    open(os.path.join(folder, name), "w", encoding="utf-8").write(r.stdout)
    if r.returncode:
        print(f"! {name}: {r.stderr.strip()[-300:]}")
    return r.stdout


hist = capture("history.txt", os.path.join(kit, "history.py"), iid)
prev = tptlib.previous_ids(iid, 1)
capture("skeleton.txt", os.path.join(kit, "skeleton.py"), *(prev[:1]))
n_due = hist.split("CLAIMS DUE")[-1].count('"id"')
print(f"issue {iid}: previous issue {prev[0] if prev else 'none'}; claims due today: {n_due}")
if taps:
    out = capture("taps.txt", os.path.join(kit, "screen_state.py"), taps, iid)
    print(out.strip()[:3000])
else:
    print("no taps.json given: skip Paul's taps (say so in the final report)")
print("files: " + ", ".join(f"{f} {os.path.getsize(os.path.join(folder, f)) // 1024 + 1} KB" for f in ("history.txt", "skeleton.txt", "taps.txt") if os.path.exists(os.path.join(folder, f))))
