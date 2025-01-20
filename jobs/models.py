from django.db import models
from django.conf import settings
from django.urls import reverse
from tagulous.models import TagField
from django.contrib.auth.models import User
import tagulous.models

SKILL_ICONS = (
    ('skill-icons:ableton', 'Ableton'),
    ('skill-icons:activitypub', 'ActivityPub'),
    ('skill-icons:actix', 'Actix'),
    ('skill-icons:adonis', 'Adonis'),
    ('skill-icons:ae', 'Adobe After Effects'),
    ('skill-icons:aiscript', 'AIScript'),
    ('skill-icons:alpinejs', 'Alpine.js'),
    ('skill-icons:anaconda', 'Anaconda'),
    ('skill-icons:androidstudio', 'Android Studio'),
    ('skill-icons:angular', 'Angular'),
    ('skill-icons:ansible', 'Ansible'),
    ('skill-icons:apollo', 'Apollo'),
    ('skill-icons:apple', 'Apple'),
    ('skill-icons:appwrite', 'Appwrite'),
    ('skill-icons:arch', 'Arch Linux'),
    ('skill-icons:arduino', 'Arduino'),
    ('skill-icons:astro', 'Astro'),
    ('skill-icons:atom', 'Atom'),
    ('skill-icons:au', 'AU'),
    ('skill-icons:autocad', 'AutoCAD'),
    ('skill-icons:aws', 'AWS'),
    ('skill-icons:azul', 'Azul'),
    ('skill-icons:azure', 'Azure'),
    ('skill-icons:babel', 'Babel'),
    ('skill-icons:bash', 'Bash'),
    ('skill-icons:bevy', 'Bevy'),
    ('skill-icons:bitbucket', 'Bitbucket'),
    ('skill-icons:blender', 'Blender'),
    ('skill-icons:bootstrap', 'Bootstrap'),
    ('skill-icons:bsd', 'BSD'),
    ('skill-icons:bun', 'Bun'),
    ('skill-icons:c', 'C'),
    ('skill-icons:cs', 'C#'),
    ('skill-icons:cpp', 'C++'),
    ('skill-icons:crystal', 'Crystal'),
    ('skill-icons:cassandra', 'Cassandra'),
    ('skill-icons:clion', 'CLion'),
    ('skill-icons:clojure', 'Clojure'),
    ('skill-icons:cloudflare', 'Cloudflare'),
    ('skill-icons:cmake', 'CMake'),
    ('skill-icons:codepen', 'CodePen'),
    ('skill-icons:coffeescript', 'CoffeeScript'),
    ('skill-icons:css', 'CSS'),
    ('skill-icons:cypress', 'Cypress'),
    ('skill-icons:d3', 'D3.js'),
    ('skill-icons:dart', 'Dart'),
    ('skill-icons:debian', 'Debian'),
    ('skill-icons:deno', 'Deno'),
    ('skill-icons:devto', 'Dev.to'),
    ('skill-icons:discord', 'Discord'),
    ('skill-icons:bots', 'Bots'),
    ('skill-icons:discordjs', 'Discord.js'),
    ('skill-icons:django', 'Django'),
    ('skill-icons:docker', 'Docker'),
    ('skill-icons:dotnet', '.NET'),
    ('skill-icons:dynamodb', 'DynamoDB'),
    ('skill-icons:eclipse', 'Eclipse'),
    ('skill-icons:elasticsearch', 'Elasticsearch'),
    ('skill-icons:electron', 'Electron'),
    ('skill-icons:elixir', 'Elixir'),
    ('skill-icons:elysia', 'Elysia'),
    ('skill-icons:emacs', 'Emacs'),
    ('skill-icons:ember', 'Ember'),
    ('skill-icons:emotion', 'Emotion'),
    ('skill-icons:express', 'Express'),
    ('skill-icons:fastapi', 'FastAPI'),
    ('skill-icons:fediverse', 'Fediverse'),
    ('skill-icons:figma', 'Figma'),
    ('skill-icons:firebase', 'Firebase'),
    ('skill-icons:flask', 'Flask'),
    ('skill-icons:flutter', 'Flutter'),
    ('skill-icons:forth', 'Forth'),
    ('skill-icons:fortran', 'Fortran'),
    ('skill-icons:gamemakerstudio', 'GameMaker Studio'),
    ('skill-icons:gatsby', 'Gatsby'),
    ('skill-icons:gcp', 'Google Cloud Platform'),
    ('skill-icons:git', 'Git'),
    ('skill-icons:github', 'GitHub'),
    ('skill-icons:githubactions', 'GitHub Actions'),
    ('skill-icons:gitlab', 'GitLab'),
    ('skill-icons:gmail', 'Gmail'),
    ('skill-icons:gherkin', 'Gherkin'),
    ('skill-icons:go', 'Go'),
    ('skill-icons:gradle', 'Gradle'),
    ('skill-icons:godot', 'Godot'),
    ('skill-icons:grafana', 'Grafana'),
    ('skill-icons:graphql', 'GraphQL'),
    ('skill-icons:gtk', 'GTK'),
    ('skill-icons:gulp', 'Gulp'),
    ('skill-icons:haskell', 'Haskell'),
    ('skill-icons:haxe', 'Haxe'),
    ('skill-icons:haxeflixel', 'HaxeFlixel'),
    ('skill-icons:heroku', 'Heroku'),
    ('skill-icons:hibernate', 'Hibernate'),
    ('skill-icons:html', 'HTML'),
    ('skill-icons:htmx', 'HTMX'),
    ('skill-icons:idea', 'IntelliJ IDEA'),
    ('skill-icons:ai', 'AI'),
    ('skill-icons:instagram', 'Instagram'),
    ('skill-icons:ipfs', 'IPFS'),
    ('skill-icons:java', 'Java'),
    ('skill-icons:js', 'JavaScript'),
    ('skill-icons:jenkins', 'Jenkins'),
    ('skill-icons:jest', 'Jest'),
    ('skill-icons:jquery', 'jQuery'),
    ('skill-icons:kafka', 'Kafka'),
    ('skill-icons:kali', 'Kali Linux'),
    ('skill-icons:kotlin', 'Kotlin'),
    ('skill-icons:ktor', 'Ktor'),
    ('skill-icons:kubernetes', 'Kubernetes'),
    ('skill-icons:laravel', 'Laravel'),
    ('skill-icons:latex', 'LaTeX'),
    ('skill-icons:less', 'Less'),
    ('skill-icons:linkedin', 'LinkedIn'),
    ('skill-icons:linux', 'Linux'),
    ('skill-icons:lit', 'Lit'),
    ('skill-icons:lua', 'Lua'),
    ('skill-icons:md', 'Markdown'),
    ('skill-icons:mastodon', 'Mastodon'),
    ('skill-icons:materialui', 'Material-UI'),
    ('skill-icons:matlab', 'MATLAB'),
    ('skill-icons:maven', 'Maven'),
    ('skill-icons:mint', 'Mint'),
    ('skill-icons:misskey', 'Misskey'),
    ('skill-icons:mongodb', 'MongoDB'),
    ('skill-icons:mysql', 'MySQL'),
    ('skill-icons:neovim', 'Neovim'),
    ('skill-icons:nestjs', 'NestJS'),
    ('skill-icons:netlify', 'Netlify'),
    ('skill-icons:nextjs', 'Next.js'),
    ('skill-icons:nginx', 'Nginx'),
    ('skill-icons:nim', 'Nim'),
    ('skill-icons:nix', 'Nix'),
    ('skill-icons:nodejs', 'Node.js'),
    ('skill-icons:notion', 'Notion'),
    ('skill-icons:npm', 'NPM'),
    ('skill-icons:nuxtjs', 'Nuxt.js'),
    ('skill-icons:obsidian', 'Obsidian'),
    ('skill-icons:ocaml', 'OCaml'),
    ('skill-icons:octave', 'Octave'),
    ('skill-icons:opencv', 'OpenCV'),
    ('skill-icons:openshift', 'OpenShift'),
    ('skill-icons:openstack', 'OpenStack'),
    ('skill-icons:p5js', 'p5.js'),
    ('skill-icons:perl', 'Perl'),
    ('skill-icons:ps', 'PowerShell'),
    ('skill-icons:php', 'PHP'),
    ('skill-icons:phpstorm', 'PhpStorm'),
    ('skill-icons:pinia', 'Pinia'),
    ('skill-icons:pkl', 'PKL'),
    ('skill-icons:plan9', 'Plan 9'),
    ('skill-icons:planetscale', 'PlanetScale'),
    ('skill-icons:pnpm', 'PNPM'),
    ('skill-icons:postgres', 'PostgreSQL'),
    ('skill-icons:postman', 'Postman'),
    ('skill-icons:powershell', 'PowerShell'),
    ('skill-icons:pr', 'PR'),
    ('skill-icons:prisma', 'Prisma'),
    ('skill-icons:processing', 'Processing'),
    ('skill-icons:prometheus', 'Prometheus'),
    ('skill-icons:pug', 'Pug'),
    ('skill-icons:pycharm', 'PyCharm'),
    ('skill-icons:py', 'Python'),
    ('skill-icons:pytorch', 'PyTorch'),
    ('skill-icons:qt', 'Qt'),
    ('skill-icons:r', 'R'),
    ('skill-icons:rabbitmq', 'RabbitMQ'),
    ('skill-icons:rails', 'Rails'),
    ('skill-icons:raspberrypi', 'Raspberry Pi'),
    ('skill-icons:react', 'React'),
    ('skill-icons:reactivex', 'ReactiveX'),
    ('skill-icons:redhat', 'Red Hat'),
    ('skill-icons:redis', 'Redis'),
    ('skill-icons:redux', 'Redux'),
    ('skill-icons:regex', 'Regex'),
    ('skill-icons:remix', 'Remix'),
    ('skill-icons:replit', 'Replit'),
    ('skill-icons:rider', 'Rider'),
    ('skill-icons:robloxstudio', 'Roblox Studio'),
    ('skill-icons:rocket', 'Rocket'),
    ('skill-icons:rollupjs', 'Rollup.js'),
    ('skill-icons:ros', 'ROS'),
    ('skill-icons:ruby', 'Ruby'),
    ('skill-icons:rust', 'Rust'),
    ('skill-icons:sass', 'Sass'),
    ('skill-icons:spring', 'Spring'),
    ('skill-icons:sqlite', 'SQLite'),
    ('skill-icons:stackoverflow', 'Stack Overflow'),
    ('skill-icons:styledcomponents', 'Styled Components'),
    ('skill-icons:sublime', 'Sublime Text'),
    ('skill-icons:supabase', 'Supabase'),
    ('skill-icons:scala', 'Scala'),
    ('skill-icons:sklearn', 'scikit-learn'),
    ('skill-icons:selenium', 'Selenium'),
    ('skill-icons:sentry', 'Sentry'),
    ('skill-icons:sequelize', 'Sequelize'),
    ('skill-icons:sketchup', 'SketchUp'),
    ('skill-icons:solidity', 'Solidity'),
    ('skill-icons:solidjs', 'SolidJS'),
    ('skill-icons:svelte', 'Svelte'),
    ('skill-icons:svg', 'SVG'),
    ('skill-icons:swift', 'Swift'),
    ('skill-icons:symfony', 'Symfony'),
    ('skill-icons:tailwind', 'Tailwind CSS'),
    ('skill-icons:tauri', 'Tauri'),
    ('skill-icons:tensorflow', 'TensorFlow'),
    ('skill-icons:terraform', 'Terraform'),
    ('skill-icons:threejs', 'Three.js'),
    ('skill-icons:twitter', 'Twitter'),
    ('skill-icons:ts', 'TypeScript'),
    ('skill-icons:ubuntu', 'Ubuntu'),
    ('skill-icons:unity', 'Unity'),
    ('skill-icons:unreal', 'Unreal Engine'),
    ('skill-icons:v', 'V'),
    ('skill-icons:vala', 'Vala'),
    ('skill-icons:vercel', 'Vercel'),
    ('skill-icons:vim', 'Vim'),
    ('skill-icons:visualstudio', 'Visual Studio'),
    ('skill-icons:vite', 'Vite'),
    ('skill-icons:vitest', 'Vitest'),
    ('skill-icons:vscode', 'VS Code'),
    ('skill-icons:vscodium', 'VSCodium'),
    ('skill-icons:vue', 'Vue.js'),
    ('skill-icons:vuetify', 'Vuetify'),
    ('skill-icons:wasm', 'WebAssembly'),
    ('skill-icons:webflow', 'Webflow'),
    ('skill-icons:webpack', 'Webpack'),
    ('skill-icons:webstorm', 'WebStorm'),
    ('skill-icons:windicss', 'WindiCSS'),
    ('skill-icons:windows', 'Windows'),
    ('skill-icons:wordpress', 'WordPress'),
    ('skill-icons:workers', 'Workers'),
    ('skill-icons:xd', 'Adobe XD'),
    ('skill-icons:yarn', 'Yarn'),
    ('skill-icons:yew', 'Yew'),
    ('skill-icons:zig', 'Zig')
)


class SkillsTagModel(tagulous.models.TagModel):
    class TagMeta:
        initial = SKILL_ICONS
        force_lowercase = True
        autocomplete_view = 'jobs:skills_autocomplete'
        space_delimiter = False
        max_count = 10
        case_sensitive = False

    def get_icon(self):
        """Get the icon for this skill"""
        for icon, name in SKILL_ICONS:
            if name.lower() == str(self).lower():
                return icon
        return 'heroicons:academic-cap'  # Default icon

class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('interested', 'Interested'),
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary_range = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    description = models.TextField()
    skills = tagulous.models.TagField(
        to=SkillsTagModel,
        help_text="Select skills from the predefined list",
        blank=True,
        related_name="job_skills"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='interested')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourites = models.ManyToManyField(User, related_name="favourited_jobs", blank=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})
