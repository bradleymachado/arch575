# -*- coding: utf-8 -*-
"""vendor_three.py - download three.js at a pinned version into js/vendor/ (no CDN at runtime).

Files (plan v1.1 section 2 lists three; the 0.186.1 build needs two more, found by reading the imports):
  js/vendor/three.module.js                      <- build/three.module.js      (re-exports ./three.core.js)
  js/vendor/three.core.js                        <- build/three.core.js        (imported by three.module.js since r163)
  js/vendor/addons/loaders/GLTFLoader.js         <- examples/jsm/loaders/GLTFLoader.js
  js/vendor/addons/utils/BufferGeometryUtils.js  <- examples/jsm/utils/BufferGeometryUtils.js
  js/vendor/addons/utils/SkeletonUtils.js        <- examples/jsm/utils/SkeletonUtils.js (imported by GLTFLoader)
GLTFLoader imports 'three', '../utils/BufferGeometryUtils.js' and '../utils/SkeletonUtils.js';
index.html maps 'three' and 'three/addons/' with an importmap. REVISION lives in three.core.js.

Usage (from the repo root):  python tools/vendor_three.py [version]   (default 0.186.1)
"""
import sys, os, re, urllib.request

VERSION = "0.186.1"
BASE = "https://cdn.jsdelivr.net/npm/three@%s/"
FILES = [("build/three.module.js", "three.module.js"),
         ("build/three.core.js", "three.core.js"),
         ("examples/jsm/loaders/GLTFLoader.js", "addons/loaders/GLTFLoader.js"),
         ("examples/jsm/utils/BufferGeometryUtils.js", "addons/utils/BufferGeometryUtils.js"),
         ("examples/jsm/utils/SkeletonUtils.js", "addons/utils/SkeletonUtils.js")]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(REPO, "js", "vendor")


def main(version):
    for src, dst in FILES:
        url = BASE % version + src
        out = os.path.join(VENDOR, dst)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        data = urllib.request.urlopen(url, timeout=60).read()
        with open(out, "wb") as f:
            f.write(data)
        print("%-45s %9d bytes" % (dst, len(data)))
    core = open(os.path.join(VENDOR, "three.core.js"), encoding="utf-8").read()
    m = re.search(r"const REVISION = '([^']+)'", core)
    print("three.core.js REVISION = %s (package %s)" % (m.group(1) if m else "not found", version))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else VERSION)
