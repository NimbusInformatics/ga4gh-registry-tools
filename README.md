# ga4gh-registry-tools

A repo for registry tools.  Specifically, to generate a report in HTML from the public GA4GH registry.

## Install

```bash
conda create -n ga4gh-registry python=3.11 -y
conda activate ga4gh-registry
pip install requests jinja2
```
## Running Tool & Making Registry Reports

### Show all services (default)
    python generate_registry_summary.py

### Filter only those with artifact "drs"
    python generate_registry_summary.py --artifact drs

### Output to custom filename
    python generate_registry_summary.py --artifact drs --output drs_summary.html

## Sample Output

I generated the file `outputs/drs_summary.html` on 20250919.

