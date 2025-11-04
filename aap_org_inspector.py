#!/usr/bin/env python3
"""
Ansible Automation Platform Organization Inspector

This script uses AAP API 2.3 to retrieve organization details and dependencies.
"""

import requests
import json
import sys
import argparse
from urllib.parse import urljoin
from getpass import getpass


class AAPClient:
    """Client for interacting with Ansible Automation Platform API 2.3"""
    
    def __init__(self, base_url, username, password, verify_ssl=True):
        """
        Initialize AAP client
        
        Args:
            base_url: Base URL of AAP instance (e.g., https://aap.example.com)
            username: AAP username
            password: AAP password
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v2/"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl
        self.session.headers.update({
            'Content-Type': 'application/json',
        })
    
    def get(self, endpoint):
        """
        Make GET request to API endpoint
        
        Args:
            endpoint: API endpoint (relative to /api/v2/)
            
        Returns:
            Response JSON data
        """
        url = urljoin(self.api_base, endpoint)
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}", file=sys.stderr)
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}", file=sys.stderr)
            sys.exit(1)
    
    def get_organizations(self):
        """Get all organizations"""
        return self.get('organizations/')
    
    def get_organization_by_name(self, org_name):
        """
        Get organization by name
        
        Args:
            org_name: Name of the organization
            
        Returns:
            Organization data or None if not found
        """
        response = self.get(f'organizations/?name={org_name}')
        results = response.get('results', [])
        if results:
            return results[0]
        return None
    
    def get_organization_by_id(self, org_id):
        """
        Get organization by ID
        
        Args:
            org_id: ID of the organization
            
        Returns:
            Organization data
        """
        return self.get(f'organizations/{org_id}/')
    
    def get_related_data(self, related_url):
        """
        Get data from a related endpoint
        
        Args:
            related_url: Full URL or relative path to related data
            
        Returns:
            Related data
        """
        # If it's a full URL, extract the path after /api/v2/
        if related_url.startswith('http'):
            # Extract path after /api/v2/
            parts = related_url.split('/api/v2/')
            if len(parts) > 1:
                endpoint = parts[1]
            else:
                return None
        else:
            endpoint = related_url.lstrip('/')
        
        return self.get(endpoint)


class OrganizationInspector:
    """Inspector for organization details and dependencies"""
    
    def __init__(self, client):
        """
        Initialize inspector
        
        Args:
            client: AAPClient instance
        """
        self.client = client
    
    def inspect_organization(self, org_identifier):
        """
        Inspect organization and find dependencies
        
        Args:
            org_identifier: Organization name or ID
            
        Returns:
            Dictionary with organization details and dependencies
        """
        # Try to get organization by name first, then by ID
        try:
            org_id = int(org_identifier)
            org = self.client.get_organization_by_id(org_id)
        except ValueError:
            org = self.client.get_organization_by_name(org_identifier)
        
        if not org:
            print(f"Organization '{org_identifier}' not found.", file=sys.stderr)
            sys.exit(1)
        
        print(f"\n{'='*80}")
        print(f"ORGANIZATION DETAILS: {org['name']}")
        print(f"{'='*80}\n")
        
        # Display main organization details
        self._display_org_details(org)
        
        # Find and display dependencies
        dependencies = self._find_dependencies(org)
        
        return {
            'organization': org,
            'dependencies': dependencies
        }
    
    def _display_org_details(self, org):
        """Display organization details"""
        important_fields = [
            'id', 'name', 'description', 'created', 'modified',
            'max_hosts', 'custom_virtualenv', 'default_environment'
        ]
        
        print("Basic Information:")
        print("-" * 80)
        for field in important_fields:
            if field in org:
                value = org[field]
                if value is None or value == '':
                    value = 'N/A'
                print(f"  {field:.<30} {value}")
        print()
    
    def _find_dependencies(self, org):
        """
        Find organization dependencies
        
        Args:
            org: Organization data
            
        Returns:
            Dictionary of dependencies
        """
        dependencies = {}
        
        print("DEPENDENCIES & RELATED RESOURCES:")
        print("-" * 80)
        
        # Check related and summary fields for organizational dependencies
        related_fields = org.get('related', {})
        summary_fields = org.get('summary_fields', {})
        
        # Check for related organizations in various resources
        resource_types = [
            ('teams', 'Teams'),
            ('users', 'Users'),
            ('projects', 'Projects'),
            ('inventories', 'Inventories'),
            ('job_templates', 'Job Templates'),
            ('workflow_job_templates', 'Workflow Job Templates'),
            ('credentials', 'Credentials'),
            ('notification_templates', 'Notification Templates'),
            ('instance_groups', 'Instance Groups'),
            ('applications', 'Applications'),
            ('activity_stream', 'Activity Stream'),
            ('access_list', 'Access List'),
        ]
        
        for field, label in resource_types:
            if field in related_fields:
                print(f"\n{label}:")
                try:
                    data = self.client.get_related_data(related_fields[field])
                    count = data.get('count', 0)
                    print(f"  Count: {count}")
                    
                    if count > 0 and 'results' in data:
                        dependencies[field] = []
                        # Show first few items
                        for item in data['results'][:5]:
                            name = item.get('name', item.get('username', 'N/A'))
                            item_id = item.get('id', 'N/A')
                            print(f"    - [{item_id}] {name}")
                            dependencies[field].append({
                                'id': item_id,
                                'name': name
                            })
                        
                        if count > 5:
                            print(f"    ... and {count - 5} more")
                except Exception as e:
                    print(f"  Error retrieving {label}: {e}")
        
        # Check for galaxy credentials or other org-linked credentials
        if 'credentials' in dependencies:
            print(f"\nChecking credentials for cross-organization dependencies...")
            for cred in dependencies['credentials']:
                try:
                    cred_detail = self.client.get(f"credentials/{cred['id']}/")
                    cred_org_id = cred_detail.get('organization')
                    if cred_org_id and cred_org_id != org['id']:
                        print(f"  ⚠️  Credential '{cred['name']}' belongs to different organization (ID: {cred_org_id})")
                        if 'cross_org_credentials' not in dependencies:
                            dependencies['cross_org_credentials'] = []
                        dependencies['cross_org_credentials'].append({
                            'credential': cred,
                            'organization_id': cred_org_id
                        })
                except Exception as e:
                    print(f"  Error checking credential {cred['id']}: {e}")
        
        print()
        return dependencies
    
    def export_to_json(self, data, filename):
        """
        Export data to JSON file
        
        Args:
            data: Data to export
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nData exported to: {filename}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Inspect Ansible Automation Platform organizations and their dependencies'
    )
    parser.add_argument(
        'organization',
        help='Organization name or ID to inspect'
    )
    parser.add_argument(
        '--url',
        required=True,
        help='AAP base URL (e.g., https://aap.example.com)'
    )
    parser.add_argument(
        '--username',
        help='AAP username (will prompt if not provided)'
    )
    parser.add_argument(
        '--password',
        help='AAP password (will prompt if not provided)'
    )
    parser.add_argument(
        '--no-verify-ssl',
        action='store_true',
        help='Disable SSL certificate verification'
    )
    parser.add_argument(
        '--export',
        help='Export results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Get credentials
    username = args.username or input("AAP Username: ")
    password = args.password or getpass("AAP Password: ")
    
    # Create client
    client = AAPClient(
        base_url=args.url,
        username=username,
        password=password,
        verify_ssl=not args.no_verify_ssl
    )
    
    # Create inspector and inspect organization
    inspector = OrganizationInspector(client)
    result = inspector.inspect_organization(args.organization)
    
    # Export if requested
    if args.export:
        inspector.export_to_json(result, args.export)
    
    print(f"\n{'='*80}")
    print("Inspection complete!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()

