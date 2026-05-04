"""Round 2 probe for the still-weak vendors."""
import concurrent.futures as cf, urllib.request, urllib.error
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

CANDIDATES = {
    "Sophos": [
        "https://www.sophos.com/en-us",
        "https://www.sophos.com/en-us/products/managed-detection-and-response",
        "https://www.sophos.com/en-us/cybersecurity-explained/cloud-security",
        "https://www.sophos.com/en-us/cybersecurity-explained/what-is-cspm",
        "https://news.sophos.com/en-us/category/security-operations/",
        "https://docs.sophos.com/",
    ],
    "Upwind": [
        "https://www.upwind.io/feature",
        "https://www.upwind.io/use-cases",
        "https://www.upwind.io/about",
        "https://www.upwind.io/blog/category/cspm",
        "https://www.upwind.io/blog/runtime-powered-cspm",
        "https://www.upwind.io/blog/runtime-powered-cnapp",
    ],
    "Orca Security": [
        "https://orca.security/platform",
        "https://orca.security/cloud-security/cspm/",
        "https://orca.security/resources/blog/category/cspm/",
        "https://orca.security/resources/blog/",
        "https://orca.security/why-orca/",
        "https://orca.security/cloud-security/cnapp/",
        "https://orca.security/use-cases/",
    ],
    "Wiz": [
        "https://www.wiz.io/solutions/code-security",
        "https://www.wiz.io/solutions/api-security",
        "https://www.wiz.io/solutions/kubernetes-security",
    ],
    "SentinelOne": [
        "https://www.sentinelone.com/platform/singularity-cloud-native-security/",
        "https://www.sentinelone.com/platform/singularity-cloud-workload-security/",
        "https://www.sentinelone.com/platform/singularity-data-lake/",
    ],
    "CrowdStrike": [
        "https://www.crowdstrike.com/platform/cloud-security/dspm/",
        "https://www.crowdstrike.com/platform/cloud-security/ciem/",
        "https://www.crowdstrike.com/platform/identity-protection/",
    ],
    "Microsoft": [
        "https://learn.microsoft.com/en-us/azure/defender-for-cloud/concept-cloud-security-posture-management",
        "https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-containers-introduction",
        "https://learn.microsoft.com/en-us/azure/defender-for-cloud/concept-attack-path",
    ],
    "Aqua Security": [
        "https://www.aquasec.com/products/aqua-cloud-security/",
        "https://www.aquasec.com/aqua-cloud-native-application-protection-platform/",
        "https://www.aquasec.com/cloud-native-academy/cnapp/",
    ],
    "Tenable": [
        "https://www.tenable.com/products/tenable-cloud-security/cnapp",
        "https://www.tenable.com/products/tenable-cloud-security/cspm",
        "https://www.tenable.com/products/tenable-cloud-security/ciem",
        "https://www.tenable.com/products/tenable-cloud-security/dspm",
    ],
    "Snyk": [
        "https://snyk.io/product/snyk-code/",
        "https://snyk.io/product/container-security/",
        "https://snyk.io/solutions/cloud-native-application-security/",
    ],
    "Datadog": [
        "https://www.datadoghq.com/product/cloud-security/",
        "https://www.datadoghq.com/product/cloud-security-management/cspm/",
        "https://www.datadoghq.com/product/cloud-security-management/ciem/",
        "https://www.datadoghq.com/product/cloud-security-management/sensitive-data-scanner/",
    ],
    "Rapid7": [
        "https://www.rapid7.com/products/insightcloudsec/cspm/",
        "https://www.rapid7.com/products/insightcloudsec/cwpp/",
        "https://www.rapid7.com/products/insightcloudsec/ciem/",
        "https://www.rapid7.com/products/exposure-command/",
    ],
}

def probe(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            return url, r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return url, e.code, 0
    except Exception:
        return url, -1, 0

all_urls = [(v, u) for v, urls in CANDIDATES.items() for u in urls]
results = {v: [] for v in CANDIDATES}
with cf.ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(probe, u): (v, u) for v, u in all_urls}
    try:
        for fut in cf.as_completed(futs, timeout=60):
            v, _ = futs[fut]
            results[v].append(fut.result())
    except cf.TimeoutError:
        for fut, (v, u) in futs.items():
            if not fut.done():
                results[v].append((u, -1, 0))

for vendor in CANDIDATES:
    print(f"=== {vendor} ===")
    for url, status, size in sorted(results[vendor], key=lambda r: -r[2]):
        mark = "OK " if status == 200 and size > 5000 else "   "
        print(f"  {mark} [{status:>4}] {size:>7}b  {url}")
    print()
