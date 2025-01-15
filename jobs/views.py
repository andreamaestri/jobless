from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
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
from django import template

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

class JobPostingListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of job postings for the logged-in user.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        ListView: Handles listing of JobPosting objects

    Attributes:
        model: JobPosting model
        template_name: Path to the list template
        context_object_name: Name used for the job list in template context
    """
    model = JobPosting
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return JobPosting.objects.filter(user=self.request.user)


class JobPostingCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new job posting entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        CreateView: Handles creation of JobPosting objects

    Attributes:
        model: JobPosting model
        form_class: Form class for job posting creation
        template_name: Path to the creation template
        success_url: URL to redirect to after successful creation
    """
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/add.html'
    success_url = reverse_lazy('jobs:list')

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': form.errors,
                'message': 'Validation failed'
            }, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if self.request.POST.get('process_paste') == 'true':
                paste_text = self.request.POST.get('paste')
                if paste_text:
                    try:
                        parsed = form.parse_job_with_ai(paste_text)
                        if parsed:
                            return JsonResponse({'fields': parsed})
                        return JsonResponse({
                            'error': 'Could not parse text',
                            'message': 'AI processing failed'
                        }, status=400)
                    except Exception as e:
                        return JsonResponse({
                            'error': str(e),
                            'message': 'Processing error'
                        }, status=400)
                return JsonResponse({
                    'error': 'No text provided',
                    'message': 'Please provide text to process'
                }, status=400)
        
        form.instance.user = self.request.user
        messages.success(self.request, 'Job posting added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create groups by uppercase first letter
        skill_groups = {}
        for icon, name in SKILL_ICONS:
            first_letter = name[0].upper()
            if (first_letter not in skill_groups):
                skill_groups[first_letter] = []
                
            skill_groups[first_letter].append({
                'name': name,
                'icon': ICON_NAME_MAPPING.get(name, icon),
                'icon_dark': DARK_VARIANTS.get(ICON_NAME_MAPPING.get(name, icon), ICON_NAME_MAPPING.get(name, icon))
            })
        
        # Convert to sorted list of tuples (letter, skills)
        context['skill_icons'] = [
            {'letter': letter, 'skills': sorted(skills, key=lambda x: x['name'].upper())}
            for letter, skills in sorted(skill_groups.items())
        ]
        return context


class JobPostingUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating existing job posting entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        UpdateView: Handles updating of JobPosting objects

    Attributes:
        model: JobPosting model
        form_class: Form class for job posting updating
        template_name: Path to the edit template
        success_url: URL to redirect to after successful update
    """
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/edit.html'
    success_url = reverse_lazy('jobs:list')

    def get_queryset(self):
        # Ensure users can only edit their own job postings
        return JobPosting.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Job posting updated successfully.')
        return super().form_valid(form)


class JobPostingDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting job posting entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        DeleteView: Handles deletion of JobPosting objects

    Attributes:
        model: JobPosting model
        template_name: Path to the deletion confirmation template
        success_url: URL to redirect to after successful deletion
    """
    model = JobPosting
    template_name = 'jobs/delete.html'
    success_url = reverse_lazy('jobs:list')

    def get_queryset(self):
        # Ensure users can only delete their own job postings
        return JobPosting.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Job posting deleted successfully.')
        return super().delete(request, *args, **kwargs)


class JobPostingDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying detailed information about a job posting.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        DetailView: Handles displaying detailed view of JobPosting objects

    Attributes:
        model: JobPosting model
        template_name: Path to the detail template
        context_object_name: Name used for the job posting in template context
    """
    model = JobPosting
    template_name = 'jobs/detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        # Ensure users can only view their own job postings
        return JobPosting.objects.filter(user=self.request.user)
    
def toggle_favourite(request, job_id):
    """Toggle favourite status of a job posting"""
    job = get_object_or_404(JobPosting, id=job_id)
    
    if request.method == "POST":
        if request.user in job.favourites.all():
            job.favourites.remove(request.user)
            messages.success(request, "Job removed from favourites!")
        else:
            job.favourites.add(request.user)
            messages.success(request, "Job added to favourites!")
    
    return redirect("jobs:list")


def favourited_jobs(request):
    """Display user's favourited jobs"""
    favorite_jobs = JobPosting.objects.filter(favourites=request.user)
    return render(request, "jobs/favourites.html", {"favorite_jobs": favorite_jobs})

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
    """Handle HTMX request to parse job description"""
    paste_text = request.POST.get('paste', '').strip()
    
    if not paste_text:
        return HttpResponse(
            render_to_string('jobs/partials/alert.html', {
                'type': 'warning',
                'message': 'Please paste some text first'
            }),
            status=400
        )

    try:
        form = JobPostingForm()
        parsed = form.parse_job_with_ai(paste_text)
        
        if not parsed:
            return HttpResponse(
                render_to_string('jobs/partials/alert.html', {
                    'type': 'error',
                    'message': 'Could not extract job details. Please check the text format.'
                }),
                status=400
            )
            
        # Return rendered form fields with parsed data
        context = {'parsed': parsed}
        return HttpResponse(
            render_to_string('jobs/partials/form_fields.html', context)
        )

    except Exception as e:
        logger.error(f"Error in parse_job_description: {str(e)}")
        return HttpResponse(
            render_to_string('jobs/partials/alert.html', {
                'type': 'error',
                'message': f'Error processing job description: {str(e)}'
            }),
            status=400
        )
