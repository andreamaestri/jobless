from django_components import component


@component.register("job_card_list")
class JobCardListComponent(component.Component):
    template_name = "job_card_list.html"
    template_dir = "jobs/components"
    
    def get_context_data(self, jobs, favorite_job_ids=None):
        return {
            "jobs": jobs,
            "favorite_job_ids": favorite_job_ids or []
        }
