# Easel CLI

A powerful Python CLI tool for Canvas LMS API access, providing read-only operations with flexible output formatting and robust error handling.

## Features

### Milestone 3: Analytics, Bulk Download, Grade Export

Easel provides comprehensive data access and workflow support for Canvas LMS:

- **Course Operations**: List, show details, explore course modules
- **Assignment Operations**: Browse assignments, review submissions
- **User Operations**: View profiles, course enrollments, rosters
- **Analytics**: CLI analytics and reporting for Canvas data
- **Bulk Download**: Download artifacts and course content in bulk
- **Grade Export**: Export assignment grades in multiple formats
- **Multiple Output Formats**: Table, JSON, CSV, YAML support
- **Transparent Pagination**: Automatically handles large datasets
- **Robust Error Handling**: Clear, actionable error messages

## Installation

```bash
pip install easel
```

## Quick Start

```bash
# Initialize configuration with Canvas credentials
easel init

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

**Important:** Global options (e.g., `--format`/`-f`, `--verbose`/`-v`, `--config`/`-C`) must be specified immediately after `easel` and before the subcommand. Most options support both long and short flags. For example: use `-I` for `--include`, `-c` for `--columns`, `-s` for `--status`, `-f` for `--format`, etc. Example: `easel -f csv assignment submissions ...`

**Note:** Not all subcommands support `--format` or `--include`. See command-specific help (`easel <subcommand> --help`) for details and supported options.

All commands support these global options:

- `--format`: Output format (`table`, `json`, `csv`, `yaml`) - default: `table`
- `--verbose`: Enable verbose output for debugging
- `--config`: Path to custom configuration file

### Grade Management Commands

#### `easel grade export <course-id>`

Export grades for a course with multiple output formats and filtering options.

```bash
# Export all grades to CSV (Excel-compatible)
easel grade export 12345 --format csv --output grades.csv

# Export grades filtered by assignment group
# You can now filter by assignment group name (case-insensitive substring match):
easel grade export 12345 --assignment-group "Homework" --format csv

# Export all grades to CSV (Excel-compatible)
easel grade export 12345 --format csv

# Export specific columns only
# NOTE: --include-columns is currently broken (known bug)
# easel grade export 12345 --include-columns "student_name,assignment_name,score" (not supported)
easel grade export 12345 --format csv
```

#### `easel grade analytics <course-id>`

Generate comprehensive grade analytics and insights.

```bash
# Basic grade analytics
easel grade analytics 12345

# Export raw analytics data
easel grade analytics 12345 --export-raw --format json
```

**Example Analytics Output:**
```
Course: CS101 - Introduction to Python

Grade Statistics:
  Class Average: 82.3%
  Class Median: 81.5%
  Standard Deviation: 12.8

Grade Distribution:
  A (90-100%): 12 students (26.7%)
  B (80-89%): 18 students (40.0%)
  C (70-79%): 10 students (22.2%)
  D (60-69%): 3 students (6.7%)
  F (0-59%): 2 students (4.4%)

Most Difficult Assignment: Final Project (avg: 68.2%)
Easiest Assignment: Quiz 3 (avg: 91.5%)

Student Insights:
  At-Risk Students: 5 (grades below 70%)
  Improving Students: 8 (showing upward trend)
```

### Canvas Page Management Commands

#### `easel page list <course-id>`

List all Canvas pages for a course.

```bash
# List all pages
easel page list 12345

# List with specific columns
easel page list 12345 --include-columns "title,published,updated_at"

# Export to CSV
easel page list 12345 --format csv --output pages.csv
```

#### `easel page show <course-id> <page-id>`

Display full content of a specific page by ID.

```bash
# Show page content
easel page show 12345 67890

# Output as JSON
easel page show 12345 67890 --format json
```

#### `easel page info <course-id> <page-slug>`

Get metadata for a page using its URL slug.

```bash
# Get page metadata
easel page info 12345 "course-syllabus"

# Export metadata as YAML
easel page info 12345 "course-syllabus" --format yaml
```

#### `easel page export <course-id> <page-slug>`

Export page content to HTML or Markdown.

```bash
# Export single page to Markdown
easel page export 12345 "course-syllabus" --format markdown --output syllabus.md

# Export all pages in a course
easel page export 12345 --all --format html --output-dir ./exports/pages/
```

### Content Discovery Commands

#### `easel content list <course-id>`

Create comprehensive content inventory for a course.

```bash
# List all content types
# NOTE: easel content list may return HTTP 404 for some courses (known bug)
easel content list 12345

# Filter by content type
# NOTE: easel content list may return HTTP 404 for some courses (known bug)
easel content list 12345 --content-type files

# Show only published content
# NOTE: easel content list may return HTTP 404 for some courses (known bug)
easel content list 12345 --published-only

# Filter by module
# NOTE: easel content list may return HTTP 404 for some courses (known bug)
easel content list 12345 --module-filter "Week 1"
```

#### `easel content analytics <course-id>`

Generate content usage statistics and accessibility analysis.

```bash
# Basic content analytics
easel content analytics 12345

# Include detailed file analysis
easel content analytics 12345 --include-files --format json
```

**Example Content Analytics Output:**
```
Course: CS101 - Introduction to Python

Content Summary:
  Files: 245 (1.2 GB)
  Pages: 15
  Assignments: 12
  Discussions: 8
  Modules: 16

File Type Distribution:
  application/pdf: 89 files (456 MB)
  image/png: 67 files (234 MB)
  text/plain: 45 files (12 MB)

Accessibility Analysis:
  Large Files (>10MB): 5 (89 MB)
  Empty Pages: 2
  Empty Assignments: 0
```

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
easel --format json course list
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
easel --format yaml course show 12345
```

#### `easel course modules <course-id>`

List modules for a specific course.

```bash
# List course modules
easel course modules 12345

# Include module items
easel course modules 12345 --include items

# Export to CSV
easel --format csv course modules 12345
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
easel --format csv assignment submissions 12345 67890 --status graded
```

### User Commands

#### `easel user profile`

Show current user profile information.

```bash
# View your profile
easel user profile

# Output as JSON
# NOTE: --format is not supported for user profile
# easel user profile --format json (not supported)
easel user profile
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
# NOTE: --include is not supported for user roster (known bug)
# easel user roster 12345 --include enrollments (not supported)
easel user roster 12345

# Export student list to CSV
# You can use --format for CSV, JSON, YAML, or table output:
easel --format csv user roster 12345 --role student

easel --format json user roster 12345 --role teacher

easel user roster 12345 --role student
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
easel init
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
easel --format csv  course list --include total_students > enrollment_data.csv

# Get assignment submission statistics
easel --format json assignment list 12345 --include needs_grading_count | jq '.[] | {name, needs_grading_count}'

# Export student roster for attendance tracking
easel --format csv user roster 12345 --role student  > class_roster.csv
```

### Course Management

```bash
# Check assignment due dates across courses
for course_id in $(easel course list --format json | jq -r '.[].id'); do
  echo "Course $course_id assignments:"
  easel --format table assignment list $course_id
done

# Generate course summary report
easel --format yaml course show 12345 --include syllabus_body,term > course_summary.yaml
```

### Grading Workflows

```bash
# Check submissions that need grading
easel --format table assignment submissions 12345 67890 --status submitted

# Export graded submissions for record keeping
easel --format csv assignment submissions 12345 67890 --status graded --include user > graded_submissions.csv
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Verify your connection
   easel doctor

   # Re-run setup if needed
   easel init
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
