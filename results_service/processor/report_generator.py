import os
import json
import csv
import uuid
from datetime import datetime

# Note: In a real implementation, you'd use a library like ReportLab for PDF generation
# For simplicity, this example just creates basic reports in different formats

def generate_report(scan_id, vulnerabilities, report_format='pdf', options=None):
    """
    Generate a report from scan results
    
    Args:
        scan_id (str): ID of the scan
        vulnerabilities (list): List of vulnerabilities
        report_format (str): Report format (pdf, csv, html, json)
        options (dict): Additional report options
        
    Returns:
        str: Path to the generated report
    """
    # Create reports directory if it doesn't exist
    reports_dir = os.environ.get('REPORTS_DIR', '../data/reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"report_{scan_id}_{timestamp}"
    
    # Generate report based on format
    if report_format == 'json':
        return generate_json_report(scan_id, vulnerabilities, os.path.join(reports_dir, f"{filename}.json"), options)
    elif report_format == 'csv':
        return generate_csv_report(scan_id, vulnerabilities, os.path.join(reports_dir, f"{filename}.csv"), options)
    elif report_format == 'html':
        return generate_html_report(scan_id, vulnerabilities, os.path.join(reports_dir, f"{filename}.html"), options)
    else:
        # Default to PDF
        return generate_pdf_report(scan_id, vulnerabilities, os.path.join(reports_dir, f"{filename}.pdf"), options)

def generate_json_report(scan_id, vulnerabilities, output_path, options=None):
    """Generate a JSON report"""
    report_data = {
        'scan_id': scan_id,
        'generated_at': datetime.now().isoformat(),
        'vulnerabilities': vulnerabilities,
        'summary': generate_summary(vulnerabilities)
    }
    
    with open(output_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    return output_path

def generate_csv_report(scan_id, vulnerabilities, output_path, options=None):
    """Generate a CSV report"""
    # Define CSV fields
    fields = [
        'ID', 'File', 'Function', 'Line', 'Severity', 'Type', 
        'CWE', 'Description', 'Recommendation'
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for vuln in vulnerabilities:
            writer.writerow({
                'ID': vuln.get('id', 'N/A'),
                'File': vuln.get('file_name', 'N/A'),
                'Function': vuln.get('function_name', 'N/A'),
                'Line': vuln.get('line_number', 'N/A'),
                'Severity': vuln.get('severity', 'N/A'),
                'Type': vuln.get('vulnerability_type') or vuln.get('type', 'N/A'),
                'CWE': vuln.get('cwe_id', 'N/A'),
                'Description': vuln.get('description', 'N/A'),
                'Recommendation': vuln.get('recommendation', 'N/A')
            })
    
    return output_path

def generate_html_report(scan_id, vulnerabilities, output_path, options=None):
    """Generate an HTML report"""
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>VulCNN Scan Report - {scan_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .high {{ background-color: #ffebee; }}
            .medium {{ background-color: #fff8e1; }}
            .low {{ background-color: #e3f2fd; }}
            .summary {{ margin: 20px 0; padding: 10px; background-color: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>VulCNN Vulnerability Scan Report</h1>
        <p>Scan ID: {scan_id}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p>Total vulnerabilities: {len(vulnerabilities)}</p>
            <p>High severity: {sum(1 for v in vulnerabilities if v.get('severity') == 'high')}</p>
            <p>Medium severity: {sum(1 for v in vulnerabilities if v.get('severity') == 'medium')}</p>
            <p>Low severity: {sum(1 for v in vulnerabilities if v.get('severity') == 'low')}</p>
        </div>
        
        <h2>Vulnerabilities</h2>
        <table>
            <tr>
                <th>Severity</th>
                <th>Type</th>
                <th>File</th>
                <th>Function</th>
                <th>Line</th>
                <th>CWE</th>
                <th>Description</th>
            </tr>
    """
    
    # Add vulnerabilities to table
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'medium')
        html += f"""
            <tr class="{severity}">
                <td>{severity.upper()}</td>
                <td>{vuln.get('vulnerability_type') or vuln.get('type', 'N/A')}</td>
                <td>{vuln.get('file_name', 'N/A')}</td>
                <td>{vuln.get('function_name', 'N/A')}</td>
                <td>{vuln.get('line_number', 'N/A')}</td>
                <td>{vuln.get('cwe_id', 'N/A')}</td>
                <td>{vuln.get('description', 'N/A')}</td>
            </tr>
        """
    
    # Close HTML
    html += """
        </table>
    </body>
    </html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path

def generate_pdf_report(scan_id, vulnerabilities, output_path, options=None):
    """
    Generate a PDF report
    
    Note: In a real implementation, you'd use a library like ReportLab
    For simplicity, this example just generates an HTML report and returns the path
    """
    # In a real implementation, you would use a PDF generation library
    # For this example, we'll just create an HTML report
    html_path = output_path.replace('.pdf', '.html')
    html_path = generate_html_report(scan_id, vulnerabilities, html_path, options)
    
    # In a real implementation, you would then convert this HTML to PDF
    # For example, using a library like WeasyPrint or xhtml2pdf
    
    # For demonstration purposes, we'll just rename the HTML file to PDF
    # (this wouldn't actually create a valid PDF)
    try:
        os.rename(html_path, output_path)
    except Exception as e:
        print(f"Error renaming file: {str(e)}")
        # Fall back to HTML
        return html_path
    
    return output_path

def generate_summary(vulnerabilities):
    """Generate a summary of vulnerabilities"""
    # Count by severity
    severity_counts = {
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    # Count by type
    type_counts = {}
    
    # Count by CWE
    cwe_counts = {}
    
    for vuln in vulnerabilities:
        # Count by severity
        severity = vuln.get('severity', 'medium')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by type
        vuln_type = vuln.get('vulnerability_type') or vuln.get('type', 'Unknown')
        type_counts[vuln_type] = type_counts.get(vuln_type, 0) + 1
        
        # Count by CWE
        cwe = vuln.get('cwe_id', 'Unknown')
        cwe_counts[cwe] = cwe_counts.get(cwe, 0) + 1
    
    return {
        'total': len(vulnerabilities),
        'by_severity': severity_counts,
        'by_type': type_counts,
        'by_cwe': cwe_counts
    }