from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required  # Add this import
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
import json
import logging
from .models import JobPosting, SKILL_ICONS
from .forms import JobPostingForm
from django import template, forms

logger = logging.getLogger(__name__)

register = template.Library()

DARK_VARIANTS = {
    'skill-icons:ableton': 'skill-icons:ableton-dark',
    'skill-icons:activitypub': 'skill-icons:activitypub-dark',
    'skill-icons:actix': 'skill-icons:actix-dark',
    'skill-icons:aiscript': 'skill-icons:aiscript-dark',
    'skill-icons:alpinejs': 'skill-icons:alpinejs-dark',
    'skill-icons:anaconda': 'skill-icons:anaconda-dark',
    'skill-icons:androidstudio': 'skill-icons:androidstudio-dark',
    'skill-icons:angular': 'skill-icons:angular-dark',
    'skill-icons:apple': 'skill-icons:apple-dark',
    'skill-icons:arch': 'skill-icons:arch-dark',
    'skill-icons:autocad': 'skill-icons:autocad-dark',
    'skill-icons:aws': 'skill-icons:aws-dark',
    'skill-icons:azure': 'skill-icons:azure-dark',
    'skill-icons:bash': 'skill-icons:bash-dark',
    'skill-icons:bevy': 'skill-icons:bevy-dark',
    'skill-icons:bitbucket': 'skill-icons:bitbucket-dark',
    'skill-icons:blender': 'skill-icons:blender-dark',
    'skill-icons:bsd': 'skill-icons:bsd-dark',
    'skill-icons:bun': 'skill-icons:bun-dark',
    'skill-icons:cassandra': 'skill-icons:cassandra-dark',
    'skill-icons:clion': 'skill-icons:clion-dark',
    'skill-icons:clojure': 'skill-icons:clojure-dark',
    'skill-icons:cloudflare': 'skill-icons:cloudflare-dark',
    'skill-icons:cmake': 'skill-icons:cmake-dark',
    'skill-icons:codepen': 'skill-icons:codepen-dark',
    'skill-icons:coffeescript': 'skill-icons:coffeescript-dark',
    'skill-icons:crystal': 'skill-icons:crystal-dark',
    'skill-icons:cypress': 'skill-icons:cypress-dark',
    'skill-icons:d3': 'skill-icons:d3-dark',
    'skill-icons:dart': 'skill-icons:dart-dark',
    'skill-icons:debian': 'skill-icons:debian-dark',
    'skill-icons:deno': 'skill-icons:deno-dark',
    'skill-icons:devto': 'skill-icons:devto-dark',
    'skill-icons:discordjs': 'skill-icons:discordjs-dark',
    'skill-icons:dynamodb': 'skill-icons:dynamodb-dark',
    'skill-icons:eclipse': 'skill-icons:eclipse-dark',
    'skill-icons:elasticsearch': 'skill-icons:elasticsearch-dark',
    'skill-icons:elixir': 'skill-icons:elixir-dark',
    'skill-icons:elysia': 'skill-icons:elysia-dark',
    'skill-icons:emotion': 'skill-icons:emotion-dark',
    'skill-icons:expressjs': 'skill-icons:expressjs-dark',
    'skill-icons:fediverse': 'skill-icons:fediverse-dark',
    'skill-icons:figma': 'skill-icons:figma-dark',
    'skill-icons:flask': 'skill-icons:flask-dark',
    'skill-icons:flutter': 'skill-icons:flutter-dark',
    'skill-icons:gcp': 'skill-icons:gcp-dark',
    'skill-icons:gherkin': 'skill-icons:gherkin-dark',
    'skill-icons:github': 'skill-icons:github-dark',
    'skill-icons:githubactions': 'skill-icons:githubactions-dark',
    'skill-icons:gitlab': 'skill-icons:gitlab-dark',
    'skill-icons:gmail': 'skill-icons:gmail-dark',
    'skill-icons:godot': 'skill-icons:godot-dark',
    'skill-icons:gradle': 'skill-icons:gradle-dark',
    'skill-icons:grafana': 'skill-icons:grafana-dark',
    'skill-icons:graphql': 'skill-icons:graphql-dark',
    'skill-icons:gtk': 'skill-icons:gtk-dark',
    'skill-icons:haskell': 'skill-icons:haskell-dark',
    'skill-icons:haxe': 'skill-icons:haxe-dark',
    'skill-icons:haxeflixel': 'skill-icons:haxeflixel-dark',
    'skill-icons:hibernate': 'skill-icons:hibernate-dark',
    'skill-icons:htmx': 'skill-icons:htmx-dark',
    'skill-icons:idea': 'skill-icons:idea-dark',
    'skill-icons:ipfs': 'skill-icons:ipfs-dark',
    'skill-icons:java': 'skill-icons:java-dark',
    'skill-icons:jenkins': 'skill-icons:jenkins-dark',
    'skill-icons:julia': 'skill-icons:julia-dark',
    'skill-icons:kali': 'skill-icons:kali-dark',
    'skill-icons:kotlin': 'skill-icons:kotlin-dark',
    'skill-icons:ktor': 'skill-icons:ktor-dark',
    'skill-icons:laravel': 'skill-icons:laravel-dark',
    'skill-icons:latex': 'skill-icons:latex-dark',
    'skill-icons:less': 'skill-icons:less-dark',
    'skill-icons:linux': 'skill-icons:linux-dark',
    'skill-icons:lit': 'skill-icons:lit-dark',
    'skill-icons:lua': 'skill-icons:lua-dark',
    'skill-icons:markdown': 'skill-icons:markdown-dark',
    'skill-icons:mastodon': 'skill-icons:mastodon-dark',
    'skill-icons:materialui': 'skill-icons:materialui-dark',
    'skill-icons:matlab': 'skill-icons:matlab-dark',
    'skill-icons:maven': 'skill-icons:maven-dark',
    'skill-icons:mint': 'skill-icons:mint-dark',
    'skill-icons:misskey': 'skill-icons:misskey-dark',
    'skill-icons:mysql': 'skill-icons:mysql-dark',
    'skill-icons:neovim': 'skill-icons:neovim-dark',
    'skill-icons:nestjs': 'skill-icons:nestjs-dark',
    'skill-icons:netlify': 'skill-icons:netlify-dark',
    'skill-icons:nextjs': 'skill-icons:nextjs-dark',
    'skill-icons:nim': 'skill-icons:nim-dark',
    'skill-icons:nix': 'skill-icons:nix-dark',
    'skill-icons:nodejs': 'skill-icons:nodejs-dark',
    'skill-icons:notion': 'skill-icons:notion-dark',
    'skill-icons:npm': 'skill-icons:npm-dark',
    'skill-icons:nuxtjs': 'skill-icons:nuxtjs-dark',
    'skill-icons:obsidian': 'skill-icons:obsidian-dark',
    'skill-icons:octave': 'skill-icons:octave-dark',
    'skill-icons:opencv': 'skill-icons:opencv-dark',
    'skill-icons:openstack': 'skill-icons:openstack-dark',
    'skill-icons:php': 'skill-icons:php-dark',
    'skill-icons:phpstorm': 'skill-icons:phpstorm-dark',
    'skill-icons:pinia': 'skill-icons:pinia-dark',
    'skill-icons:pkl': 'skill-icons:pkl-dark',
    'skill-icons:plan9': 'skill-icons:plan9-dark',
    'skill-icons:planetscale': 'skill-icons:planetscale-dark',
    'skill-icons:pnpm': 'skill-icons:pnpm-dark',
    'skill-icons:postgresql': 'skill-icons:postgresql-dark',
    'skill-icons:powershell': 'skill-icons:powershell-dark',
    'skill-icons:processing': 'skill-icons:processing-dark',
    'skill-icons:pug': 'skill-icons:pug-dark',
    'skill-icons:pycharm': 'skill-icons:pycharm-dark',
    'skill-icons:python': 'skill-icons:python-dark',
    'skill-icons:pytorch': 'skill-icons:pytorch-dark',
    'skill-icons:qt': 'skill-icons:qt-dark',
    'skill-icons:r': 'skill-icons:r-dark',
    'skill-icons:rabbitmq': 'skill-icons:rabbitmq-dark',
    'skill-icons:raspberrypi': 'skill-icons:raspberrypi-dark',
    'skill-icons:react': 'skill-icons:react-dark',
    'skill-icons:reactivex': 'skill-icons:reactivex-dark',
    'skill-icons:redhat': 'skill-icons:redhat-dark',
    'skill-icons:redis': 'skill-icons:redis-dark',
    'skill-icons:regex': 'skill-icons:regex-dark',
    'skill-icons:remix': 'skill-icons:remix-dark',
    'skill-icons:replit': 'skill-icons:replit-dark',
    'skill-icons:rider': 'skill-icons:rider-dark',
    'skill-icons:rollupjs': 'skill-icons:rollupjs-dark',
    'skill-icons:ros': 'skill-icons:ros-dark',
    'skill-icons:scala': 'skill-icons:scala-dark',
    'skill-icons:scikitlearn': 'skill-icons:scikitlearn-dark',
    'skill-icons:sequelize': 'skill-icons:sequelize-dark',
    'skill-icons:sketchup': 'skill-icons:sketchup-dark',
    'skill-icons:solidjs': 'skill-icons:solidjs-dark',
    'skill-icons:spring': 'skill-icons:spring-dark',
    'skill-icons:stackoverflow': 'skill-icons:stackoverflow-dark',
    'skill-icons:sublime': 'skill-icons:sublime-dark',
    'skill-icons:supabase': 'skill-icons:supabase-dark',
    'skill-icons:svg': 'skill-icons:svg-dark',
    'skill-icons:symfony': 'skill-icons:symfony-dark',
    'skill-icons:tailwindcss': 'skill-icons:tailwindcss-dark',
    'skill-icons:tauri': 'skill-icons:tauri-dark',
    'skill-icons:tensorflow': 'skill-icons:tensorflow-dark',
    'skill-icons:terraform': 'skill-icons:terraform-dark',
    'skill-icons:threejs': 'skill-icons:threejs-dark',
    'skill-icons:ubuntu': 'skill-icons:ubuntu-dark',
    'skill-icons:unity': 'skill-icons:unity-dark',
    'skill-icons:v': 'skill-icons:v-dark',
    'skill-icons:vercel': 'skill-icons:vercel-dark',
    'skill-icons:vim': 'skill-icons:vim-dark',
    'skill-icons:visualstudio': 'skill-icons:visualstudio-dark',
    'skill-icons:vite': 'skill-icons:vite-dark',
    'skill-icons:vitest': 'skill-icons:vitest-dark',
    'skill-icons:vscode': 'skill-icons:vscode-dark',
    'skill-icons:vscodium': 'skill-icons:vscodium-dark',
    'skill-icons:vuejs': 'skill-icons:vuejs-dark',
    'skill-icons:vuetify': 'skill-icons:vuetify-dark',
    'skill-icons:webpack': 'skill-icons:webpack-dark',
    'skill-icons:webstorm': 'skill-icons:webstorm-dark',
    'skill-icons:windicss': 'skill-icons:windicss-dark',
    'skill-icons:windows': 'skill-icons:windows-dark',
    'skill-icons:workers': 'skill-icons:workers-dark',
    'skill-icons:yarn': 'skill-icons:yarn-dark',
    'skill-icons:yew': 'skill-icons:yew-dark',
    'skill-icons:zig': 'skill-icons:zig-dark'
}

