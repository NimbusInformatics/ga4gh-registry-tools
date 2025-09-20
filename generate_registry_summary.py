import requests
from jinja2 import Template
import argparse
import json

REGISTRY_URL = "https://registry.ga4gh.org/v1/services"

SERVICE_INFO_PATHS = {
    "drs": "/ga4gh/drs/v1/service-info",
    # Add more artifact types here as needed
}

def fetch_services():
    """Fetch JSON data from GA4GH service registry."""
    response = requests.get(REGISTRY_URL)
    response.raise_for_status()
    return response.json()

def fetch_live_service_info(base_url, artifact):
    """Fetch live service-info JSON from the given base URL based on artifact."""
    path = SERVICE_INFO_PATHS.get(artifact.lower())
    if not path:
        return None, None
    service_info_url = base_url.rstrip("/") + path
    try:
        response = requests.get(service_info_url, timeout=5)
        response.raise_for_status()
        return response.json(), service_info_url
    except Exception as e:
        return {"error": str(e)}, service_info_url

def extract_service_info(services, artifact_filter=None):
    """Extract relevant fields and filter by artifact if specified."""
    extracted = []
    for idx, service in enumerate(services):
        artifact = service.get("type", {}).get("artifact", "N/A")
        version = service.get("type", {}).get("version", "N/A")

        if artifact_filter and artifact.lower() != artifact_filter.lower():
            continue

        base_url = service.get("url", "")
        live_info, service_info_url = fetch_live_service_info(base_url, artifact)
        live_version = live_info.get("type", {}).get("version") if isinstance(live_info, dict) else None
        version_mismatch = live_version and (live_version != version)

        info = {
            "id": f"svc-{idx}",
            "name": service.get("name", "N/A"),
            "artifact": artifact,
            "version": version,
            "org_name": service.get("organization", {}).get("name", "N/A"),
            "url": service_info_url or base_url,
            "live_version": live_version or "N/A",
            "version_mismatch": version_mismatch,
            "raw_json": json.dumps(service, indent=2)
        }
        extracted.append(info)
    return extracted

def generate_html(services_info, output_file="registry_summary.html"):
    """Render HTML summary page using a Jinja2 template."""
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>GA4GH Registry Summary</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
            th { background-color: #f2f2f2; }
            tr:hover { background-color: #f9f9f9; }
            .mismatch { background-color: #ffe6e6; }
            .json-row { display: none; }
            .json-toggle { cursor: pointer; color: blue; text-decoration: underline; }
            pre { background: #f4f4f4; padding: 10px; overflow-x: auto; max-height: 400px; }
        </style>
        <script>
            function toggleJsonRow(id) {
                const row = document.getElementById(id);
                row.style.display = row.style.display === 'table-row' ? 'none' : 'table-row';
            }
        </script>
    </head>
    <body>
        <h1>GA4GH Registry Summary</h1>
        <table>
            <tr>
                <th>Name</th>
                <th>Artifact</th>
                <th>Registry Version</th>
                <th>Live Version</th>
                <th>Organization</th>
                <th>Service-info URL</th>
                <th>More</th>
            </tr>
            {% for svc in services %}
            <tr class="{% if svc.version_mismatch %}mismatch{% endif %}">
                <td>{{ svc.name }}</td>
                <td>{{ svc.artifact }}</td>
                <td>{{ svc.version }}</td>
                <td>{{ svc.live_version }}</td>
                <td>{{ svc.org_name }}</td>
                <td><a href="{{ svc.url }}" target="_blank">{{ svc.url }}</a></td>
                <td><span class="json-toggle" onclick="toggleJsonRow('{{ svc.id }}')">Show JSON registration</span></td>
            </tr>
            <tr id="{{ svc.id }}" class="json-row">
                <td colspan="7"><pre><code class="language-json">{{ svc.raw_json }}</code></pre></td>
            </tr>
            {% endfor %}
        </table>
        <p>Total services: {{ services|length }}</p>
    </body>
    </html>
    """
    template = Template(template_str)
    html_output = template.render(services=services_info)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"HTML summary written to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate GA4GH Registry HTML summary")
    parser.add_argument("--artifact", type=str, help="Filter services by artifact type")
    parser.add_argument("--output", type=str, default="registry_summary.html", help="Output HTML file name")
    args = parser.parse_args()

    services = fetch_services()
    services_info = extract_service_info(services, artifact_filter=args.artifact)
    generate_html(services_info, output_file=args.output)

if __name__ == "__main__":
    main()
