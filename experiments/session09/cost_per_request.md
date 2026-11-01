# Cost per request of the web app (Session 09)

Measured 2026-10-31T21:48:30+00:00 on macOS arm64, Python 3.12.15, model `dafbb5470f2f`. Real HTTP requests to `/api/analyze` on 127.0.0.1, one at a time, after 2 warm-up requests.

| Document | Sentences | Requests | Median (ms) | 95th percentile (ms) | CPU per request (ms) |
|---|---:|---:|---:|---:|---:|
| examples/study/document_F.txt | 16 | 30 | 4.4 | 4.9 | 3.7 |
| examples/fictional_terms.txt x 100 | 1100 | 30 | 140.6 | 154.3 | 139.2 |

Model load: 0.174 s. Peak memory: 143.0 MB (resource.getrusage, peak resident memory of the whole process).
Network calls outside this computer: 0. API cost per request: $0.00.

The product runs on the user's own computer and calls no API, so each request costs us nothing. The honest costs are the user's computer, its electricity and their setup time.

**Hosted estimate** (DigitalOcean Basic Droplet, Regular: 1 GiB memory, 1 vCPU, $0.00893 per hour, from https://www.digitalocean.com/pricing/droplets, looked up 2026-10-31): $0.0109 per million requests for the study document and $0.3488 per million for the long document. One server of this plan answers requests one at a time; the cost of a request is the price of the seconds it takes (price per hour x median seconds / 3600).
Peak memory fits in the plan's 1024 MB: yes.

An always-on server is billed by the hour whatever the traffic, so at low traffic the hourly price, not the cost per request, is what matters.
