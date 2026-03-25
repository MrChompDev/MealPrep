#!/usr/bin/env python3
"""
Vendor installer: download wheels from PyPI and extract into vendor/
Usage:
    python vendor_install.py SQLAlchemy==2.0.20
If no version is given, the latest release is used.
"""
import sys
import os
import json
import shutil
import zipfile
import urllib.request

VENDOR_DIR = os.path.abspath("vendor")
WHEELS_DIR = os.path.join(VENDOR_DIR, "wheels")

def ensure_dirs():
    os.makedirs(WHEELS_DIR, exist_ok=True)

def pypi_json(package):
    url = f"https://pypi.org/pypi/{package}/json"
    with urllib.request.urlopen(url) as r:
        return json.load(r)

def choose_wheel(releases):
    wheel_candidates = [f for f in releases if f["filename"].endswith(".whl")]
    if not wheel_candidates:
        return None
    def score(f):
        fn = f["filename"].lower()
        score = 0
        if "py3" in fn or "py311" in fn or "py310" in fn:
            score += 10
        if "none-any.whl" in fn or ".py3-none-any.whl" in fn:
            score += 20
        if "cp" in fn:
            score += 5
        return score
    wheel_candidates.sort(key=score, reverse=True)
    return wheel_candidates[0]

def download_file(url, dest):
    print(f"Downloading {url} -> {dest}")
    with urllib.request.urlopen(url) as r, open(dest, "wb") as out:
        shutil.copyfileobj(r, out)

def extract_wheel(path, dest):
    print(f"Extracting {os.path.basename(path)} to {dest}")
    with zipfile.ZipFile(path, "r") as z:
        z.extractall(dest)

def parse_requires_dist(info):
    requires = info.get("requires_dist") or []
    deps = []
    for r in requires:
        pkg = r.split(";")[0].strip().split(" ")[0]
        if pkg:
            deps.append(pkg)
    return deps

def vendor_package(spec):
    if "==" in spec:
        name, version = spec.split("==", 1)
    else:
        name, version = spec, None
    name = name.strip()
    print(f"\nProcessing {name} {('version '+version) if version else ''}")
    data = pypi_json(name)
    releases = []
    if version:
        if version not in data["releases"]:
            raise SystemExit(f"Version {version} not found for {name}")
        releases = data["releases"][version]
    else:
        latest = data["info"]["version"]
        releases = data["releases"][latest]
    wheel = choose_wheel(releases)
    if not wheel:
        raise SystemExit(f"No wheel found for {name}")
    url = wheel["url"]
    filename = wheel["filename"]
    local_wheel = os.path.join(WHEELS_DIR, filename)
    if not os.path.exists(local_wheel):
        download_file(url, local_wheel)
    extract_wheel(local_wheel, VENDOR_DIR)
    deps = parse_requires_dist(data["info"])
    return deps

def main():
    if len(sys.argv) < 2:
        print("Usage: python vendor_install.py SQLAlchemy==2.0.20")
        sys.exit(1)
    ensure_dirs()
    to_process = sys.argv[1:]
    processed = set()
    while to_process:
        spec = to_process.pop(0)
        pkg_name = spec.split("==")[0] if "==" in spec else spec
        if pkg_name.lower() in processed:
            continue
        try:
            deps = vendor_package(spec)
        except Exception as e:
            print("Error:", e)
            sys.exit(1)
        processed.add(pkg_name.lower())
        for d in deps:
            if d and d.lower() not in processed:
                to_process.append(d)
    init_py = os.path.join(VENDOR_DIR, "__init__.py")
    with open(init_py, "w") as f:
        f.write(
            "import sys, os\n"
            "p = os.path.dirname(__file__)\n"
            "if p not in sys.path:\n"
            "    sys.path.insert(0, p)\n"
        )
    print("\nVendor install complete. Add `import vendor` at top of your app.py or ensure vendor/ is on sys.path.")

if __name__ == "__main__":
    main()
