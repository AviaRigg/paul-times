"""Decrypt an earlier issue's source so it can be used as a pattern.

Usage:  TPT_PASSWORD=xxxx python kit/unlock.py 2026-10-15
Writes  issues/<id>/sections.html (gitignored; never commit it).
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
iid = sys.argv[1]
pw = os.environ.get("TPT_PASSWORD") or sys.exit("Set TPT_PASSWORD")
cfg = json.load(open(os.path.join(ROOT, "docs", "crypto.json")))
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(cfg["salt"]), iterations=cfg["iterations"]).derive(pw.encode())
blob = json.load(open(os.path.join(ROOT, "issues", iid, "sections.enc")))
plain = AESGCM(key).decrypt(base64.b64decode(blob["iv"]), base64.b64decode(blob["ct"]), None)
open(os.path.join(ROOT, "issues", iid, "sections.html"), "wb").write(plain)
print("unlocked", iid)
