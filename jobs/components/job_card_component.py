from django_components import component


@component.register("job_card")
class JobCardComponent(component.Component):
    template = """
    {% load job_tags %}
    <div class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all duration-300 group relative overflow-hidden"
         x-data="{ 
             isFavorite: {{ is_favorite|yesno:'true,false' }},
             toggleFavorite(jobId) {
                 this.isFavorite = !this.isFavorite;
                 fetch(`/jobs/toggle_favorite/${jobId}/`, {
                     method: 'POST',
                     headers: {
                         'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                     }
                 });
             }
         }">
        <div class="absolute top-4 right-4 z-10">
            <button @click="toggleFavorite({{ job.pk }})"
                    class="btn btn-circle btn-ghost btn-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <iconify-icon 
                    :icon="isFavorite ? 'octicon:star-fill-24' : 'octicon:star-24'" 
                    class="text-warning"
                    :class="{ 'text-warning': isFavorite }">
                </iconify-icon>
            </button>
        </div>
        <a href="{% url 'jobs:detail' job.pk %}" class="block">
            <div class="card-body">
                <div class="flex justify-between items-start">
                    <div>
                        <h2 class="card-title text-base-content">{{ job.title }}</h2>
                        <p class="text-base-content/70 text-sm">{{ job.company }}</p>
                    </div>
                    <span class="badge {{ job.status|status_badge }} badge-sm">
                        <iconify-icon icon="{{ job.status|status_icon }}" class="mr-1"></iconify-icon>
                        {{ job.get_status_display }}
                    </span>
                </div>
                
                <div class="mt-4">
                    <div class="flex items-center text-base-content/70 text-sm gap-2 mb-2">
                        <iconify-icon icon="heroicons:map-pin" class="text-base"></iconify-icon>
                        {{ job.location }}
                    </div>
                    
                    {% if job.skills.count > 0 %}
                    <div class="flex flex-wrap gap-2 mt-2">
                        {% for skill in job.skills.all|slice:":3" %}
                        <span class="badge badge-accent badge-xs gap-1">
                            <iconify-icon icon="{{ skill|get_skill_icon:True }}" class="text-xs"></iconify-icon>
                            {{ skill.name }}
                        </span>
                        {% endfor %}
                        {% if job.skills.count > 3 %}
                        <span class="badge badge-ghost badge-xs">
                            +{{ job.skills.count|add:"-3" }}
                        </span>
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
            </div>
        </a>
    </div>
    """

    def get_context_data(self, job, is_favorite=False):
        return {
            "job": job,
            "is_favorite": is_favorite
        }
