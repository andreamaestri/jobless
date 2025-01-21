"""Module containing skill icon mappings and utilities"""

# Base icons that have both dark and light variants
THEME_VARIANTS = [
    'ableton', 'activitypub', 'actix', 'aiscript', 'alpinejs', 'androidstudio',
    'angular', 'autocad', 'aws', 'azure', 'bash', 'bevy', 'blender', 'bsd',
    'cassandra', 'clojure', 'cloudflare', 'cmake', 'codepen', 'coffeescript',
    'crystal', 'd3', 'dart', 'deno', 'devto', 'dynamodb', 'eclipse', 'elixir',
    'emotion', 'expressjs', 'fediverse', 'figma', 'flask', 'flutter', 'gcp',
    'gherkin', 'github', 'githubactions', 'gitlab', 'godot', 'gradle', 'grafana',
    'graphql', 'gtk', 'haskell', 'haxe', 'haxeflixel', 'hibernate', 'idea',
    'ipfs', 'java', 'jenkins', 'julia', 'kotlin', 'ktor', 'laravel', 'latex',
    'linux', 'lit', 'lua', 'markdown', 'mastodon', 'materialui', 'matlab',
    'maven', 'misskey', 'mysql', 'neovim', 'nestjs', 'netlify', 'nextjs',
    'nim', 'nodejs', 'nuxtjs', 'octave', 'openstack', 'php', 'plan9',
    'planetscale', 'postgresql', 'powershell', 'processing', 'pug', 'python',
    'pytorch', 'qt', 'r', 'rabbitmq', 'raspberrypi', 'react', 'reactivex',
    'redis', 'regex', 'remix', 'replit', 'rollupjs', 'ros', 'scala',
    'sequelize', 'sketchup', 'solidjs', 'spring', 'stackoverflow', 'supabase',
    'svg', 'symfony', 'tailwindcss', 'tauri', 'tensorflow', 'threejs',
    'unity', 'v', 'vercel', 'vim', 'visualstudio', 'vite', 'vscode',
    'vuejs', 'webpack', 'windicss', 'workers', 'zig'
]

# Icons that only have one variant
SINGLE_VARIANT_ICONS = [
    'adonis', 'aftereffects', 'ansible', 'apollo', 'appwrite', 'arduino',
    'astro', 'atom', 'audition', 'azul', 'babel', 'bootstrap', 'c', 'cpp',
    'cs', 'css', 'discord', 'discordbots', 'django', 'docker', 'dotnet',
    'electron', 'emacs', 'ember', 'fastapi', 'forth', 'fortran',
    'gamemakerstudio', 'gatsby', 'git', 'golang', 'gulp', 'heroku', 'html',
    'illustrator', 'instagram', 'javascript', 'jest', 'jquery', 'kafka',
    'kubernetes', 'linkedin', 'mongodb', 'nginx', 'ocaml', 'openshift',
    'perl', 'photoshop', 'postman', 'premiere', 'prisma', 'prometheus',
    'rails', 'redux', 'rocket', 'ruby', 'rust', 'sass', 'selenium',
    'sentry', 'solidity', 'sqlite', 'styledcomponents', 'svelte', 'swift',
    'twitter', 'typescript', 'unrealengine', 'vala', 'webassembly',
    'webflow', 'wordpress', 'xd'
]

# Generate DARK_VARIANTS for backward compatibility
DARK_VARIANTS = {}
for base_name in THEME_VARIANTS:
    icon_name = f'skill-icons:{base_name}'
    DARK_VARIANTS[icon_name] = f'{icon_name}-dark'

# Add any single variants that might have dark variants in the original
for icon_name in SINGLE_VARIANT_ICONS:
    full_name = f'skill-icons:{icon_name}'
    if icon_name in ['javascript', 'typescript', 'html', 'css']:  # Add any special cases
        DARK_VARIANTS[full_name] = full_name  # These don't have dark variants

# Generate full icon list with variants
SKILL_ICONS = []

# Add theme variant icons (maintain the same structure as before)
for base_name in THEME_VARIANTS:
    icon_name = f'skill-icons:{base_name}'
    dark_name = f'{icon_name}-dark'
    # Add only the dark variant to maintain backward compatibility
    SKILL_ICONS.append((dark_name, base_name.title()))

# Add single variant icons
for icon_name in SINGLE_VARIANT_ICONS:
    full_name = f'skill-icons:{icon_name}'
    SKILL_ICONS.append((full_name, icon_name.title()))

# Convert to tuple for immutability
SKILL_ICONS = tuple(SKILL_ICONS)

