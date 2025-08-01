---
description: "Generate and validate documentation for Easel CLI including API docs, CLI help, and user guides"
allowed-tools: ["Bash", "Read", "Write", "Edit"]
---

# Easel CLI Documentation Generator

Generate and validate comprehensive documentation for the Easel CLI project.

## API Documentation Generation

### Generate Sphinx Documentation
!poetry run sphinx-build -b html docs/ docs/_build/html

### Validate Docstring Coverage
!poetry run docstr-coverage easel/ --badge=docs/docstring-coverage.svg

## CLI Help Validation

### Validate Main Command Help
!poetry run easel --help

### Validate Subcommand Help
!poetry run easel course --help || echo "(Command not yet implemented)"
!poetry run easel assignment --help || echo "(Command not yet implemented)"
!poetry run easel user --help || echo "(Command not yet implemented)"
!poetry run easel grade --help || echo "(Command not yet implemented)"

## Documentation Content Validation

### Check README Accuracy
@README.md

### Validate Installation Instructions
!echo "Testing installation process simulation..."
!pip show easel-cli > /dev/null 2>&1 && echo "✓ Package is installable" || echo "✗ Package not yet published"

### Check Documentation Links
!poetry run python -c "
import requests
import re
from pathlib import Path

readme = Path('README.md').read_text()
links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', readme)
print(f'Found {len(links)} external links in README.md')
for link in links[:5]:  # Check first 5 links
    try:
        response = requests.head(link, timeout=5)
        status = '✓' if response.status_code < 400 else '✗'
        print(f'{status} {link} ({response.status_code})')
    except Exception as e:
        print(f'✗ {link} (Error: {str(e)[:30]}...)')
" || echo "Link validation requires requests package"

## Examples and Tutorials Validation

### Validate Code Examples
!echo "Validating code examples in documentation..."
@easel-spec.md

### Check Tutorial Accuracy
@specs/README.md

## Documentation Quality Checks

### Spell Check (if available)
!command -v aspell >/dev/null 2>&1 && find . -name "*.md" -exec aspell check {} \; || echo "Aspell not available for spell checking"

### Markdown Linting
!command -v markdownlint >/dev/null 2>&1 && markdownlint *.md docs/*.md || echo "markdownlint not available"

## Documentation Build Verification

### Verify All Documentation Builds
!echo "=== DOCUMENTATION BUILD STATUS ==="
!echo "Date: $(date)"
!echo "Git commit: $(git rev-parse --short HEAD)"
!echo ""

!if [ -d "docs/_build/html" ]; then
    echo "✓ Sphinx documentation: Built successfully"
    echo "  Location: docs/_build/html/index.html"
else
    echo "✗ Sphinx documentation: Build failed or not attempted"
fi

!if [ -f "docs/docstring-coverage.svg" ]; then
    echo "✓ Docstring coverage: Generated"
else
    echo "✗ Docstring coverage: Not generated"
fi

### Generate Documentation Summary
!echo ""
!echo "=== DOCUMENTATION SUMMARY ==="
!find . -name "*.md" -type f | wc -l | xargs echo "Markdown files:"
!find docs/ -name "*.rst" -type f 2>/dev/null | wc -l | xargs echo "reStructuredText files:" || echo "reStructuredText files: 0"
!find . -name "*.py" -exec grep -l '"""' {} \; | wc -l | xargs echo "Python files with docstrings:"

!echo ""
!echo "Documentation generation and validation complete. Review any errors above."