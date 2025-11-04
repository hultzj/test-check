# Ansible Automation Platform Organization Inspector

A Python script to inspect organizations in Ansible Automation Platform (AAP) using the API 2.3 and identify their dependencies and related resources.

## Features

- Retrieve detailed organization information from AAP
- Identify all resources associated with an organization (teams, projects, inventories, etc.)
- Detect cross-organization dependencies
- Support for both organization name and ID lookup
- Export results to JSON format
- Secure password handling (prompts for credentials)

## Requirements

- Python 3.6+
- Access to Ansible Automation Platform with API 2.3
- Valid AAP credentials with permissions to view organizations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable (optional):
```bash
chmod +x aap_org_inspector.py
```

## Usage

### Basic Usage

Inspect an organization by name:
```bash
python aap_org_inspector.py "My Organization" --url https://aap.example.com
```

Inspect an organization by ID:
```bash
python aap_org_inspector.py 5 --url https://aap.example.com
```

### Advanced Options

Provide credentials via command line (not recommended for security):
```bash
python aap_org_inspector.py "My Organization" \
  --url https://aap.example.com \
  --username admin \
  --password mypassword
```

Disable SSL verification (for self-signed certificates):
```bash
python aap_org_inspector.py "My Organization" \
  --url https://aap.example.com \
  --no-verify-ssl
```

Export results to JSON:
```bash
python aap_org_inspector.py "My Organization" \
  --url https://aap.example.com \
  --export results.json
```

### Help

View all available options:
```bash
python aap_org_inspector.py --help
```

## Output

The script displays:

1. **Basic Organization Information**:
   - ID, name, description
   - Creation and modification dates
   - Max hosts and environment settings

2. **Dependencies & Related Resources**:
   - Teams
   - Users
   - Projects
   - Inventories
   - Job Templates
   - Workflow Job Templates
   - Credentials
   - Notification Templates
   - Instance Groups
   - Applications
   - And more...

3. **Cross-Organization Dependencies**:
   - Identifies resources that belong to other organizations

## Example Output

```
================================================================================
ORGANIZATION DETAILS: My Organization
================================================================================

Basic Information:
--------------------------------------------------------------------------------
  id............................... 5
  name............................. My Organization
  description...................... Production organization
  created.......................... 2024-01-15T10:30:00.000000Z
  modified......................... 2024-11-01T14:22:00.000000Z
  max_hosts........................ 100

DEPENDENCIES & RELATED RESOURCES:
--------------------------------------------------------------------------------

Teams:
  Count: 3
    - [12] Development Team
    - [13] Operations Team
    - [14] Security Team

Projects:
  Count: 8
    - [45] Web Application Deployment
    - [46] Database Management
    - [47] Infrastructure as Code
    ... and 5 more

================================================================================
Inspection complete!
================================================================================
```

## Security Notes

- The script prompts for credentials by default (secure)
- Use `--username` and `--password` flags only in secure environments
- Consider using `--no-verify-ssl` only for testing with self-signed certificates
- Credentials are not stored or logged

## API Compatibility

This script is designed for Ansible Automation Platform API version 2.3. It should work with:
- AAP 2.3 and later
- Ansible Tower 3.8+ (with potential minor adjustments)

## Troubleshooting

**SSL Certificate Errors**: Use `--no-verify-ssl` for self-signed certificates

**Authentication Errors**: Verify your credentials and permissions

**Organization Not Found**: Check the organization name spelling or try using the organization ID

**Connection Refused**: Ensure the AAP URL is correct and accessible from your network

## License

This script is provided as-is for use with Ansible Automation Platform.

