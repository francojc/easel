# Easel CLI Commands Reference

Comprehensive reference for all Easel CLI commands with examples and use cases.

## Global Options

All commands support these global options:

- `--format {table,json,csv,yaml}`: Output format (default: table)
- `--verbose`: Enable verbose output for debugging
- `--config PATH`: Path to custom configuration file
- `--help`: Show command help

## Command Categories

### Configuration Commands

#### `easel config init`

Interactive configuration setup wizard.

```bash
# Run setup wizard
easel config init
```

**Prompts for:**
- Canvas instance URL
- API token
- Default output format preferences

#### `easel doctor`

Validate configuration and test Canvas API connection.

```bash
# Basic health check
easel doctor

# Verbose output for troubleshooting
easel doctor --verbose
```

**Checks:**
- Configuration file existence and validity
- Canvas URL accessibility
- API token authentication
- Network connectivity

### Course Commands

#### `easel course list`

List courses for the current user.

**Syntax:**
```bash
easel course list [OPTIONS]
```

**Options:**
- `--active`: Show only active courses
- `--include FIELD`: Additional data to include (can be used multiple times)

**Examples:**
```bash
# List all courses
easel course list

# Active courses only
easel course list --active

# Include student counts
easel course list --include total_students

# Multiple includes
easel course list --include total_students --include term

# JSON output for scripting
easel course list --format json

# CSV export
easel course list --format csv > my_courses.csv
```

**Available Include Fields:**
- `total_students`: Total enrolled students
- `teachers`: Course teachers
- `term`: Academic term information
- `course_progress`: Progress information
- `sections`: Course sections
- `storage_quota_mb`: Storage quota

#### `easel course show <course-id>`

Show detailed information for a specific course.

**Syntax:**
```bash
easel course show COURSE_ID [OPTIONS]
```

**Options:**
- `--include FIELD`: Additional data to include

**Examples:**
```bash
# Basic course details
easel course show 12345

# Include syllabus content
easel course show 12345 --include syllabus_body

# Include multiple fields
easel course show 12345 --include syllabus_body --include term

# YAML output for readability
easel course show 12345 --format yaml
```

**Available Include Fields:**
- `syllabus_body`: Course syllabus content
- `term`: Academic term details
- `course_progress`: Progress information
- `teachers`: Instructor information
- `total_students`: Enrollment count

#### `easel course modules <course-id>`

List modules for a specific course.

**Syntax:**
```bash
easel course modules COURSE_ID [OPTIONS]
```

**Options:**
- `--include FIELD`: Additional data to include

**Examples:**
```bash
# List course modules
easel course modules 12345

# Include module items
easel course modules 12345 --include items

# Export module structure
easel course modules 12345 --format json > course_structure.json
```

**Available Include Fields:**
- `items`: Module items and content
- `content_details`: Detailed content information

### Assignment Commands

#### `easel assignment list <course-id>`

List assignments for a course.

**Syntax:**
```bash
easel assignment list COURSE_ID [OPTIONS]
```

**Options:**
- `--include FIELD`: Additional data to include

**Examples:**
```bash
# List all assignments
easel assignment list 12345

# Include submission information
easel assignment list 12345 --include submission

# Include grading statistics
easel assignment list 12345 --include needs_grading_count

# Export assignment list
easel assignment list 12345 --format csv > assignments.csv
```

**Available Include Fields:**
- `submission`: Current user's submission
- `needs_grading_count`: Number of submissions needing grading
- `rubric`: Assignment rubric
- `overrides`: Assignment overrides

#### `easel assignment show <course-id> <assignment-id>`

Show detailed information for a specific assignment.

**Syntax:**
```bash
easel assignment show COURSE_ID ASSIGNMENT_ID [OPTIONS]
```

**Options:**
- `--include FIELD`: Additional data to include

**Examples:**
```bash
# Basic assignment details
easel assignment show 12345 67890

# Include submission details
easel assignment show 12345 67890 --include submission

# Include rubric
easel assignment show 12345 67890 --include rubric

# JSON output for processing
easel assignment show 12345 67890 --format json
```

**Available Include Fields:**
- `submission`: Current user's submission
- `rubric`: Assignment rubric
- `overrides`: Assignment overrides

#### `easel assignment submissions <course-id> <assignment-id>`

List submissions for a specific assignment.

**Syntax:**
```bash
easel assignment submissions COURSE_ID ASSIGNMENT_ID [OPTIONS]
```

**Options:**
- `--include FIELD`: Additional data to include
- `--status {submitted,unsubmitted,graded,pending_review}`: Filter by submission status

**Examples:**
```bash
# All submissions
easel assignment submissions 12345 67890

# Only submitted work
easel assignment submissions 12345 67890 --status submitted

# Include user information
easel assignment submissions 12345 67890 --include user

# Graded submissions with user details
easel assignment submissions 12345 67890 --status graded --include user

# Export for grading analysis
easel assignment submissions 12345 67890 --format csv > submissions.csv
```

**Available Include Fields:**
- `user`: Student information
- `submission_history`: Submission history
- `rubric_assessment`: Rubric assessments

### User Commands

#### `easel user profile`

Show current user profile information.

**Syntax:**
```bash
easel user profile [OPTIONS]
```