# Icon name mapping for backward compatibility
ICON_NAME_MAPPING = {
    # .NET Platform (single standardized naming)
    '.NET': 'skill-icons:dotnet',  # Keep only this one entry for .NET
    
    # Programming Languages
    'Python': 'skill-icons:python-dark',
    'py': 'skill-icons:python-dark',
    'JavaScript': 'skill-icons:javascript',
    'JS': 'skill-icons:javascript',
    'TypeScript': 'skill-icons:typescript',
    'TS': 'skill-icons:typescript',
    'Java': 'skill-icons:java-dark',
    'Kotlin': 'skill-icons:kotlin-dark',
    'Swift': 'skill-icons:swift',
    'Rust': 'skill-icons:rust',
    'Go': 'skill-icons:golang',
    'Golang': 'skill-icons:golang',
    'C++': 'skill-icons:cpp',
    'Cpp': 'skill-icons:cpp',
    'C Plus Plus': 'skill-icons:cpp',
    'C#': 'skill-icons:cs',
    'C Sharp': 'skill-icons:cs',
    'CSharp': 'skill-icons:cs',
    'Ruby': 'skill-icons:ruby',
    'PHP': 'skill-icons:php-dark',
    'R': 'skill-icons:r-dark',
    'Scala': 'skill-icons:scala-dark',
    'Perl': 'skill-icons:perl',
    'Haskell': 'skill-icons:haskell-dark',
    'Lua': 'skill-icons:lua-dark',
    'Julia': 'skill-icons:julia-dark',
    'Clojure': 'skill-icons:clojure-dark',
    'Elixir': 'skill-icons:elixir-dark',
    'Dart': 'skill-icons:dart-dark',
    
    # Web Technologies
    'HTML': 'skill-icons:html',
    'HTML5': 'skill-icons:html',
    'CSS': 'skill-icons:css',
    'CSS3': 'skill-icons:css',
    'Sass': 'skill-icons:sass',
    'SCSS': 'skill-icons:sass',
    'Less': 'skill-icons:less-dark',
    'Stylus': 'skill-icons:stylus',
    
    # Frontend Frameworks/Libraries
    'React': 'skill-icons:react-dark',
    'React.js': 'skill-icons:react-dark',
    'ReactJS': 'skill-icons:react-dark',
    'Vue': 'skill-icons:vuejs-dark',
    'Vue.js': 'skill-icons:vuejs-dark',
    'VueJS': 'skill-icons:vuejs-dark',
    'Angular': 'skill-icons:angular-dark',
    'AngularJS': 'skill-icons:angular-dark',
    'Svelte': 'skill-icons:svelte',
    'SvelteKit': 'skill-icons:svelte',
    'Next': 'skill-icons:nextjs-dark',
    'Next.js': 'skill-icons:nextjs-dark',
    'NextJS': 'skill-icons:nextjs-dark',
    'Nuxt': 'skill-icons:nuxtjs-dark',
    'Nuxt.js': 'skill-icons:nuxtjs-dark',
    'NuxtJS': 'skill-icons:nuxtjs-dark',
    
    # Backend Frameworks
    'Django': 'skill-icons:django',
    'Flask': 'skill-icons:flask-dark',
    'FastAPI': 'skill-icons:fastapi',
    'Express': 'skill-icons:expressjs-dark',
    'Express.js': 'skill-icons:expressjs-dark',
    'ExpressJS': 'skill-icons:expressjs-dark',
    'Spring': 'skill-icons:spring-dark',
    'Spring Boot': 'skill-icons:spring-dark',
    'Laravel': 'skill-icons:laravel-dark',
    'Rails': 'skill-icons:rails',
    'Ruby on Rails': 'skill-icons:rails',
    'NestJS': 'skill-icons:nestjs-dark',
    'Nest.js': 'skill-icons:nestjs-dark',
    
    # Databases
    'PostgreSQL': 'skill-icons:postgresql-dark',
    'Postgres': 'skill-icons:postgresql-dark',
    'MySQL': 'skill-icons:mysql-dark',
    'MongoDB': 'skill-icons:mongodb',
    'Redis': 'skill-icons:redis-dark',
    'SQLite': 'skill-icons:sqlite',
    'Cassandra': 'skill-icons:cassandra-dark',
    'DynamoDB': 'skill-icons:dynamodb-dark',
    'MariaDB': 'skill-icons:mysql-dark',
    
    # Cloud Services
    'AWS': 'skill-icons:aws-dark',
    'Amazon Web Services': 'skill-icons:aws-dark',
    'Azure': 'skill-icons:azure-dark',
    'Microsoft Azure': 'skill-icons:azure-dark',
    'GCP': 'skill-icons:gcp-dark',
    'Google Cloud': 'skill-icons:gcp-dark',
    'Google Cloud Platform': 'skill-icons:gcp-dark',
    'Heroku': 'skill-icons:heroku',
    'DigitalOcean': 'skill-icons:digitalocean',
    'Vercel': 'skill-icons:vercel-dark',
    'Netlify': 'skill-icons:netlify-dark',
    
    # DevOps & Tools
    'Git': 'skill-icons:git',
    'GitHub': 'skill-icons:github-dark',
    'GitLab': 'skill-icons:gitlab-dark',
    'Bitbucket': 'skill-icons:bitbucket-dark',
    'Docker': 'skill-icons:docker',
    'Kubernetes': 'skill-icons:kubernetes',
    'K8s': 'skill-icons:kubernetes',
    'Jenkins': 'skill-icons:jenkins-dark',
    'Terraform': 'skill-icons:terraform-dark',
    'Ansible': 'skill-icons:ansible',
    'Nginx': 'skill-icons:nginx',
    'Apache': 'skill-icons:apache',
    
    # Package Managers
    'NPM': 'skill-icons:npm',
    'Yarn': 'skill-icons:yarn-dark',
    'PNPM': 'skill-icons:pnpm-dark',
    'Pip': 'skill-icons:python-dark',
    'Conda': 'skill-icons:anaconda-dark',
    
    # Build Tools
    'Webpack': 'skill-icons:webpack-dark',
    'Vite': 'skill-icons:vite-dark',
    'Rollup': 'skill-icons:rollupjs-dark',
    'Babel': 'skill-icons:babel',
    'Gradle': 'skill-icons:gradle-dark',
    'Maven': 'skill-icons:maven-dark',
    
    # Mobile Development
    'Flutter': 'skill-icons:flutter-dark',
    'React Native': 'skill-icons:react-dark',
    'Xamarin': 'skill-icons:xamarin',
    'Android': 'skill-icons:androidstudio-dark',
    'iOS': 'skill-icons:apple-dark',
    
    # AI/ML
    'TensorFlow': 'skill-icons:tensorflow-dark',
    'PyTorch': 'skill-icons:pytorch-dark',
    'Keras': 'skill-icons:tensorflow-dark',
    'scikit-learn': 'skill-icons:scikitlearn-dark',
    'Sklearn': 'skill-icons:scikitlearn-dark',
    
    # IDE/Editors
    'VS Code': 'skill-icons:vscode-dark',
    'Visual Studio Code': 'skill-icons:vscode-dark',
    'VSCode': 'skill-icons:vscode-dark',
    'Visual Studio': 'skill-icons:visualstudio-dark',
    'IntelliJ': 'skill-icons:idea-dark',
    'IntelliJ IDEA': 'skill-icons:idea-dark',
    'PyCharm': 'skill-icons:pycharm-dark',
    'WebStorm': 'skill-icons:webstorm-dark',
    'Vim': 'skill-icons:vim-dark',
    'Neovim': 'skill-icons:neovim-dark',
    
    # UI Libraries
    'Tailwind': 'skill-icons:tailwindcss-dark',
    'TailwindCSS': 'skill-icons:tailwindcss-dark',
    'Tailwind CSS': 'skill-icons:tailwindcss-dark',
    'Bootstrap': 'skill-icons:bootstrap',
    'Material UI': 'skill-icons:materialui-dark',
    'MUI': 'skill-icons:materialui-dark',
    'Chakra UI': 'skill-icons:chakraui',
    'Vuetify': 'skill-icons:vuetify-dark',
    
    # Operating Systems
    'Linux': 'skill-icons:linux-dark',
    'Ubuntu': 'skill-icons:ubuntu-dark',
    'Debian': 'skill-icons:debian-dark',
    'Windows': 'skill-icons:windows-dark',
    'macOS': 'skill-icons:apple-dark',
    
    # Testing
    'Jest': 'skill-icons:jest',
    'Cypress': 'skill-icons:cypress-dark',
    'Selenium': 'skill-icons:selenium',
    'Vitest': 'skill-icons:vitest-dark',
    
    # Other
    'GraphQL': 'skill-icons:graphql-dark',
    'REST': 'skill-icons:postman',
    'RESTful': 'skill-icons:postman',
    'REST API': 'skill-icons:postman',
    'WebSocket': 'skill-icons:nodejs-dark',
    'WebSockets': 'skill-icons:nodejs-dark',
    'Web Components': 'skill-icons:html',
}

def get_icon_variant(base_name, theme='dark'):
    """Helper function to get the appropriate icon variant"""
    if base_name in THEME_VARIANTS:
        return f'skill-icons:{base_name}-{theme}'
    return f'skill-icons:{base_name}'

# Update mapping with theme variants
for base_name in THEME_VARIANTS:
    display_name = base_name.replace('-', ' ').title()
    ICON_NAME_MAPPING[display_name] = f'skill-icons:{base_name}-dark'  # Default to dark

# Add single variant mappings
for icon_name in SINGLE_VARIANT_ICONS:
    display_name = icon_name.replace('-', ' ').title()
    ICON_NAME_MAPPING[display_name] = f'skill-icons:{icon_name}'
