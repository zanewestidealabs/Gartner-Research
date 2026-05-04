import urllib.request, json

r = urllib.request.urlopen("http://localhost:5000/api/vendor-files")
print("Status:", r.status)
files = json.loads(r.read())
print("Total vendor files:", len(files))
offsec = [f for f in files if "Offensive" in f.get("file", "")]
print("OffSec files:")
for f in offsec:
    print(f"  {f['file']} ({f.get('count', '?')} vendors)")
