<template>
  <div class="course-recommendations">
    <!-- Header -->
    <div class="recommendations-header">
      <h2>Recommended Courses for You</h2>
      <p>Based on your learning progress and interests</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading recommendations...</p>
    </div>

    <!-- Recommendations List -->
    <div v-else class="recommendations-list">
      <div
        v-for="course in recommendations"
        :key="course.name"
        class="course-card"
        @click="viewCourse(course.name)"
      >
        <!-- Course Image -->
        <div class="course-image">
          <img :src="course.image || '/assets/frappe/images/default-course.png'" :alt="course.title">
          <div class="recommendation-badge">
            <span>{{ course.recommendation_score }}% Match</span>
          </div>
        </div>

        <!-- Course Info -->
        <div class="course-info">
          <h3>{{ course.title }}</h3>
          <p class="course-description">{{ course.short_introduction }}</p>
          <p class="recommendation-reason">
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            {{ course.reason }}
          </p>

          <!-- Tags -->
          <div v-if="course.tags" class="course-tags">
            <span v-for="tag in parseTags(course.tags)" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>

          <!-- Action Button -->
          <button
            class="enroll-btn"
            @click.stop="enrollInCourse(course.name)"
            :disabled="enrolling === course.name"
          >
            <span v-if="enrolling === course.name">Enrolling...</span>
            <span v-else>Enroll Now</span>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="recommendations.length === 0" class="empty-state">
        <p>No recommendations available at the moment.</p>
        <p>Complete more courses to get personalized recommendations!</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadRecommendations">Retry</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseRecommendations',

  data() {
    return {
      recommendations: [],
      loading: true,
      error: null,
      enrolling: null
    }
  },

  mounted() {
    this.loadRecommendations()
  },

  methods: {
    async loadRecommendations() {
      this.loading = true
      this.error = null

      try {
        // Call your backend API using Frappe's call method
        const response = await frappe.call({
          method: 'frappe_apps.course_api.get_course_recommendations',
          args: {},
        })

        if (response.message) {
          this.recommendations = response.message
        }
      } catch (err) {
        this.error = 'Failed to load recommendations. Please try again.'
        console.error('Error loading recommendations:', err)
      } finally {
        this.loading = false
      }
    },

    async enrollInCourse(courseName) {
      this.enrolling = courseName

      try {
        const response = await frappe.call({
          method: 'frappe_apps.course_api.enroll_in_course',
          args: { course_name: courseName },
        })

        if (response.message.success) {
          // Show success message
          frappe.show_alert({
            message: response.message.message,
            indicator: 'green'
          })

          // Remove from recommendations
          this.recommendations = this.recommendations.filter(
            c => c.name !== courseName
          )

          // Redirect to course
          setTimeout(() => {
            window.location.href = `/courses/${courseName}`
          }, 1000)
        } else {
          frappe.show_alert({
            message: response.message.message,
            indicator: 'orange'
          })
        }
      } catch (err) {
        frappe.show_alert({
          message: 'Failed to enroll. Please try again.',
          indicator: 'red'
        })
        console.error('Error enrolling:', err)
      } finally {
        this.enrolling = null
      }
    },

    viewCourse(courseName) {
      window.location.href = `/courses/${courseName}`
    },

    parseTags(tags) {
      if (typeof tags === 'string') {
        return tags.split(',').map(t => t.trim()).filter(Boolean)
      }
      return Array.isArray(tags) ? tags : []
    }
  }
}
</script>

<style scoped>
.course-recommendations {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.recommendations-header {
  margin-bottom: 2rem;
}

.recommendations-header h2 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.recommendations-header p {
  color: #666;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.recommendations-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.course-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.course-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommendation-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.course-info {
  padding: 1.5rem;
}

.course-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.course-description {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recommendation-reason {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #764ba2;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.recommendation-reason .icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag {
  background: #f0f0f0;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  color: #666;
}

.enroll-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.enroll-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.enroll-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  color: #666;
}

.error-message {
  text-align: center;
  padding: 2rem;
  color: #e74c3c;
}

.error-message button {
  margin-top: 1rem;
  padding: 10px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
