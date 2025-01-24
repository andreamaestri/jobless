from django_components import Component, register

@register("job_detail")
class JobDetailComponent(Component):
    template_file = "jobs/components/job_detail.html"
    
    def get_context_data(self, job, is_favorite=False):
        return {
            "job": job,
            "is_favorite": is_favorite
        }
