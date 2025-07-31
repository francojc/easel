# Milestone 2: Read-Only Commands

**Goal:** Implement core read-only Canvas operations with consistent output formatting

**Duration:** 3-4 weeks  
**Priority:** High  
**Dependencies:** Milestone 1 (Core Infrastructure)  

## Overview

This milestone builds upon the foundation to deliver the core user-facing functionality. It implements read-only operations for courses, assignments, and users, along with a flexible output formatting system that supports multiple data formats.

## Deliverables

- Course operations (`list`, `show`, `modules`)
- Assignment operations (`list`, `show`, `submissions`)
- User operations (`profile`, `courses`, `roster`)
- Output formatting system (table, JSON, CSV, YAML)
- Comprehensive error handling and user feedback

## Acceptance Criteria

- All commands support `--format` flag with consistent behavior
- Pagination is handled transparently without user intervention
- Error messages are actionable and provide clear next steps
- Commands integrate properly with shell piping and redirection
- Response times under 2 seconds for typical operations

## Detailed Task Breakdown

### Output Formatting System

- [ ] Design formatter interface with pluggable architecture
- [ ] Implement table formatter using rich library
- [ ] Create JSON formatter with proper escaping and structure
- [ ] Add CSV formatter with configurable delimiters
- [ ] Implement YAML formatter for human-readable config-style output
- [ ] Add formatter factory and registration system
- [ ] Create format detection from file extensions for output redirection

### Course Commands

- [ ] Implement `easel course list` with filtering options
- [ ] Add `easel course show <course-id>` for detailed course information
- [ ] Create `easel course modules <course-id>` for module hierarchy
- [ ] Add course search functionality with text matching
- [ ] Implement course filtering by enrollment status and dates
- [ ] Add pagination support for large course lists
- [ ] Create course roster shortcut command

### Assignment Commands

- [ ] Implement `easel assignment list <course-id>` with status filtering
- [ ] Add `easel assignment show <course-id> <assignment-id>` with full details
- [ ] Create `easel assignment submissions <course-id> <assignment-id>` command
- [ ] Add submission filtering by status (submitted, graded, late)
- [ ] Implement date-based filtering for assignment due dates
- [ ] Add assignment group support and filtering
- [ ] Create assignment statistics summary

### User Commands

- [ ] Implement `easel user profile` for current user information
- [ ] Add `easel user courses` to list user's course enrollments
- [ ] Create `easel user roster <course-id>` for course participant lists
- [ ] Add user search within courses
- [ ] Implement enrollment status filtering
- [ ] Add user role filtering (student, teacher, ta, etc.)
- [ ] Create user activity summary commands

### Data Processing & Transformation

- [ ] Create Canvas API response normalizers
- [ ] Implement data field selection and filtering
- [ ] Add computed fields (e.g., days until due, grade percentages)
- [ ] Create data sorting with multiple field support
- [ ] Implement field aliasing for user-friendly column names
- [ ] Add data validation and type conversion

### Pagination & Performance

- [ ] Implement transparent pagination for all list commands
- [ ] Add progress indicators for long-running operations
- [ ] Create configurable page size settings
- [ ] Implement concurrent request handling where appropriate
- [ ] Add request caching for frequently accessed data
- [ ] Create pagination control options (--limit, --offset)

### Error Handling & User Experience

- [ ] Implement Canvas API error mapping to user-friendly messages
- [ ] Add input validation with helpful suggestions
- [ ] Create connection error handling with retry logic
- [ ] Implement graceful degradation for partial API failures
- [ ] Add verbose mode for debugging API interactions
- [ ] Create contextual help for each command

### Testing

- [ ] Create comprehensive test fixtures for Canvas API responses
- [ ] Add unit tests for all formatter implementations
- [ ] Create integration tests for command workflows
- [ ] Add performance tests for large datasets
- [ ] Implement property-based testing for data transformations
- [ ] Create CLI command testing with various input scenarios

### Documentation

- [ ] Create command reference documentation
- [ ] Add output format examples for each command
- [ ] Create filtering and searching guide
- [ ] Document pagination behavior and controls
- [ ] Add troubleshooting guide for common issues
- [ ] Create scripting examples and best practices

## Technical Specifications

### Command Interface Design

```bash
# Course operations
easel course list [--active] [--format json|csv|yaml|table]
easel course show <course-id> [--format json]
easel course modules <course-id> [--format table]

# Assignment operations  
easel assignment list <course-id> [--status published|unpublished] [--format csv]
easel assignment show <course-id> <assignment-id> [--format json]
easel assignment submissions <course-id> <assignment-id> [--status submitted|graded]

# User operations
easel user profile [--format json]
easel user courses [--role student|teacher] [--format table]
easel user roster <course-id> [--role all|student|teacher] [--format csv]
```

### Output Format Examples

**Table Format:**
```
Course ID | Name                    | Code     | Status | Students
----------|-------------------------|----------|--------|----------
12345     | Introduction to Python  | CS101    | Active | 45
12346     | Data Structures         | CS201    | Active | 32
```

**JSON Format:**
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

**CSV Format:**
```csv
id,name,course_code,workflow_state,total_students,start_at
12345,"Introduction to Python",CS101,available,45,2024-08-26T00:00:00Z
```

### Formatter Architecture

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class OutputFormatter(ABC):
    @abstractmethod
    def format(self, data: List[Dict[str, Any]]) -> str:
        pass

class TableFormatter(OutputFormatter):
    def format(self, data: List[Dict[str, Any]]) -> str:
        # Rich table implementation
        pass

class FormatterFactory:
    @staticmethod
    def get_formatter(format_type: str) -> OutputFormatter:
        # Factory pattern implementation
        pass
```

## Success Metrics

- All commands execute successfully with real Canvas data
- Output formats are consistent and properly structured
- Error handling provides actionable feedback
- Commands complete within performance targets (<2s typical)
- Test coverage remains >80% for all new code

## Risk Mitigation

- **Canvas API rate limits:** Implement intelligent request batching
- **Large datasets:** Add streaming and pagination controls
- **Data inconsistencies:** Robust error handling and validation
- **Performance issues:** Caching and concurrent request strategies

## Integration Points

- **Configuration system:** Commands use centralized config management
- **Authentication:** Leverages token management from Milestone 1
- **Logging:** Integrates with established logging infrastructure
- **Error handling:** Uses standardized error response patterns

## Follow-up Tasks

Items deferred to later milestones:

- Data export functionality (Milestone 3)
- Automation scripting features (Milestone 4)
- Caching optimization (Milestone 5)
- Advanced filtering with query language (Future enhancement)