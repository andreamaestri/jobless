from django_components import component


@component.register("job_list")
class JobListComponent(component.Component):
    template = """
    {% load job_tags %}
    
    <div class="w-full rounded-xl border border-base-200"
         x-data="{ 
             activeFilter: '{{ filter|default:'all' }}',
             favoriteJobs: new Set({{ favorite_job_ids|safe|default:'[]' }}),
             isFavorited(jobId) {
                 return this.favoriteJobs.has(jobId);
             },
             toggleFavorite(jobId) {
                 if (this.isFavorited(jobId)) {
                     this.favoriteJobs.delete(jobId);
                 } else {
                     this.favoriteJobs.add(jobId);
                 }
             }
         }">
        <!-- Table view (hidden on mobile) -->
        <div class="hidden sm:block">
            {% component "job_table" jobs=jobs favorite_job_ids=favorite_job_ids %}
            {% endcomponent %}
        </div>

        <!-- Card view (visible only on mobile) -->
        <div class="sm:hidden">
            {% component "job_card_list" jobs=jobs favorite_job_ids=favorite_job_ids %}
            {% endcomponent %}
        </div>
    </div>
    """

    def get_context_data(self, jobs, favorite_job_ids=None, filter=None):
        return {
            "jobs": jobs,
            "favorite_job_ids": favorite_job_ids or [],
            "filter": filter
        }
