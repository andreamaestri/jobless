from django_components import component, types


@component.register("job_form")
class JobFormComponent(component.Component):
    template: types.django_html = """
    {% include "jobs/partials/form_fields.html" %}
    """

    def get_context_data(self, form):
        return {
            "form": form
        }
