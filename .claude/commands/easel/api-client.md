# Easel API Client Documentation

The Easel API client provides programmatic access to Canvas LMS data with built-in rate limiting, error handling, and async support.

## Overview

The `CanvasClient` is an async HTTP client that wraps the Canvas REST API with:

- **Rate Limiting**: Automatic request throttling to respect Canvas API limits
- **Error Handling**: Specific exceptions for different error types
- **Pagination**: Transparent handling of paginated responses
- **Retry Logic**: Automatic retries with exponential backoff
- **Type Safety**: Pydantic models for all API responses

## Basic Usage

### Client Initialization

```python
from easel.api.auth import CanvasAuth
from easel.api.client import CanvasClient

# Create authentication
auth = CanvasAuth("your_api_token")

# Initialize client
async with CanvasClient("https://your-school.instructure.com", auth) as client:
    # Use client for API calls
    user = await client.verify_connection()
    print(f"Connected as: {user.name}")
```

### Configuration Options

```python
client = CanvasClient(
    base_url="https://your-school.instructure.com",
    auth=auth,
    rate_limit=10.0,      # Max 10 requests per second
    timeout=30.0,         # 30 second timeout
    max_retries=3,        # Retry failed requests 3 times
    per_page=100          # Default page size
)
```

## API Methods

### User Operations

#### `verify_connection()`

Test API connection and get current user information.

```python
async with CanvasClient(url, auth) as client:
    user = await client.verify_connection()
    print(f"User ID: {user.id}")
    print(f"Name: {user.name}")
    print(f"Email: {user.login_id}")
```

### Course Operations

#### `get_courses()`

Get courses for the current user with optional filtering.

```python
async with CanvasClient(url, auth) as client:
    # Basic course list
    response = await client.get_courses()
    courses = response.data
    
    # Filter by active courses only
    response = await client.get_courses(state=["available"])
    
    # Include additional data
    response = await client.get_courses(
        include=["total_students", "term"],
        state=["available", "completed"]
    )
    
    # Custom page size
    response = await client.get_courses(per_page=50)
```

**Available Include Options:**
- `total_students`: Total enrolled students
- `teachers`: Course instructors
- `term`: Academic term information
- `course_progress`: Course progress
- `sections`: Course sections
- `storage_quota_mb`: Storage quota

#### `get_course(course_id, include=None)`

Get detailed information for a specific course.

```python
async with CanvasClient(url, auth) as client:
    # Basic course details
    course = await client.get_course(12345)
    
    # Include syllabus and term
    course = await client.get_course(
        12345, 
        include=["syllabus_body", "term"]
    )
    
    print(f"Course: {course.name}")
    print(f"Code: {course.course_code}")
    print(f"Students: {course.total_students}")
```

### Assignment Operations

#### `get_assignments(course_id, include=None, per_page=None)`

Get assignments for a course.

```python
async with CanvasClient(url, auth) as client:
    # List assignments
    response = await client.get_assignments(12345)
    assignments = response.data
    
    # Include submission data
    response = await client.get_assignments(
        12345,
        include=["submission", "needs_grading_count"]
    )
    
    for assignment in response.data:
        print(f"{assignment.name}: {assignment.points_possible} points")
```

**Available Include Options:**
- `submission`: Current user's submission
- `needs_grading_count`: Submissions needing grading
- `rubric`: Assignment rubric
- `overrides`: Assignment overrides

#### `get_assignment(course_id, assignment_id, include=None)`

Get detailed information for a specific assignment.

```python
async with CanvasClient(url, auth) as client:
    assignment = await client.get_assignment(
        12345, 67890,
        include=["rubric", "submission"]
    )
    
    print(f"Assignment: {assignment.name}")
    print(f"Due: {assignment.due_at}")
    print(f"Points: {assignment.points_possible}")
```

#### `get_submissions(course_id, assignment_id, include=None, per_page=None)`

Get submissions for an assignment.

