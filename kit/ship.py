"""One command for the whole publish step: assemble, lint, build, commit, push.

Usage:  TPT_PASSWORD=xxxx python kit/ship.py <issue id> [--edition daily|sunday] [--no-push] [--force]

Run it as soon as there is anything to show (a partial issue is fine, missing parts become "more later today"),
and again after every deepening pass. Blocking lint problems stop it unless --force is given (use --force only
for the early partial push). Never prints the password. Plain sections.html stays gitignored; only the encrypted
files are committed.
"""
import json, os, subprocess, sys
import tptlib

iid = sys.argv[1]
ed = sys.argv[sys.argv.index("--edition") + 1] if "--edition" in sys.argv else "daily"
py, kit = sys.executable, os.path.join(tptlib.ROOT, "kit")
meta = json.load(open(os.path.join(tptlib.ROOT, "issues", iid, "parts", "meta.json"))) if os.path.exists(os.path.join(tptlib.ROOT, "issues", iid, "parts", "meta.json")) else {}


def run(*a, check=True):
    r = subprocess.run(a, cwd=tptlib.ROOT)
    if check and r.returncode:
        sys.exit(r.returncode)
    return r.returncode


run(py, os.path.join(kit, "assemble.py"), iid, "--edition", ed)
if run(py, os.path.join(kit, "lint.py"), iid, "--fix", check=False) and "--force" not in sys.argv:
    sys.exit("lint found blocking problems: fix them, or use --force for a partial early push")
sudoku = meta.get("sudoku") or ("Easy:38,Medium:32,Hard:26,Hard:24" if ed == "sunday" else "Medium:32,Hard:25")
run(py, os.path.join(kit, "build.py"), iid, "--edition", "daily", "--title", meta.get("title", ""), "--sudoku", sudoku)
if "--no-push" in sys.argv:
    sys.exit(0)
run("git", "add", "docs", "issues", "kit/feedback-handled.json")
staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=tptlib.ROOT, capture_output=True, text=True).stdout.split()
bad = [f for f in staged if f.endswith("sections.html") or "/parts/" in f or f.endswith(".txt") or "portfolio" in f]
if bad:
    run("git", "reset", "-q")
    sys.exit("refusing to commit plain-text files: " + ", ".join(bad))
run("git", "commit", "-m", f"Issue {iid}", "-m", "Co-Authored-By: Claude <noreply@anthropic.com>", check=False)
run("git", "push")
print("pushed; the site updates in about 90 seconds")
