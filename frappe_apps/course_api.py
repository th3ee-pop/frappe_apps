"""
Course API - Backend endpoints for course-related features
This demonstrates how to build APIs that interact with LMS data
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_user_dashboard():
    """
    Get comprehensive dashboard data for the current user
    Combines data from LMS and custom logic
    """
    user = frappe.session.user

    # Get enrolled courses from LMS
    enrollments = frappe.get_all(
        "LMS Enrollment",
        filters={"member": user},
        fields=["course", "progress", "current_lesson", "creation"]
    )

    # Enrich with course details
    courses = []
    for enrollment in enrollments:
        course_doc = frappe.get_doc("LMS Course", enrollment.course)

        courses.append({
            "name": course_doc.name,
            "title": course_doc.title,
            "description": course_doc.short_introduction,
            "image": course_doc.image,
            "progress": enrollment.progress or 0,
            "current_lesson": enrollment.current_lesson,
            "enrolled_date": enrollment.creation,
            "instructor": course_doc.owner
        })

    # Get recent progress
    recent_progress = frappe.get_all(
        "LMS Course Progress",
        filters={"member": user},
        fields=["lesson", "status", "time_spent", "modified"],
        order_by="modified desc",
        limit=5
    )

    # Calculate statistics
    total_courses = len(courses)
    completed_courses = len([c for c in courses if c["progress"] >= 100])
    in_progress = total_courses - completed_courses

    return {
        "user": user,
        "statistics": {
            "total_courses": total_courses,
            "completed": completed_courses,
            "in_progress": in_progress
        },
        "courses": courses,
        "recent_activity": recent_progress
    }


@frappe.whitelist()
def get_course_recommendations(course_name=None):
    """
    Get AI-powered course recommendations
    Based on user's current enrollments and progress
    """
    user = frappe.session.user

    # Get user's enrolled courses
    enrolled_courses = frappe.get_all(
        "LMS Enrollment",
        filters={"member": user},
        fields=["course"],
        pluck="course"
    )

    # Get all available courses (not enrolled)
    all_courses = frappe.get_all(
        "LMS Course",
        filters={
            "published": 1,
            "name": ["not in", enrolled_courses]
        },
        fields=["name", "title", "short_introduction", "image", "tags"],
        limit=10
    )

    # Simple recommendation logic (can be enhanced with ML)
    recommendations = []
    for course in all_courses:
        score = calculate_recommendation_score(course, enrolled_courses)
        recommendations.append({
            **course,
            "recommendation_score": score,
            "reason": get_recommendation_reason(course, enrolled_courses)
        })

    # Sort by score
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)

    return recommendations[:5]


def calculate_recommendation_score(course, enrolled_courses):
    """Calculate recommendation score based on tags and other factors"""
    # Simple scoring logic - can be enhanced with ML
    score = 50  # Base score

    # Boost if tags match user's interests
    # This is a placeholder - implement your logic
    if course.get("tags"):
        score += 20

    return score


def get_recommendation_reason(course, enrolled_courses):
    """Generate human-readable recommendation reason"""
    reasons = [
        "Popular in your field",
        "Complements your current courses",
        "Trending this week",
        "Recommended by instructors"
    ]

    # Simple logic - return first reason
    return reasons[0]


@frappe.whitelist()
def search_courses(query, filters=None):
    """
    Search courses with advanced filtering
    """
    if not query:
        return []

    # Build search filters
    search_filters = {
        "published": 1
    }

    if filters:
        if isinstance(filters, str):
            import json
            filters = json.loads(filters)
        search_filters.update(filters)

    # Search in title and description
    courses = frappe.get_all(
        "LMS Course",
        filters=search_filters,
        fields=["name", "title", "short_introduction", "image", "owner"],
        or_filters={
            "title": ["like", f"%{query}%"],
            "short_introduction": ["like", f"%{query}%"]
        },
        limit=20
    )

    return courses


@frappe.whitelist()
def enroll_in_course(course_name):
    """
    Enroll current user in a course
    """
    user = frappe.session.user

    # Check if already enrolled
    existing = frappe.db.exists("LMS Enrollment", {
        "member": user,
        "course": course_name
    })

    if existing:
        return {
            "success": False,
            "message": "Already enrolled in this course"
        }

    # Create enrollment
    enrollment = frappe.get_doc({
        "doctype": "LMS Enrollment",
        "member": user,
        "course": course_name,
        "member_type": "Student"
    })
    enrollment.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "message": "Successfully enrolled in course",
        "enrollment": enrollment.name
    }
