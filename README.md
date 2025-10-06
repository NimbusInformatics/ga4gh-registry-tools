# ga4gh-registry-tools

A repo for registry tools.  Specifically, to generate a report in HTML from the public GA4GH registry and to plot a map of the registered DRS servers.

## Install

```bash
conda create -n ga4gh-registry python=3.11 -y
conda activate ga4gh-registry
conda install -c conda-forge cartopy pandas matplotlib -y
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