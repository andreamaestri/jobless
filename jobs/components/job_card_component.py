from django_components import Component, register

@register("job_card")
class JobCardComponent(Component):
    template_file = "jobs/components/job_card.html"
    
    def get_context_data(self, job, is_favorite=False):
        return {
            "job": job,
            "is_favorite": is_favorite
        }
