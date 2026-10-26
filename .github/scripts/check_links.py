"""Fail when a relative link or #anchor in the Markdown files does not resolve.
Usage: check_links.py <docs root>"""
import os, re, sys
root = sys.argv[1]
def slug(h):
    h = h.strip().lower()
    h = re.sub(r"[`*_]", "", h)
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")
anchors = {}
for d, _, fs in os.walk(root):
    if ".git" in d: continue
    for f in fs:
        if f.endswith(".md"):
            p = os.path.join(d, f); text = open(p).read()
            text_nocode = re.sub(r"```.*?```", "", text, flags=re.S)
            anchors[os.path.abspath(p)] = {slug(m) for m in re.findall(r"^#+\s+(.*)$", text_nocode, re.M)}
bad = 0
for p in anchors:
    text = re.sub(r"```.*?```", "", open(p).read(), flags=re.S)
    for link in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"(https?:|mailto:)", link): continue
        path, _, anc = link.partition("#")
        target = os.path.abspath(os.path.join(os.path.dirname(p), path)) if path else p
        if not os.path.exists(target):
            print("MISSING", os.path.relpath(p, root), link); bad += 1; continue
        if anc and target.endswith(".md") and anc not in anchors.get(target, set()):
            print("ANCHOR", os.path.relpath(p, root), link); bad += 1
print("broken links:", bad)
sys.exit(1 if bad else 0)
