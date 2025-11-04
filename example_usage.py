#!/usr/bin/env python3
"""
Example usage of the AAP Organization Inspector as a module
"""

from aap_org_inspector import AAPClient, OrganizationInspector


def example_programmatic_usage():
    """Example of using the inspector programmatically"""
    
    # Configuration
    AAP_URL = "https://aap.example.com"
    USERNAME = "admin"
    PASSWORD = "your_password"
    ORG_NAME = "My Organization"
    
    # Create client
    client = AAPClient(
        base_url=AAP_URL,
        username=USERNAME,
        password=PASSWORD,
        verify_ssl=True  # Set to False for self-signed certificates
    )
    
    # Create inspector
    inspector = OrganizationInspector(client)
    
    # Inspect organization
    result = inspector.inspect_organization(ORG_NAME)
    
    # Access the data
    org = result['organization']
    dependencies = result['dependencies']
    
    print(f"\nOrganization '{org['name']}' has {len(dependencies)} dependency types")
    
    # Example: Count total resources
    total_resources = 0
    for dep_type, items in dependencies.items():
        if isinstance(items, list):
            total_resources += len(items)
    
    print(f"Total resources: {total_resources}")
    
    # Example: Export to JSON
    inspector.export_to_json(result, 'org_report.json')


def example_list_all_organizations():
    """Example of listing all organizations"""
    
    AAP_URL = "https://aap.example.com"
    USERNAME = "admin"
    PASSWORD = "your_password"
    
    # Create client
    client = AAPClient(
        base_url=AAP_URL,
        username=USERNAME,
        password=PASSWORD,
        verify_ssl=True
    )
    
    # Get all organizations
    orgs_data = client.get_organizations()
    
    print(f"\nTotal organizations: {orgs_data['count']}")
    print("\nOrganizations:")
    for org in orgs_data['results']:
        print(f"  [{org['id']}] {org['name']}")


if __name__ == '__main__':
    print("This is an example file. Modify the credentials and uncomment the function you want to test.")
    print("\nAvailable examples:")
    print("  1. example_programmatic_usage() - Inspect a single organization")
    print("  2. example_list_all_organizations() - List all organizations")
    
    # Uncomment one of these to run:
    # example_programmatic_usage()
    # example_list_all_organizations()

