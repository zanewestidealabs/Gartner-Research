"""
Probe candidate replacement URLs for CNAPP vendors with weak page coverage.

For each vendor that had < 3 cached pages in v1.1, try a list of plausible
alternate URLs. Print which ones return HTTP 200 with substantive HTML so we
can promote them into VENDOR_URLS for the v1.2 re-fetch.
"""
from __future__ import annotations
import concurrent.futures as cf
import urllib.request
import urllib.error
from typing import Dict, List, Tuple

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

CANDIDATES: Dict[str, List[str]] = {
    "Sophos": [
        "https://www.sophos.com/en-us/products/cloud-native-security",
        "https://www.sophos.com/en-us/products/cloud-optix",
        "https://www.sophos.com/en-us/cybersecurity-explained/cnapp",
        "https://www.sophos.com/en-us/products",
        "https://docs.sophos.com/central/Customer/help/en-us/PeopleAndDevices/CloudOptix/index.html",
    ],
    "Bitdefender": [
        "https://www.bitdefender.com/business/products/gravityzone-platform.html",
        "https://www.bitdefender.com/business/products/cloud-security.html",
        "https://www.bitdefender.com/business/solutions/cloud-workload-security.html",
        "https://www.bitdefender.com/business/products/container-security.html",
        "https://www.bitdefender.com/en-us/business",
    ],
    "Caveonix": [
        "https://www.caveonix.com/",
        "https://www.caveonix.com/platform/",
        "https://www.caveonix.com/cloud-security-posture-management/",
        "https://www.caveonix.com/multi-cloud-compliance/",
        "https://www.caveonix.com/about-us/",
    ],
    "Fortinet": [
        "https://www.fortinet.com/products/public-cloud-security/forticnapp",
        "https://www.fortinet.com/products/public-cloud-security",
        "https://www.fortinet.com/solutions/enterprise-midsize-business/cloud-security",
        "https://www.fortinet.com/products/public-cloud-security/cloud-workload-protection",
        "https://docs.fortinet.com/product/forticnapp",
    ],
    "Check Point": [
        "https://www.checkpoint.com/cloudguard/cnapp/",
        "https://www.checkpoint.com/cloudguard/",
        "https://www.checkpoint.com/cloudguard/cloud-network-security/",
        "https://www.checkpoint.com/cloudguard/code-security/",
        "https://www.checkpoint.com/cloudguard/cloud-detection-response/",
    ],
    "Qualys": [
        "https://www.qualys.com/apps/totalcloud/",
        "https://www.qualys.com/cloud-platform/",
        "https://www.qualys.com/apps/cloud-security-assessment/",
        "https://www.qualys.com/apps/container-runtime-security/",
        "https://www.qualys.com/forms/totalcloud/",
    ],
    "Uptycs": [
        "https://www.uptycs.com/products/cnapp",
        "https://www.uptycs.com/products/kubernetes-and-container-security",
        "https://www.uptycs.com/products/cloud-workload-protection",
        "https://www.uptycs.com/products",
        "https://www.uptycs.com/platform",
    ],
    "Upwind": [
        "https://www.upwind.io/feature/cspm",
        "https://www.upwind.io/feature/cwpp",
        "https://www.upwind.io/feature/dspm",
        "https://www.upwind.io/feature/api-security",
        "https://www.upwind.io/feature/runtime",
    ],
    "Sweet Security": [
        "https://sweet.security/",
        "https://sweet.security/platform",
        "https://sweet.security/runtime-cspm",
        "https://sweet.security/cloud-detection-response",
        "https://sweet.security/non-human-identity",
    ],
    "AccuKnox": [
        "https://www.accuknox.com/",
        "https://www.accuknox.com/saas",
        "https://www.accuknox.com/cspm",
        "https://www.accuknox.com/kubernetes-security",
        "https://www.accuknox.com/runtime-security",
    ],
    "Trend Micro": [
        "https://www.trendmicro.com/en_us/business/products/one-platform.html",
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one.html",
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-workload-security.html",
        "https://www.trendmicro.com/en_us/business/products/hybrid-cloud/cloud-one-application-security.html",
        "https://www.trendmicro.com/en_us/business/services/managed-xdr.html",
    ],
    "Sysdig": [
        "https://sysdig.com/products/secure/",
        "https://sysdig.com/products/cloud-detection-and-response/",
        "https://sysdig.com/use-cases/cspm/",
        "https://sysdig.com/use-cases/ciem/",
        "https://sysdig.com/use-cases/vulnerability-management/",
    ],
    "Orca Security": [
        "https://orca.security/platform/cspm/",
        "https://orca.security/platform/cwpp/",
        "https://orca.security/platform/ciem/",
        "https://orca.security/platform/dspm/",
        "https://orca.security/platform/cdr/",
    ],
}


def probe(url: str) -> Tuple[str, int, int]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read()
            return url, resp.status, len(body)
    except urllib.error.HTTPError as e:
        return url, e.code, 0
    except Exception as e:
        return url, -1, 0


def main() -> None:
    all_urls = [(v, u) for v, urls in CANDIDATES.items() for u in urls]
    results: Dict[str, List[Tuple[str, int, int]]] = {v: [] for v in CANDIDATES}

    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(probe, u): (v, u) for v, u in all_urls}
        for fut in cf.as_completed(futs):
            v, u = futs[fut]
            results[v].append(fut.result())

    print()
    for vendor in CANDIDATES:
        print(f"=== {vendor} ===")
        for url, status, size in sorted(results[vendor], key=lambda r: -r[2]):
            mark = "OK " if status == 200 and size > 5000 else "   "
            print(f"  {mark} [{status:>4}] {size:>7}b  {url}")
        print()


if __name__ == "__main__":
    main()