```python
async with CanvasClient(url, auth) as client:
    response = await client.get_submissions(
        12345, 67890,
        include=["user", "submission_history"]
    )
    
    for submission in response.data:
        if submission.user:
            print(f"Student: {submission.user.name}")
            print(f"Score: {submission.score}")
            print(f"Submitted: {submission.submitted_at}")
```

**Available Include Options:**
- `user`: Student information
- `submission_history`: Submission history
- `rubric_assessment`: Rubric assessments

### User Operations

#### `get_users(course_id, enrollment_type=None, per_page=None)`

Get users enrolled in a course.

```python
async with CanvasClient(url, auth) as client:
    # All users
    response = await client.get_users(12345)
    
    # Students only
    response = await client.get_users(
        12345,
        enrollment_type=["StudentEnrollment"]
    )
    
    # Teachers and TAs
    response = await client.get_users(
        12345,
        enrollment_type=["TeacherEnrollment", "TaEnrollment"]
    )
    
    for user in response.data:
        print(f"{user.name} ({user.login_id})")
```

**Enrollment Types:**
- `StudentEnrollment`: Students
- `TeacherEnrollment`: Teachers
- `TaEnrollment`: Teaching assistants
- `ObserverEnrollment`: Observers
- `DesignerEnrollment`: Course designers

### Module Operations

#### `get_modules(course_id, include=None, per_page=None)`

Get modules for a course.

```python
async with CanvasClient(url, auth) as client:
    # Basic module list
    response = await client.get_modules(12345)
    
    # Include module items
    response = await client.get_modules(
        12345,
        include=["items"]
    )
    
    for module in response.data:
        print(f"Module: {module.name}")
        if module.items:
            for item in module.items:
                print(f"  - {item.title}")
```

## Pagination Handling

All list methods return `PaginatedResponse` objects that support automatic pagination:

```python
async with CanvasClient(url, auth) as client:
    response = await client.get_courses()
    
    # Get first page of data
    courses = response.data
    
    # Check for more pages
    if response.has_next_page:
        print(f"More pages available: {response.next_page_url}")
    
    # Manual pagination handling
    all_courses = []
    while response.has_next_page:
        # Get next page
        next_response = await client._make_request("GET", url=response.next_page_url)
        next_data = next_response.json()
        next_courses = [Course(**course_data) for course_data in next_data]
        all_courses.extend(next_courses)
        
        # Update pagination info
        from easel.api.pagination import PaginatedResponse
        response = PaginatedResponse.from_response(next_response, next_courses)
```

### PaginatedResponse Properties

```python
response = await client.get_courses()

# Data access
courses = response.data  # Current page data
count = len(response.data)  # Items on current page

# Pagination info
has_more = response.has_next_page  # Boolean
next_url = response.next_page_url  # URL for next page
prev_url = response.prev_page_url  # URL for previous page
first_url = response.first_page_url  # URL for first page
last_url = response.last_page_url  # URL for last page
```

## Error Handling

The client provides specific exception types for different error conditions:

```python
from easel.api.exceptions import (
    CanvasAPIError,
    CanvasAuthError,
    CanvasNotFoundError,
    CanvasRateLimitError,
    CanvasServerError,
    CanvasTimeoutError,
    CanvasValidationError,
    CanvasPermissionError,
)

async with CanvasClient(url, auth) as client:
    try:
        course = await client.get_course(12345)
    except CanvasAuthError:
        print("Invalid API token")
    except CanvasNotFoundError:
        print("Course not found or access denied")
    except CanvasRateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after} seconds")
    except CanvasPermissionError:
        print("Insufficient permissions")
    except CanvasValidationError as e:
        print(f"Invalid request: {e}")
    except CanvasServerError:
        print("Canvas server error")
    except CanvasTimeoutError:
        print("Request timed out")
    except CanvasAPIError as e:
        print(f"API error: {e}")
```

## Rate Limiting

The client automatically handles rate limiting:

