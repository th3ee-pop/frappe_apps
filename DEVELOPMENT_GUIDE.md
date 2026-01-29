# Development Guide - Building Features with API-First Approach

This guide explains how to develop new features in frappe_apps using a familiar API-first + frontend (Vue.js) approach.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Workflow](#development-workflow)
3. [Backend Development (Python)](#backend-development)
4. [Frontend Development (Vue.js)](#frontend-development)
5. [Accessing LMS Data](#accessing-lms-data)
6. [Complete Example](#complete-example)
7. [Best Practices](#best-practices)

---

## Architecture Overview

### How frappe_apps Integrates with LMS

```
┌─────────────────────────────────────────────────────────┐
│  frappe_apps (Your Custom App)                          │
│                                                          │
│  ├── Backend (Python)                                   │
│  │   ├── API Endpoints (@frappe.whitelist)              │
│  │   ├── DocTypes (Database Models)                     │
│  │   ├── Business Logic                                 │
│  │   └── LMS Data Access                                │
│  │                                                       │
│  ├── Frontend (Vue.js/JavaScript)                       │
│  │   ├── Vue Components                                 │
│  │   ├── Pages (/www)                                   │
│  │   └── Static Assets                                  │
│  │                                                       │
│  └── Integration Hooks                                  │
│      ├── Document Events (listen to LMS changes)        │
│      ├── Page Hooks (inject UI)                         │
│      └── Website Context (modify rendering)             │
└─────────────────────────────────────────────────────────┘
                       │
                       │ Can access data from
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Frappe LMS (Existing App)                              │
│                                                          │
│  ├── DocTypes (Database Tables)                         │
│  │   ├── LMS Course                                     │
│  │   ├── LMS Enrollment                                 │
│  │   ├── LMS Course Progress                            │
│  │   └── Course Lesson                                  │
│  │                                                       │
│  ├── LMS APIs                                            │
│  │   └── lms.lms.api.*                                  │
│  │                                                       │
│  └── LMS Utilities                                       │
│      └── lms.lms.utils.*                                │
└─────────────────────────────────────────────────────────┘
```

---

## Development Workflow

### 1. **API-First Approach** (Recommended)

Follow this workflow for building new features:

```
1. Define the feature requirements
   ↓
2. Design the API endpoints (Python)
   ↓
3. Implement backend logic (Python)
   ↓
4. Test API with Postman/curl
   ↓
5. Build frontend UI (Vue.js)
   ↓
6. Connect frontend to API (frappe.call)
   ↓
7. Test end-to-end
   ↓
8. Deploy
```

### 2. **Development Commands**

```bash
# Navigate to bench directory
cd ~/frappe-bench

# Start development server
bench start

# Watch for changes
bench watch

# Clear cache after backend changes
bench --site learning.test clear-cache

# Build frontend assets
bench build --app frappe_apps

# Run tests
bench --site learning.test run-tests --app frappe_apps
```

---

## Backend Development (Python)

### Creating API Endpoints

All API endpoints go in `frappe_apps/api.py` or dedicated files like `course_api.py`:

```python
# frappe_apps/api.py
import frappe
from frappe import _

@frappe.whitelist()
def my_api_endpoint(param1, param2):
    """
    Your API endpoint documentation

    Args:
        param1: Description
        param2: Description

    Returns:
        dict: Response data
    """
    # Your logic here
    user = frappe.session.user

    # Access database
    data = frappe.get_all("DocType Name", filters={...})

    return {
        "success": True,
        "data": data
    }

# No authentication required (guest access)
@frappe.whitelist(allow_guest=True)
def public_api():
    return {"message": "Public endpoint"}
```

### Accessing LMS Data

#### Method 1: Query DocTypes Directly

```python
import frappe

# Get all courses
courses = frappe.get_all(
    "LMS Course",
    filters={"published": 1},
    fields=["name", "title", "short_introduction", "image"]
)

# Get single course
course = frappe.get_doc("LMS Course", "course-name")

# Get user enrollments
enrollments = frappe.get_all(
    "LMS Enrollment",
    filters={"member": frappe.session.user},
    fields=["course", "progress", "current_lesson"]
)

# Get course progress
progress = frappe.get_all(
    "LMS Course Progress",
    filters={
        "member": frappe.session.user,
        "course": "course-name"
    },
    fields=["lesson", "status", "time_spent"]
)
```

#### Method 2: Use LMS Utilities

```python
from lms.lms.utils import (
    get_membership,
    get_chapters,
    get_lessons,
    get_course_progress
)

# Check if user is enrolled
membership = get_membership("course-name", frappe.session.user)
is_enrolled = membership is not None

# Get course structure
chapters = get_chapters("course-name")
lessons = get_lessons("course-name")

# Get detailed progress
progress = get_course_progress("course-name", frappe.session.user)
```

### Available LMS DocTypes

You can query these DocTypes from frappe_apps:

| DocType | Purpose | Key Fields |
|---------|---------|------------|
| `LMS Course` | Course information | name, title, description, published, owner |
| `LMS Enrollment` | User enrollments | member, course, progress, member_type |
| `LMS Course Progress` | Lesson progress | member, course, lesson, status, time_spent |
| `Course Lesson` | Lesson content | title, body, course, chapter, idx |
| `LMS Batch` | Course batches | title, course, start_date, end_date |
| `LMS Certificate` | Certificates | member, course, issue_date |

### Hooks: Listening to LMS Events

React to LMS actions automatically:

```python
# frappe_apps/hooks.py
doc_events = {
    "LMS Enrollment": {
        "after_insert": "frappe_apps.events.on_course_enrollment",
        "on_update": "frappe_apps.events.on_enrollment_update"
    },
    "LMS Course Progress": {
        "on_update": "frappe_apps.events.on_lesson_complete"
    }
}

# frappe_apps/events.py
import frappe

def on_course_enrollment(doc, method):
    """Called when user enrolls in a course"""
    # Send welcome notification
    # Update user statistics
    # Trigger AI assistant greeting
    pass

def on_lesson_complete(doc, method):
    """Called when user completes a lesson"""
    if doc.status == "Complete":
        # Award points
        # Check for achievement unlocks
        # Send congratulations message
        pass
```

---

## Frontend Development (Vue.js)

### Option 1: Simple In-Page Vue (Quick Prototyping)

Create a page in `frappe_apps/www/mypage.html`:

```html
{% extends "templates/web.html" %}

{% block page_content %}
<div id="app">
    <h1>{{ message }}</h1>
    <button @click="loadData">Load Data</button>
    <ul>
        <li v-for="item in items" :key="item.name">{{ item.title }}</li>
    </ul>
</div>

<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
<script>
    const { createApp } = Vue;

    frappe.ready(() => {
        createApp({
            data() {
                return {
                    message: 'Hello from Vue!',
                    items: []
                }
            },
            methods: {
                async loadData() {
                    const response = await frappe.call({
                        method: 'frappe_apps.api.my_api_endpoint',
                        args: { param1: 'value' }
                    });
                    this.items = response.message.data;
                }
            },
            mounted() {
                this.loadData();
            }
        }).mount('#app');
    });
</script>
{% endblock %}
```

### Option 2: Full Vue SPA (Production)

For complex UIs, build a separate Vue app like LMS does:

```bash
# Create frontend directory
cd frappe_apps
mkdir -p frontend/src

# Initialize Vue project
cd frontend
yarn init -y
yarn add vue@3 vite @vitejs/plugin-vue

# Create vite.config.js
cat > vite.config.js <<EOF
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/assets/frappe_apps/frontend/',
  build: {
    outDir: '../frappe_apps/public/frontend',
    emptyOutDir: true,
  }
})
EOF
```

### Calling Backend APIs from Vue

```javascript
// In any Vue component
export default {
  methods: {
    async callApi() {
      try {
        // Method 1: Using frappe.call (recommended)
        const response = await frappe.call({
          method: 'frappe_apps.course_api.get_user_dashboard',
          args: {},
        });

        console.log('Data:', response.message);

        // Method 2: Using fetch (alternative)
        const res = await fetch('/api/method/frappe_apps.course_api.get_user_dashboard', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': frappe.csrf_token
          },
          body: JSON.stringify({})
        });

        const data = await res.json();
        console.log('Data:', data.message);

      } catch (error) {
        console.error('API Error:', error);
        frappe.show_alert({
          message: 'Failed to load data',
          indicator: 'red'
        });
      }
    }
  }
}
```

---

## Complete Example

See the following files for a complete working example:

1. **Backend API**: `frappe_apps/course_api.py`
   - Implements course recommendations
   - Accesses LMS data
   - Provides enrollment functionality

2. **Vue Component**: `frappe_apps/public/js/CourseRecommendations.vue`
   - Displays recommendations
   - Handles user interactions
   - Calls backend APIs

3. **Frappe Page**: `frappe_apps/www/recommendations.html`
   - Hosts the Vue component
   - Handles authentication
   - Renders the UI

### Test the Example

```bash
# Access the page
http://localhost:8000/recommendations

# The page will:
# 1. Load course recommendations via API
# 2. Display them in a card layout
# 3. Allow users to enroll with one click
```

---

## Best Practices

### 1. **API Design**

✅ **DO:**
- Use clear, descriptive endpoint names
- Return consistent response structures
- Include proper error handling
- Add docstrings to all functions
- Validate input parameters

❌ **DON'T:**
- Return raw database objects
- Expose sensitive data without checks
- Use allow_guest=True unless necessary
- Skip permission checks

### 2. **Accessing LMS Data**

✅ **DO:**
- Use frappe.get_all() for lists
- Use frappe.get_doc() for single documents
- Check permissions before returning data
- Use LMS utility functions when available

❌ **DON'T:**
- Query database directly with SQL
- Return data without permission checks
- Modify LMS DocTypes without understanding impact

### 3. **Frontend Development**

✅ **DO:**
- Use frappe.call() for API calls
- Show loading states
- Handle errors gracefully
- Use Frappe's built-in alerts

❌ **DON'T:**
- Make API calls on every keystroke (debounce!)
- Store sensitive data in component state
- Ignore error responses

### 4. **Performance**

- Cache expensive queries
- Paginate large lists
- Use database indexes
- Minimize API calls

---

## Common Patterns

### Pattern 1: Dashboard Page

```python
# Backend
@frappe.whitelist()
def get_dashboard_data():
    user = frappe.session.user

    # Aggregate data from multiple sources
    courses = get_user_courses(user)
    stats = calculate_stats(user)
    activity = get_recent_activity(user)

    return {
        "courses": courses,
        "stats": stats,
        "activity": activity
    }
```

```javascript
// Frontend
export default {
  data() {
    return {
      dashboard: null,
      loading: true
    }
  },
  async mounted() {
    const res = await frappe.call({
      method: 'frappe_apps.api.get_dashboard_data'
    });
    this.dashboard = res.message;
    this.loading = false;
  }
}
```

### Pattern 2: Search with Filters

```python
# Backend
@frappe.whitelist()
def search_courses(query, category=None, level=None):
    filters = {"published": 1}

    if category:
        filters["category"] = category
    if level:
        filters["level"] = level

    return frappe.get_all(
        "LMS Course",
        filters=filters,
        or_filters={
            "title": ["like", f"%{query}%"],
            "description": ["like", f"%{query}%"]
        }
    )
```

```javascript
// Frontend with debounce
export default {
  data() {
    return {
      query: '',
      results: []
    }
  },
  watch: {
    query: {
      handler: 'debouncedSearch',
      immediate: false
    }
  },
  methods: {
    debouncedSearch: _.debounce(async function() {
      const res = await frappe.call({
        method: 'frappe_apps.api.search_courses',
        args: { query: this.query }
      });
      this.results = res.message;
    }, 300)
  }
}
```

### Pattern 3: Form Submission

```python
# Backend
@frappe.whitelist()
def save_user_preference(preference_type, value):
    user = frappe.session.user

    # Validate input
    if preference_type not in ["theme", "language", "notifications"]:
        frappe.throw("Invalid preference type")

    # Save to database
    pref = frappe.get_doc({
        "doctype": "User Preference",
        "user": user,
        "preference_type": preference_type,
        "value": value
    })
    pref.insert()

    return {"success": True}
```

```javascript
// Frontend
export default {
  methods: {
    async savePreference(type, value) {
      try {
        await frappe.call({
          method: 'frappe_apps.api.save_user_preference',
          args: { preference_type: type, value: value }
        });

        frappe.show_alert({
          message: 'Preference saved',
          indicator: 'green'
        });
      } catch (error) {
        frappe.show_alert({
          message: 'Failed to save',
          indicator: 'red'
        });
      }
    }
  }
}
```

---

## Next Steps

1. **Study the Examples**: Review `course_api.py` and `CourseRecommendations.vue`
2. **Start Small**: Build a simple feature first (e.g., "My Learning Progress" page)
3. **Test APIs**: Use Postman or curl to test your backend before building frontend
4. **Read Frappe Docs**: https://frappeframework.com/docs
5. **Explore LMS Code**: Look at `apps/lms/lms/` for examples

---

## Useful Resources

- **Frappe Framework Docs**: https://frappeframework.com/docs
- **Frappe API Reference**: https://frappeframework.com/docs/user/en/api
- **LMS Source Code**: `/Users/chensirui/my-bench/apps/lms/`
- **Vue 3 Docs**: https://vuejs.org/guide/introduction.html

## Getting Help

- **Frappe Forum**: https://discuss.frappe.io
- **LMS Discussions**: https://github.com/frappe/lms/discussions
- **Your Project Issues**: https://github.com/th3ee-pop/frappe_apps/issues