ICON_NAME_MAPPING = {
    'Adobe After Effects': 'skill-icons:aftereffects',
    'Adobe Illustrator': 'skill-icons:illustrator',
    'Adobe Photoshop': 'skill-icons:photoshop',
    'Adobe Premiere': 'skill-icons:premierepro',
    'Adobe XD': 'skill-icons:xd',
    'Amazon Web Services': 'skill-icons:aws',
    'C Sharp': 'skill-icons:cs',
    'CSS': 'skill-icons:css',
    'Express.js': 'skill-icons:expressjs',
    'FastAPI': 'skill-icons:fastapi',
    'HTML': 'skill-icons:html',
    'JavaScript': 'skill-icons:javascript',
    'MongoDB': 'skill-icons:mongodb',
    'Next.js': 'skill-icons:nextjs',
    'Node.js': 'skill-icons:nodejs',
    'PostgreSQL': 'skill-icons:postgresql',
    'Ruby on Rails': 'skill-icons:rails',
    'React.js': 'skill-icons:react',
    'TypeScript': 'skill-icons:typescript',
    'Vue.js': 'skill-icons:vuejs',
    'scikit-learn': 'skill-icons:scikitlearn',
    'Tailwind CSS': 'skill-icons:tailwindcss',
    'Unreal Engine': 'skill-icons:unrealengine',
    'WebAssembly': 'skill-icons:webassembly',
    'AI': 'eos-icons:ai',
    'AU': 'skill-icons:audition',
    'Bots': 'skill-icons:discordbots',
    'Express': 'skill-icons:expressjs',
    'Firebase': 'devicon:firebase',
    'Go': 'skill-icons:golang',
    'Markdown': 'skill-icons:markdown',
    'PowerShell': 'skill-icons:powershell',
    'PR': 'skill-icons:premiere',
    'Python': 'skill-icons:python-dark',
}

