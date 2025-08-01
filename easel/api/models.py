"""Canvas API data models."""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class User(BaseModel):
    """Canvas user model."""

    id: int
    name: str
    email: Optional[str] = None
    login_id: Optional[str] = None
    sis_user_id: Optional[str] = None
    sortable_name: Optional[str] = None
    short_name: Optional[str] = None
    created_at: Optional[datetime] = None


class Course(BaseModel):
    """Canvas course model."""

    id: int
    name: str
    course_code: Optional[str] = None
    workflow_state: Optional[str] = None
    account_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    enrollment_term_id: Optional[int] = None
    is_public: Optional[bool] = None
    is_public_to_auth_users: Optional[bool] = None
    public_syllabus: Optional[bool] = None
    public_syllabus_to_auth: Optional[bool] = None
    public_description: Optional[str] = None
    storage_quota_mb: Optional[int] = None
    is_favorite: Optional[bool] = None
    apply_assignment_group_weights: Optional[bool] = None
    calendar: Optional[Dict[str, str]] = None
    time_zone: Optional[str] = None
    blueprint: Optional[bool] = None
    template: Optional[bool] = None
    enrollments: Optional[List[Dict[str, Any]]] = None
    hide_final_grades: Optional[bool] = None
    workflow_state_name: Optional[str] = None
    restrict_enrollments_to_course_dates: Optional[bool] = None


class Assignment(BaseModel):
    """Canvas assignment model."""

    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    lock_at: Optional[datetime] = None
    unlock_at: Optional[datetime] = None
    course_id: int
    html_url: Optional[str] = None
    submissions_download_url: Optional[str] = None
    assignment_group_id: Optional[int] = None
    due_date_required: Optional[bool] = None
    allowed_extensions: Optional[List[str]] = None
    max_name_length: Optional[int] = None
    turnitin_enabled: Optional[bool] = None
    vericite_enabled: Optional[bool] = None
    turnitin_settings: Optional[Dict[str, Any]] = None
    grade_group_students_individually: Optional[bool] = None
    external_tool_tag_attributes: Optional[Dict[str, Any]] = None
    peer_reviews: Optional[bool] = None
    automatic_peer_reviews: Optional[bool] = None
    peer_review_count: Optional[int] = None
    peer_reviews_assign_at: Optional[datetime] = None
    intra_group_peer_reviews: Optional[bool] = None
    group_category_id: Optional[int] = None
    needs_grading_count: Optional[int] = None
    needs_grading_count_by_section: Optional[List[Dict[str, Any]]] = None
    position: Optional[int] = None
    post_to_sis: Optional[bool] = None
    integration_id: Optional[str] = None
    integration_data: Optional[Dict[str, Any]] = None
    points_possible: Optional[float] = None
    submission_types: Optional[List[str]] = None
    has_submitted_submissions: Optional[bool] = None
    grading_type: Optional[str] = None
    grading_standard_id: Optional[int] = None
    published: Optional[bool] = None
    unpublishable: Optional[bool] = None
    only_visible_to_overrides: Optional[bool] = None
    locked_for_user: Optional[bool] = None
    lock_info: Optional[Dict[str, Any]] = None
    lock_explanation: Optional[str] = None
    quiz_id: Optional[int] = None
    anonymous_submissions: Optional[bool] = None
    discussion_topic: Optional[Dict[str, Any]] = None
    freeze_on_copy: Optional[bool] = None
    frozen: Optional[bool] = None
    frozen_attributes: Optional[List[str]] = None


class Discussion(BaseModel):
    """Canvas discussion topic model."""

    id: int
    title: str
    message: Optional[str] = None
    html_url: Optional[str] = None
    posted_at: Optional[datetime] = None
    last_reply_at: Optional[datetime] = None
    require_initial_post: Optional[bool] = None
    user_can_see_posts: Optional[bool] = None
    discussion_subentry_count: Optional[int] = None
    read_state: Optional[str] = None
    unread_count: Optional[int] = None
    subscribed: Optional[bool] = None
    subscription_hold: Optional[str] = None
    assignment_id: Optional[int] = None
    delayed_post_at: Optional[datetime] = None
    published: Optional[bool] = None
    lock_at: Optional[datetime] = None
    locked: Optional[bool] = None
    pinned: Optional[bool] = None
    locked_for_user: Optional[bool] = None
    lock_info: Optional[Dict[str, Any]] = None
    lock_explanation: Optional[str] = None
    user_name: Optional[str] = None
    topic_children: Optional[List[int]] = None
    group_topic_children: Optional[List[Dict[str, Any]]] = None
    root_topic_id: Optional[int] = None
    podcast_url: Optional[str] = None
    discussion_type: Optional[str] = None
    group_category_id: Optional[int] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    permissions: Optional[Dict[str, bool]] = None
    allow_rating: Optional[bool] = None
    only_graders_can_rate: Optional[bool] = None
    sort_by_rating: Optional[bool] = None


class Page(BaseModel):
    """Canvas page model."""

    url: str
    title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    hide_from_students: Optional[bool] = None
    editing_roles: Optional[str] = None
    last_edited_by: Optional[User] = None
    body: Optional[str] = None
    published: Optional[bool] = None
    front_page: Optional[bool] = None
    locked_for_user: Optional[bool] = None
    lock_info: Optional[Dict[str, Any]] = None
    lock_explanation: Optional[str] = None


class Submission(BaseModel):
    """Canvas submission model."""

    id: int
    user_id: int
    assignment_id: int
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None
    grade: Optional[str] = None
    attempt: Optional[int] = None
    body: Optional[str] = None
    url: Optional[str] = None
    submission_type: Optional[str] = None
    workflow_state: Optional[str] = None
    grade_matches_current_submission: Optional[bool] = None
    graded_at: Optional[datetime] = None
    grader_id: Optional[int] = None
    excused: Optional[bool] = None
    late_policy_status: Optional[str] = None
    points_deducted: Optional[float] = None
    seconds_late: Optional[int] = None
    extra_attempts: Optional[int] = None
    anonymous_id: Optional[str] = None
