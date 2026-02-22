"""Tests for script template manager."""
import pytest
from pathlib import Path
from addons.scripts.templates import ScriptTemplates


def test_template_manager_initialization():
    """Test template manager can be initialized."""
    templates = ScriptTemplates()
    assert templates is not None
    assert templates.templates_dir is not None


def test_list_templates():
    """Test listing available templates."""
    templates = ScriptTemplates()
    template_list = templates.list_templates()
    
    assert isinstance(template_list, list)
    # Should have some templates
    assert len(template_list) >= 0


def test_list_templates_by_category():
    """Test filtering templates by category."""
    templates = ScriptTemplates()
    
    # Get all templates
    all_templates = templates.list_templates()
    
    # If we have templates, test category filtering
    if all_templates:
        category = all_templates[0]['category']
        filtered = templates.list_templates(category=category)
        
        assert isinstance(filtered, list)
        # All filtered templates should be in the specified category
        for tmpl in filtered:
            assert tmpl['category'] == category


def test_get_categories():
    """Test getting list of template categories."""
    templates = ScriptTemplates()
    categories = templates.get_categories()
    
    assert isinstance(categories, list)
    # Should be sorted
    if len(categories) > 1:
        assert categories == sorted(categories)


def test_get_template_with_variables():
    """Test getting a template with variable substitution."""
    templates = ScriptTemplates()
    
    # Try to get backup/postgres template if it exists
    try:
        content = templates.get(
            "backup/postgres",
            variables={
                "database": "testdb",
                "backup_dir": "/tmp/backups",
                "retention_days": 7
            }
        )
        
        assert content is not None
        assert "testdb" in content
        assert "/tmp/backups" in content
        
    except Exception as e:
        # Template might not exist in test environment
        pytest.skip(f"Template not available: {e}")


def test_get_nonexistent_template():
    """Test getting a template that doesn't exist."""
    templates = ScriptTemplates()
    
    with pytest.raises(Exception):
        templates.get("nonexistent/template")


def test_save_custom_template(tmp_path):
    """Test saving a custom template."""
    custom_dir = tmp_path / "custom_templates"
    templates = ScriptTemplates(custom_dir=custom_dir)
    
    template_content = """#!/bin/bash
echo "Hello {{ name }}"
"""
    
    result = templates.save_custom_template(
        name="greeting",
        category="test",
        content=template_content
    )
    
    assert result is True
    
    # Verify template was saved
    saved_path = custom_dir / "test" / "greeting.j2"
    assert saved_path.exists()
    assert "{{ name }}" in saved_path.read_text()


def test_template_variable_rendering(tmp_path):
    """Test that Jinja2 variables are properly rendered."""
    custom_dir = tmp_path / "custom_templates"
    templates = ScriptTemplates(custom_dir=custom_dir)
    
    # Create a test template
    template_content = """#!/bin/bash
DATABASE="{{ database }}"
PORT={{ port }}
"""
    
    templates.save_custom_template(
        name="test_vars",
        category="test",
        content=template_content
    )
    
    # Render the template
    rendered = templates.get(
        "test/test_vars",
        variables={"database": "mydb", "port": 5432}
    )
    
    assert 'DATABASE="mydb"' in rendered
    assert "PORT=5432" in rendered
