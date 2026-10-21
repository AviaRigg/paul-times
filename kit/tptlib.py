"""Shared helpers for the Paul Times kit (decrypting earlier issues, reading the index)."""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def aes():
    pw = os.environ.get("TPT_PASSWORD") or sys.exit("Set TPT_PASSWORD")
    cfg = json.load(open(os.path.join(ROOT, "docs", "crypto.json")))
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(cfg["salt"]),
                     iterations=cfg["iterations"]).derive(pw.encode())
    return AESGCM(key)


def index():
    p = os.path.join(ROOT, "docs", "issues.json")
    return json.load(open(p)) if os.path.exists(p) else []


def sections_of(iid, cipher=None):
    """Decrypted sections.html of an earlier issue, or None if it is not in the repo."""
    p = os.path.join(ROOT, "issues", iid, "sections.enc")
    if not os.path.exists(p):
        return None
    b = json.load(open(p))
    try:
        return (cipher or aes()).decrypt(base64.b64decode(b["iv"]), base64.b64decode(b["ct"]), None).decode("utf-8")
    except Exception:
        print(f"warning: could not decrypt {iid} (wrong TPT_PASSWORD?)", file=sys.stderr)
        return None


def previous_ids(before, n=60):
    ids = sorted((i["id"] for i in index() if i["id"] < before), reverse=True)
    return ids[:n]
