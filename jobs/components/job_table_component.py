from django_components import component


@component.register("job_table")
class JobTableComponent(component.Component):
    template_name = "jobs/partials/job_table.html"
    
    def get_context_data(self, jobs, favorite_job_ids=None):
        return {
            "jobs": jobs,
            "favorite_job_ids": favorite_job_ids or []
        }
