# ga4gh-registry-tools

A repo for registry tools.  Specifically, to generate a report in HTML from the public GA4GH registry and to plot a map of the registered DRS servers.

## Install

```bash
conda create -n ga4gh-registry python=3.11 -y
conda activate ga4gh-registry
conda install -c conda-forge cartopy pandas matplotlib pyyaml openpyxl pip -y
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

## Generating a DRS Map

Note, I created a snapshot of registration information in the `drs_servers.tsv` file on 20251006.

In the future, this information needs to come from the GA4GH registry.  This will 
happen once the geolocation and other fields are added to the official GA4GH registry.

### Inputs

I put a simple inputs file in `drs_servers.tsv`, this was created by harvesting information
from a Google form but in the future this should be the registry.

### Generating the Map

This generates an interactive window and also .png and .svg output files.

```bash
python plot_drs_map.py
```

### Sample Map Output

The DRS map as of 20251006:

![The DRS map as of 20251006](/drs_world_map_cartopy.svg)

## Generate Registry JSON from Temporary Google Form for DRS Registration

For submission to the [official GA4GH registry](https://github.com/ga4gh/ga4gh-registry?tab=readme-ov-file) from the temporary [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSeEI6QOtNQoyha0ZcLQYaTVsA3IkWZLOzz9g1L7ZQjke2MIBA/viewform?usp=dialog) we're using to collect DRS servers.

Use a downloaded excel file from the temporary [Google Form output](https://docs.google.com/spreadsheets/d/12lXZvpwzQ3nbjNlxJoqG57U5qFe8PhQ4smeJCeS5ZkM/edit?resourcekey=&gid=1020047121#gid=1020047121) for DRS server registration.  You likely don't have access to this file since it's not a public doc.  Slack Brian for access.

```bash
# run (Excel example)
python generate_registry_json.py \
  --input "drs_servers.xlsx" \
  --sheet "Form Responses 1" \
  --config config.yaml \
  --output services.json \
  --drop-empty
```