class BaseJobView(LoginRequiredMixin):
    """Base view for job-related operations"""
    model = JobPosting
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class JobListView(BaseJobView, ListView):
    """View for listing job postings"""
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']

class JobCreateView(BaseJobView, CreateView):
    """View for creating new job postings"""
    form_class = JobPostingForm
    template_name = 'jobs/add.html'
    success_url = reverse_lazy('jobs:list')

    def get(self, request, *args, **kwargs):
        """Handle GET request"""
        logger.debug("GET request received")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request"""
        logger.debug(f"POST request received: {request.POST}")
        if 'parse_description' in request.POST:
            return self.parse_description(request)
        return super().post(request, *args, **kwargs)

    def parse_description(self, request):
        if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                description = request.POST.get('paste', '')
                # Your existing AI parsing logic here to get parsed_data
                parsed_data = your_ai_parsing_function(description)
                
                # Create a form instance with the parsed data
                form = JobForm(initial=parsed_data)
                
                # Render form HTML snippets
                form_fields = {
                    'title': render_to_string('jobs/snippets/field.html', {'field': form['title']}),
                    'company': render_to_string('jobs/snippets/field.html', {'field': form['company']}),
                    'location': render_to_string('jobs/snippets/field.html', {'field': form['location']}),
                    'url': render_to_string('jobs/snippets/field.html', {'field': form['url']}),
                    'salary_range': render_to_string('jobs/snippets/field.html', {'field': form['salary_range']}),
                    'description': render_to_string('jobs/snippets/field.html', {'field': form['description']}),
                }
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Successfully parsed job description',
                    'fields': parsed_data,
                    'html': form_fields,
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    def form_invalid(self, form):
        """Handle invalid form"""
        logger.debug("Form validation failed")
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """Handle valid form submission"""
        try:
            # Set the user before saving
            form.instance.user = self.request.user
            self.object = form.save()
            
            # Handle AJAX requests
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Job posting created successfully',
                    'redirect_url': self.get_success_url()
                })
            
            # Handle regular form submission
            messages.success(self.request, 'Job posting created successfully')
            return super().form_valid(form)
            
        except Exception as e:
            logger.error(f"Error creating job posting: {str(e)}")
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error creating job posting'
                }, status=500)
            raise

    def form_invalid(self, form):
        """Handle invalid form submission"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the form errors',
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Add additional context if needed"""
        context = super().get_context_data(**kwargs)
        context['skill_icons'] = self._get_grouped_skills()
        return context

    def _get_grouped_skills(self):
        """Helper method to group skills"""
        skill_groups = {}
        for icon, name in SKILL_ICONS:
            first_letter = name[0].upper()
            if first_letter not in skill_groups:
                skill_groups[first_letter] = []
            
            skill_groups[first_letter].append({
                'name': name,
                'icon': ICON_NAME_MAPPING.get(name, icon),
                'icon_dark': DARK_VARIANTS.get(
                    ICON_NAME_MAPPING.get(name, icon),
                    ICON_NAME_MAPPING.get(name, icon)
                )
            })
        
        return [
            {
                'letter': letter,
                'skills': sorted(skills, key=lambda x: x['name'].upper())
            }
            for letter, skills in sorted(skill_groups.items())
        ]

class JobPostingUpdateView(BaseJobView, UpdateView):
    """View for updating existing job postings"""
    form_class = JobPostingForm
    template_name = 'jobs/edit.html'
    success_url = reverse_lazy('jobs:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Job posting updated successfully.')
        return response

class JobPostingDeleteView(BaseJobView, DeleteView):
    """View for deleting job postings"""
    template_name = 'jobs/delete.html'
    success_url = reverse_lazy('jobs:list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Job posting deleted successfully.')
        return response

class JobPostingDetailView(BaseJobView, DetailView):
    """View for displaying job details"""
    template_name = 'jobs/detail.html'
    context_object_name = 'job'

class JobFavoritesListView(BaseJobView, ListView):
    """View for displaying user's favourited jobs"""
    template_name = 'jobs/favourites.html'
    context_object_name = 'favorite_jobs'

    def get_queryset(self):
        return JobPosting.objects.filter(favourites=self.request.user)