```python
from easel.api.rate_limit import RateLimiter

# Custom rate limiter
rate_limiter = RateLimiter(rate=5.0)  # 5 requests per second

client = CanvasClient(
    url, auth,
    rate_limit=5.0  # Will create internal rate limiter
)

# Rate limiter automatically delays requests to stay within limits
async with client:
    # These calls will be automatically throttled
    for course_id in course_ids:
        assignments = await client.get_assignments(course_id)
```

## Advanced Usage

### Concurrent Requests

For better performance with multiple independent requests:

```python
import asyncio

async def get_course_data(client, course_id):
    """Get comprehensive course data."""
    course_task = client.get_course(course_id, include=["term"])
    assignments_task = client.get_assignments(course_id)
    modules_task = client.get_modules(course_id)
    
    # Run concurrently (still rate limited)
    course, assignments_response, modules_response = await asyncio.gather(
        course_task,
        assignments_task,
        modules_task
    )
    
    return {
        "course": course,
        "assignments": assignments_response.data,
        "modules": modules_response.data
    }

async with CanvasClient(url, auth) as client:
    course_data = await get_course_data(client, 12345)
```

### Custom Request Handling

For direct API access:

```python
async with CanvasClient(url, auth) as client:
    # Direct API call
    response = await client._make_request(
        "GET",
        "courses/12345/announcements",
        params={"per_page": 50}
    )
    
    announcements = response.json()
    
    # Custom error handling
    try:
        response = await client._make_request("GET", "invalid/endpoint")
    except CanvasNotFoundError:
        print("Endpoint not found")
```

### Configuration Integration

Using with Easel configuration system:

```python
from easel.config import ConfigManager
from easel.api.auth import CanvasAuth
from easel.api.client import CanvasClient

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Create authenticated client
auth = CanvasAuth(config.canvas.api_token)

async with CanvasClient(config.canvas.url, auth) as client:
    # Client is ready to use
    user = await client.verify_connection()
    print(f"Connected to {config.canvas.url} as {user.name}")
```

## Data Models

All API responses are parsed into Pydantic models:

### Course Model

```python
class Course(BaseModel):
    id: int
    name: str
    course_code: str
    workflow_state: str
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    total_students: Optional[int] = None
    # ... additional fields
```

### Assignment Model

```python
class Assignment(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    points_possible: Optional[float] = None
    submission_types: List[str] = []
    # ... additional fields
```

### User Model

```python
class User(BaseModel):
    id: int
    name: str
    short_name: str
    login_id: str
    avatar_url: Optional[str] = None
    # ... additional fields
```

## Best Practices

### Context Manager Usage

Always use async context manager for proper resource cleanup:

```python
# Good
async with CanvasClient(url, auth) as client:
    courses = await client.get_courses()

# Bad - may leave connections open
client = CanvasClient(url, auth)
courses = await client.get_courses()
# Missing: await client.close()
```

### Error Handling

Handle specific exceptions for better user experience:

```python
try:
    assignment = await client.get_assignment(course_id, assignment_id)
except CanvasNotFoundError:
    print(f"Assignment {assignment_id} not found in course {course_id}")
except CanvasPermissionError:
    print("You don't have permission to view this assignment")
```

### Pagination

For large datasets, handle pagination appropriately:

```python
# For processing all data
all_students = []
response = await client.get_users(course_id, enrollment_type=["StudentEnrollment"])
all_students.extend(response.data)

while response.has_next_page:
    next_response = await client._make_request("GET", url=response.next_page_url)
    # ... handle pagination
    
# For UI display with limits
response = await client.get_assignments(course_id, per_page=20)
# Display first 20 assignments only
```

### Rate Limiting Awareness

Be mindful of API rate limits in batch operations:

```python
# Good - let client handle rate limiting
async with CanvasClient(url, auth, rate_limit=5.0) as client:
    for course_id in course_ids:
        assignments = await client.get_assignments(course_id)

# Better - use concurrent requests with rate limiting
tasks = [client.get_assignments(cid) for cid in course_ids]
results = await asyncio.gather(*tasks)
```