**Examples:**
```bash
# View your profile
easel user profile

# JSON format for scripting
easel user profile --format json
```

#### `easel user courses`

List courses for the current user with filtering options.

**Syntax:**
```bash
easel user courses [OPTIONS]
```

**Options:**
- `--role {student,teacher,ta,observer,designer}`: Filter by enrollment role
- `--state {active,invited,completed}`: Filter by enrollment state
- `--include FIELD`: Additional data to include

**Examples:**
```bash
# All your courses
easel user courses

# Courses where you're a teacher
easel user courses --role teacher

# Active enrollments only
easel user courses --state active

# Include term information
easel user courses --include term

# Teaching assignments this semester
easel user courses --role teacher --state active --format table
```

**Available Include Fields:**
- `total_students`: Student count per course
- `term`: Academic term information
- `teachers`: Course instructors

#### `easel user roster <course-id>`

List users enrolled in a specific course.

**Syntax:**
```bash
easel user roster COURSE_ID [OPTIONS]
```

**Options:**
- `--role {student,teacher,ta,observer,designer}`: Filter by enrollment role
- `--include FIELD`: Additional data to include

**Examples:**
```bash
# All course participants
easel user roster 12345

# Students only
easel user roster 12345 --role student

# Include enrollment details
easel user roster 12345 --include enrollments

# Export class list
easel user roster 12345 --role student --format csv > class_roster.csv

# Teaching team
easel user roster 12345 --role teacher
```

**Available Include Fields:**
- `enrollments`: Enrollment details
- `avatar_url`: User profile pictures
- `email`: Email addresses (if permitted)

## Output Format Examples

### Table Format (Default)

Human-readable columnar output:

```
Course ID | Name                    | Code     | Status | Students
----------|-------------------------|----------|--------|----------
12345     | Introduction to Python  | CS101    | Active | 45
12346     | Data Structures         | CS201    | Active | 32
```

### JSON Format

Structured data for scripting:

```json
[
  {
    "id": 12345,
    "name": "Introduction to Python",
    "course_code": "CS101",
    "workflow_state": "available",
    "total_students": 45
  }
]
```

### CSV Format

Comma-separated values for spreadsheets:

```csv
id,name,course_code,workflow_state,total_students
12345,"Introduction to Python",CS101,available,45
12346,"Data Structures",CS201,available,32
```

### YAML Format

Human-readable structured format:

```yaml
- id: 12345
  name: Introduction to Python
  course_code: CS101
  workflow_state: available
  total_students: 45
```

## Advanced Usage Patterns

### Data Pipeline Examples

```bash
# Get course IDs for further processing
course_ids=$(easel course list --format json | jq -r '.[].id')

# Process multiple courses
for course_id in $course_ids; do
  echo "Processing course $course_id"
  easel assignment list $course_id --format csv >> all_assignments.csv
done

# Filter and transform data
easel user roster 12345 --role student --format json | \
  jq '.[] | {name: .name, email: .login_id}' > student_contacts.json
```

### Scripting Integration

```bash
#!/bin/bash
# Grade book export script

COURSE_ID=$1
if [ -z "$COURSE_ID" ]; then
  echo "Usage: $0 <course_id>"
  exit 1
fi

# Create export directory
mkdir -p "exports/course_$COURSE_ID"

# Export course details
easel course show $COURSE_ID --format yaml > "exports/course_$COURSE_ID/course.yaml"

# Export assignment list
easel assignment list $COURSE_ID --format csv > "exports/course_$COURSE_ID/assignments.csv"

# Export student roster
easel user roster $COURSE_ID --role student --format csv > "exports/course_$COURSE_ID/students.csv"

echo "Export completed for course $COURSE_ID"
```

### Error Handling

```bash
# Check command success
if easel doctor; then
  echo "Configuration valid"
else
  echo "Please run: easel config init"
  exit 1
fi

# Handle API errors gracefully
easel course show 99999 2>/dev/null || echo "Course not found or access denied"
```

## Troubleshooting

### Common Issues

1. **Configuration Problems**
   ```bash
   # Validate setup
   easel doctor --verbose

   # Reconfigure if needed
   easel config init
   ```

2. **Permission Errors**
   ```bash
   # Check user permissions
   easel user profile

   # Verify course access
   easel course list
   ```

3. **Network Issues**
   ```bash
   # Test with verbose output
   easel course list --verbose
   ```

### Debug Mode

Use `--verbose` flag for detailed output:

```bash
# See API requests and responses
easel course list --verbose

# Debug configuration issues
easel doctor --verbose
```

## Performance Tips

1. **Use Filters**: Reduce data transfer with specific filters
   ```bash
   easel course list --active  # Instead of all courses
   ```

2. **Limit Includes**: Only request needed additional data
   ```bash
   easel course list --include total_students  # Only when needed
   ```

3. **Appropriate Formats**: Use JSON for processing, table for viewing
   ```bash
   easel course list --format json | jq '.[] | .name'  # Processing
   easel course list --format table  # Human viewing
   ```

4. **Batch Operations**: Process multiple items efficiently
   ```bash
   # Better than individual calls
   easel assignment list $COURSE_ID --format json
   ```