# Remove or comment out the old function-based view:
# def favourited_jobs(request):
#     """Display user's favourited jobs"""
#     favorite_jobs = JobPosting.objects.filter(favourites=request.user)
#     return render(request, "jobs/favourites.html", {"favorite_jobs": favorite_jobs})

@login_required
def toggle_favourite(request, job_id):
    """Toggle favourite status of a job posting"""
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
        
    job = get_object_or_404(JobPosting, id=job_id)
    
    if request.user in job.favourites.all():
        job.favourites.remove(request.user)
        message = "Job removed from favourites"
    else:
        job.favourites.add(request.user)
        message = "Job added to favourites"
    
    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=200,
            headers={'HX-Trigger': json.dumps({'showMessage': {'message': message}})}
        )
        
    messages.success(request, message)
    return redirect("jobs:list")

def skills_autocomplete(request):
    """Handle skills autocomplete API requests"""
    query = request.GET.get('q', '').lower()
    results = [
        {
            'icon': icon,
            'label': name,
            'value': name.lower()
        }
        for icon, name in SKILL_ICONS
        if query in name.lower()
    ][:10]  # Limit to 10 results
    
    return JsonResponse({'results': results})

def get_skills_data(request):
    skills_data = [
        {
            'value': icon_key,
            'text': label,
            'icon': icon_key,
            'icon_dark': DARK_VARIANTS.get(icon_key, icon_key)  # Use mapping or fallback to original
        }
        for icon_key, label in SKILL_ICONS
    ]
    return JsonResponse(skills_data, safe=False)

