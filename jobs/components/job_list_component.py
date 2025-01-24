from django_components import Component, register

@register("job_list")
class JobListComponent(Component):
    template_file = "jobs/components/job_list.html"
    
    def get_context_data(self, jobs, favorite_job_ids=None):
        return {
            "jobs": jobs,
            "favorite_job_ids": favorite_job_ids or []
        }
