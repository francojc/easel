# Easel CLI

A powerful Python CLI tool for Canvas LMS API access, providing read-only operations with flexible output formatting and robust error handling.

## Features

### Milestone 2: Read-Only Commands

Easel provides comprehensive read-only access to Canvas LMS data with:

- **Course Operations**: List, show details, and explore course modules
- **Assignment Operations**: Browse assignments and review submissions
- **User Operations**: View profiles, course enrollments, and rosters
- **Multiple Output Formats**: Table, JSON, CSV, and YAML support
- **Transparent Pagination**: Automatically handles large datasets
- **Robust Error Handling**: Clear, actionable error messages

## Installation

```bash
pip install easel
```

## Quick Start

```bash
# Initialize configuration with Canvas credentials
easel config init

# Validate your setup and connection
easel doctor

# List your courses
easel course list

# Get detailed course information
easel course show 12345

# List assignments for a course
easel assignment list 12345

# View your user profile
easel user profile
```

## Command Reference

### Global Options

All commands support these global options:

- `--format`: Output format (`table`, `json`, `csv`, `yaml`) - default: `table`
- `--verbose`: Enable verbose output for debugging
- `--config`: Path to custom configuration file

### Course Commands

#### `easel course list`

List courses for the current user.

```bash
# List all courses
easel course list

# Show only active courses
easel course list --active

# Include additional data (e.g., student count)
easel course list --include total_students

# Output as JSON
easel course list --format json
```

**Example Output (Table):**

```
Course ID | Name                    | Code     | Status | Students
----------|-------------------------|----------|--------|----------
12345     | Introduction to Python  | CS101    | Active | 45
12346     | Data Structures         | CS201    | Active | 32
```

**Example Output (JSON):**
```json
[
  {
    "id": 12345,
    "name": "Introduction to Python",
    "course_code": "CS101",
    "workflow_state": "available",
    "total_students": 45,
    "start_at": "2024-08-26T00:00:00Z"
  }
]
```

#### `easel course show <course-id>`

Show detailed information for a specific course.

```bash
# Basic course details
easel course show 12345

# Include syllabus and term information
easel course show 12345 --include syllabus_body,term

# Output as YAML for readability
easel course show 12345 --format yaml
```

#### `easel course modules <course-id>`

List modules for a specific course.

```bash
# List course modules
easel course modules 12345

# Include module items
easel course modules 12345 --include items

# Export to CSV
easel course modules 12345 --format csv
```

### Assignment Commands

#### `easel assignment list <course-id>`

List assignments for a course.

```bash
# List all assignments
easel assignment list 12345

# Include submission and grading information
easel assignment list 12345 --include submission,needs_grading_count

# Export as CSV for spreadsheet analysis
easel assignment list 12345 --format csv
```

**Example Output (Table):**
```
Assignment ID | Name              | Due Date            | Points | Status
--------------|-------------------|---------------------|--------|--------
67890         | Homework 1        | 2024-09-15 23:59    | 100    | Published
67891         | Midterm Project   | 2024-10-01 23:59    | 250    | Published
```

#### `easel assignment show <course-id> <assignment-id>`

Show detailed information for a specific assignment.

```bash
# Basic assignment details
easel assignment show 12345 67890

# Include rubric information
easel assignment show 12345 67890 --include rubric

# Output as JSON for scripting
easel assignment show 12345 67890 --format json
```

#### `easel assignment submissions <course-id> <assignment-id>`

List submissions for a specific assignment.

```bash
# List all submissions
easel assignment submissions 12345 67890

# Show only submitted work
easel assignment submissions 12345 67890 --status submitted

# Include user information
easel assignment submissions 12345 67890 --include user

# Export graded submissions to CSV
easel assignment submissions 12345 67890 --status graded --format csv
```

### User Commands

#### `easel user profile`

Show current user profile information.

```bash
# View your profile
easel user profile

# Output as JSON
easel user profile --format json
```

**Example Output (Table):**
```
Field          | Value
---------------|------------------
ID             | 98765
Name           | Dr. Jane Smith
Email          | jane.smith@university.edu
Login ID       | jsmith
```

#### `easel user courses`

List courses for the current user with filtering options.

```bash
# List all your courses
easel user courses

# Show only courses where you're a teacher
easel user courses --role teacher

# Show only active enrollments
easel user courses --state active

# Include term information
easel user courses --include term
```

#### `easel user roster <course-id>`

List users enrolled in a specific course.

```bash
# Show all course participants
easel user roster 12345

# Show only students
easel user roster 12345 --role student

# Include enrollment details
easel user roster 12345 --include enrollments

# Export student list to CSV
easel user roster 12345 --role student --format csv
```

## Output Formats

### Table Format

Human-readable tabular output (default):

```bash
easel course list --format table
```

### JSON Format

Structured data perfect for scripting and integration:

```bash
easel course list --format json
```

### CSV Format

Comma-separated values for spreadsheet analysis:

```bash
easel course list --format csv > courses.csv
```

### YAML Format

Human-readable structured format for configuration:

```bash
easel course show 12345 --format yaml
```

## Configuration

### Initial Setup

```bash
# Interactive setup wizard
easel config init
```

### Manual Configuration

Configuration is stored in `~/.config/easel/config.toml`:

```toml
[canvas]
url = "https://your-school.instructure.com"
api_token = "your_api_token_here"

[output]
default_format = "table"
```

### Environment Variables

You can also use environment variables:

```bash
export CANVAS_URL="https://your-school.instructure.com"
export CANVAS_API_TOKEN="your_token_here"
```

## Examples and Use Cases

### Data Analysis Workflows

```bash
# Export course enrollments for analysis
easel course list --include total_students --format csv > enrollment_data.csv

# Get assignment submission statistics
easel assignment list 12345 --include needs_grading_count --format json | jq '.[] | {name, needs_grading_count}'

# Export student roster for attendance tracking
easel user roster 12345 --role student --format csv > class_roster.csv
```

### Course Management

```bash
# Check assignment due dates across courses
for course_id in $(easel course list --format json | jq -r '.[].id'); do
  echo "Course $course_id assignments:"
  easel assignment list $course_id --format table
done

# Generate course summary report
easel course show 12345 --include syllabus_body,term --format yaml > course_summary.yaml
```

### Grading Workflows

```bash
# Check submissions that need grading
easel assignment submissions 12345 67890 --status submitted --format table

# Export graded submissions for record keeping
easel assignment submissions 12345 67890 --status graded --include user --format csv > graded_submissions.csv
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Verify your connection
   easel doctor
   
   # Re-run setup if needed
   easel config init
   ```

2. **Rate Limiting**
   - Easel automatically handles Canvas API rate limits
   - Use `--verbose` flag to see request details

3. **Large Datasets**
   - Pagination is handled automatically
   - Consider using filters to reduce data size

### Getting Help

```bash
# General help
easel --help

# Command-specific help
easel course --help
easel assignment list --help
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/easel.git
cd easel

# Install dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run type checking
poetry run mypy easel

# Run linting
poetry run ruff check .
poetry run ruff format .

# Install pre-commit hooks
poetry run pre-commit install
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/

# Run with coverage
poetry run pytest --cov=easel
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Architecture

Easel is built with a modular architecture:

- **CLI Layer**: Click-based command interface
- **API Client**: Async Canvas API client with rate limiting
- **Output System**: Pluggable formatters for different output types
- **Configuration**: TOML-based configuration management
- **Error Handling**: Comprehensive error mapping and user feedback

## Documentation

- `specs/`: Detailed specifications and milestones
- `adr/`: Architectural decision records
- `.claude/commands/`: Development workflow documentation

## License

MIT