@register.filter
def upper(value):
    if isinstance(value, dict):
        return {k: v.upper() if isinstance(v, str) else v for k, v in value.items()}
    return value.upper() if isinstance(value, str) else value

@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["POST"])
def parse_job_description(request):
    """Handle job description parsing"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
    
    paste_text = request.POST.get('paste', '').strip()
    if not paste_text:
        return JsonResponse({'status': 'error', 'message': 'No job description provided.'}, status=400)
    
    try:
        form = JobPostingForm()
        parsed = form.parse_job_with_ai(paste_text)
        if parsed:
            return JsonResponse({
                'status': 'success',
                'fields': parsed,
                'message': 'Successfully parsed job description.'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Could not parse job description.'
            }, status=400)
    except forms.ValidationError as ve:
        return JsonResponse({
            'status': 'error',
            'message': str(ve)
        }, status=400)
    except Exception as e:
        logger.exception("Error parsing job description")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred.'
        }, status=500)

@require_http_methods(["POST"])
def parse_job_description(request):
    """Handle job description parsing endpoint"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
    
    paste_text = request.POST.get('paste', '')
    if not paste_text:
        return JsonResponse({'status': 'error', 'message': 'No text provided'}, status=400)

    try:
        form = JobPostingForm()
        parsed_data = form.parse_job_with_ai(paste_text)
        
        logger.debug(f"Parsed data from AI: {parsed_data}")  # Add debug logging
        
        if parsed_data:
            # Ensure field names match form field IDs
            response_data = {
                'status': 'success',
                'message': 'Successfully parsed job description',
                'fields': {
                    'title': parsed_data.get('title', ''),
                    'company': parsed_data.get('company', ''),
                    'location': parsed_data.get('location', ''),
                    'url': parsed_data.get('url', ''),
                    'salary_range': parsed_data.get('salary_range', ''),
                    'description': parsed_data.get('description', ''),
                    'status': 'NEW'  # Default status
                }
            }
            
            # Handle both HTMX and regular AJAX requests
            if request.headers.get('HX-Request'):
                context = {'form': form, 'parsed_data': parsed_data}
                html = render_to_string('jobs/snippets/field.html', context)
                response_data['html'] = html
            
            logger.debug(f"Sending response: {response_data}")  # Add debug logging
            return JsonResponse(response_data)
            
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to parse description'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Error parsing job description: {str(e)}")
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=500)
