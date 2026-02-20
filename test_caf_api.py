#!/usr/bin/env python3
"""
Test script for CAF Generator functionality
"""
import requests
import json

def test_web_ide_endpoint():
    """Test if the web_ide endpoint is accessible"""
    try:
        response = requests.get('http://localhost:8080/web_ide')
        if response.status_code == 200:
            print("✓ Web IDE endpoint accessible")
            return response.text
        else:
            print(f"✗ Web IDE endpoint failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Web IDE endpoint error: {e}")
        return None

def test_javascript_functions(html_content):
    """Test if the JavaScript functions are present in the HTML"""
    functions_to_check = [
        'generateCAF',
        'switchFileTab',
        'generateVariablesTemplate',
        'generateOutputsTemplate'
    ]

    print("\nJavaScript Function Check:")
    for func in functions_to_check:
        if f'function {func}' in html_content:
            print(f"✓ {func} function found")
        else:
            print(f"✗ {func} function NOT found")

def test_template_generation():
    """Test template generation by simulating JavaScript calls"""
    print("\nTemplate Generation Test:")

    # Since we can't directly execute JavaScript, let's check if the templates
    # are properly structured by looking for key indicators

    try:
        response = requests.get('http://localhost:8080/web_ide')
        html = response.text

        # Check for varTemplates object
        if 'varTemplates' in html:
            print("✓ varTemplates object found")
        else:
            print("✗ varTemplates object NOT found")

        # Check for specific module templates
        modules = ['management-groups', 'vnet', 'storage-account', 'keyvault', 'vm', 'aks']
        for module in modules:
            if f"'{module}':" in html:
                print(f"✓ {module} template found")
            else:
                print(f"✗ {module} template NOT found")

        # Check for proper template structure
        if '"${prefix}"' in html and '"${environment}"' in html and '"${location}"' in html:
            print("✓ Template placeholders found")
        else:
            print("✗ Template placeholders NOT found")

    except Exception as e:
        print(f"✗ Template test error: {e}")

def test_server_health():
    """Test basic server health"""
    try:
        response = requests.get('http://localhost:8080')
        if response.status_code == 200:
            print("✓ Main server endpoint accessible")
        else:
            print(f"✗ Main server endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Server health check error: {e}")

def main():
    print("CAF Generator API Test Suite")
    print("=" * 40)

    # Test server health
    test_server_health()

    # Test web IDE endpoint
    html_content = test_web_ide_endpoint()

    if html_content:
        # Test JavaScript functions
        test_javascript_functions(html_content)

        # Test template generation
        test_template_generation()

    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == '__main__':
    main()

def test_web_ide_endpoint():
    """Test if the web_ide endpoint is accessible"""
    try:
        response = requests.get('http://localhost:8080/web_ide')
        if response.status_code == 200:
            print("✓ Web IDE endpoint accessible")
            return response.text
        else:
            print(f"✗ Web IDE endpoint failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Web IDE endpoint error: {e}")
        return None

def test_javascript_functions(html_content):
    """Test if the JavaScript functions are present in the HTML"""
    functions_to_check = [
        'generateCAF',
        'switchFileTab',
        'generateVariablesTemplate',
        'generateOutputsTemplate'
    ]

    print("\nJavaScript Function Check:")
    for func in functions_to_check:
        if f'function {func}' in html_content:
            print(f"✓ {func} function found")
        else:
            print(f"✗ {func} function NOT found")

def test_template_generation():
    """Test template generation by simulating JavaScript calls"""
    print("\nTemplate Generation Test:")

    # Since we can't directly execute JavaScript, let's check if the templates
    # are properly structured by looking for key indicators

    try:
        response = requests.get('http://localhost:8080/web_ide')
        html = response.text

        # Check for varTemplates object
        if 'varTemplates' in html:
            print("✓ varTemplates object found")
        else:
            print("✗ varTemplates object NOT found")

        # Check for specific module templates
        modules = ['management-groups', 'vnet', 'storage-account', 'keyvault', 'vm', 'aks']
        for module in modules:
            if f"'{module}':" in html:
                print(f"✓ {module} template found")
            else:
                print(f"✗ {module} template NOT found")

        # Check for proper template structure
        if '"${prefix}"' in html and '"${environment}"' in html and '"${location}"' in html:
            print("✓ Template placeholders found")
        else:
            print("✗ Template placeholders NOT found")

    except Exception as e:
        print(f"✗ Template test error: {e}")

def test_server_health():
    """Test basic server health"""
    try:
        response = requests.get('http://localhost:8080')
        if response.status_code == 200:
            print("✓ Main server endpoint accessible")
        else:
            print(f"✗ Main server endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Server health check error: {e}")

def main():
    print("CAF Generator API Test Suite")
    print("=" * 40)

    # Test server health
    test_server_health()

    # Test web IDE endpoint
    html_content = test_web_ide_endpoint()

    if html_content:
        # Test JavaScript functions
        test_javascript_functions(html_content)

        # Test template generation
        test_template_generation()

    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == '__main__':
    main()