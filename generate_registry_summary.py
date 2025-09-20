import requests
from jinja2 import Template
import argparse

REGISTRY_URL = "https://registry.ga4gh.org/v1/services"

def fetch_services():
    """Fetch JSON data from GA4GH service registry."""
    response = requests.get(REGISTRY_URL)
    response.raise_for_status()
    return response.json()

def extract_service_info(services, artifact_filter=None):
    """Extract relevant fields and filter by artifact if specified."""
    extracted = []
    for service in services:
        artifact = service.get("type", {}).get("artifact", "N/A")
        if artifact_filter and artifact.lower() != artifact_filter.lower():
            continue
        info = {
            "name": service.get("name", "N/A"),
            "artifact": artifact,
            "version": service.get("version", "N/A"),
            "org_name": service.get("organization", {}).get("name", "N/A"),
            "url": service.get("url", "#"),
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
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:hover { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>GA4GH Registry Summary</h1>
        <table>
            <tr>
                <th>Name</th>
                <th>Artifact</th>
                <th>Version</th>
                <th>Organization</th>
                <th>URL</th>
            </tr>
            {% for svc in services %}
            <tr>
                <td>{{ svc.name }}</td>
                <td>{{ svc.artifact }}</td>
                <td>{{ svc.version }}</td>
                <td>{{ svc.org_name }}</td>
                <td><a href="{{ svc.url }}" target="_blank">{{ svc.url }}</a></td>
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