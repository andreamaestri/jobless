# Generated by Django 5.1.4 on 2025-01-22 09:34

import django.db.models.deletion
import tagulous.models.fields
import tagulous.models.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SkillsTagModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField()),
                (
                    "count",
                    models.IntegerField(
                        default=0,
                        help_text="Internal counter of how many times this tag is in use",
                    ),
                ),
                (
                    "protected",
                    models.BooleanField(
                        default=False,
                        help_text="Will not be deleted when the count reaches 0",
                    ),
                ),
                ("icon", models.CharField(blank=True, max_length=100, null=True)),
                ("icon_dark", models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                "verbose_name": "Skill",
                "verbose_name_plural": "Skills",
            },
            bases=(tagulous.models.models.BaseTagModel, models.Model),
        ),
        migrations.CreateModel(
            name="JobPosting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("company", models.CharField(max_length=200)),
                ("location", models.CharField(max_length=200)),
                ("salary_range", models.CharField(blank=True, max_length=100)),
                ("url", models.URLField(blank=True)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("interested", "Interested"),
                            ("applied", "Applied"),
                            ("interviewing", "Interviewing"),
                            ("rejected", "Rejected"),
                            ("accepted", "Accepted"),
                        ],
                        default="interested",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "favorite_users",
                    models.ManyToManyField(
                        blank=True,
                        related_name="favorited_postings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "skills",
                    tagulous.models.fields.TagField(
                        _set_tag_meta=True,
                        autocomplete_view="jobs:skills_autocomplete",
                        blank=True,
                        case_sensitive=False,
                        force_lowercase=True,
                        help_text="Select skills from the predefined list",
                        initial="\"('skill-icons:ableton-dark', 'Ableton')\", \"('skill-icons:activitypub-dark', 'Activitypub')\", \"('skill-icons:actix-dark', 'Actix')\", \"('skill-icons:adonis', 'Adonis')\", \"('skill-icons:aftereffects', 'Aftereffects')\", \"('skill-icons:aiscript-dark', 'Aiscript')\", \"('skill-icons:alpinejs-dark', 'Alpinejs')\", \"('skill-icons:androidstudio-dark', 'Androidstudio')\", \"('skill-icons:angular-dark', 'Angular')\", \"('skill-icons:ansible', 'Ansible')\", \"('skill-icons:apollo', 'Apollo')\", \"('skill-icons:appwrite', 'Appwrite')\", \"('skill-icons:arduino', 'Arduino')\", \"('skill-icons:astro', 'Astro')\", \"('skill-icons:atom', 'Atom')\", \"('skill-icons:audition', 'Audition')\", \"('skill-icons:autocad-dark', 'Autocad')\", \"('skill-icons:aws-dark', 'Aws')\", \"('skill-icons:azul', 'Azul')\", \"('skill-icons:azure-dark', 'Azure')\", \"('skill-icons:babel', 'Babel')\", \"('skill-icons:bash-dark', 'Bash')\", \"('skill-icons:bevy-dark', 'Bevy')\", \"('skill-icons:blender-dark', 'Blender')\", \"('skill-icons:bootstrap', 'Bootstrap')\", \"('skill-icons:bsd-dark', 'Bsd')\", \"('skill-icons:c', 'C')\", \"('skill-icons:cassandra-dark', 'Cassandra')\", \"('skill-icons:clojure-dark', 'Clojure')\", \"('skill-icons:cloudflare-dark', 'Cloudflare')\", \"('skill-icons:cmake-dark', 'Cmake')\", \"('skill-icons:codepen-dark', 'Codepen')\", \"('skill-icons:coffeescript-dark', 'Coffeescript')\", \"('skill-icons:cpp', 'Cpp')\", \"('skill-icons:crystal-dark', 'Crystal')\", \"('skill-icons:cs', 'Cs')\", \"('skill-icons:css', 'Css')\", \"('skill-icons:d3-dark', 'D3')\", \"('skill-icons:dart-dark', 'Dart')\", \"('skill-icons:deno-dark', 'Deno')\", \"('skill-icons:devto-dark', 'Devto')\", \"('skill-icons:discord', 'Discord')\", \"('skill-icons:discordbots', 'Discordbots')\", \"('skill-icons:django', 'Django')\", \"('skill-icons:docker', 'Docker')\", \"('skill-icons:dotnet', 'Dotnet')\", \"('skill-icons:dynamodb-dark', 'Dynamodb')\", \"('skill-icons:eclipse-dark', 'Eclipse')\", \"('skill-icons:electron', 'Electron')\", \"('skill-icons:elixir-dark', 'Elixir')\", \"('skill-icons:emacs', 'Emacs')\", \"('skill-icons:ember', 'Ember')\", \"('skill-icons:emotion-dark', 'Emotion')\", \"('skill-icons:expressjs-dark', 'Expressjs')\", \"('skill-icons:fastapi', 'Fastapi')\", \"('skill-icons:fediverse-dark', 'Fediverse')\", \"('skill-icons:figma-dark', 'Figma')\", \"('skill-icons:flask-dark', 'Flask')\", \"('skill-icons:flutter-dark', 'Flutter')\", \"('skill-icons:forth', 'Forth')\", \"('skill-icons:fortran', 'Fortran')\", \"('skill-icons:gamemakerstudio', 'Gamemakerstudio')\", \"('skill-icons:gatsby', 'Gatsby')\", \"('skill-icons:gcp-dark', 'Gcp')\", \"('skill-icons:gherkin-dark', 'Gherkin')\", \"('skill-icons:git', 'Git')\", \"('skill-icons:github-dark', 'Github')\", \"('skill-icons:githubactions-dark', 'Githubactions')\", \"('skill-icons:gitlab-dark', 'Gitlab')\", \"('skill-icons:godot-dark', 'Godot')\", \"('skill-icons:golang', 'Golang')\", \"('skill-icons:gradle-dark', 'Gradle')\", \"('skill-icons:grafana-dark', 'Grafana')\", \"('skill-icons:graphql-dark', 'Graphql')\", \"('skill-icons:gtk-dark', 'Gtk')\", \"('skill-icons:gulp', 'Gulp')\", \"('skill-icons:haskell-dark', 'Haskell')\", \"('skill-icons:haxe-dark', 'Haxe')\", \"('skill-icons:haxeflixel-dark', 'Haxeflixel')\", \"('skill-icons:heroku', 'Heroku')\", \"('skill-icons:hibernate-dark', 'Hibernate')\", \"('skill-icons:html', 'Html')\", \"('skill-icons:idea-dark', 'Idea')\", \"('skill-icons:illustrator', 'Illustrator')\", \"('skill-icons:instagram', 'Instagram')\", \"('skill-icons:ipfs-dark', 'Ipfs')\", \"('skill-icons:java-dark', 'Java')\", \"('skill-icons:javascript', 'Javascript')\", \"('skill-icons:jenkins-dark', 'Jenkins')\", \"('skill-icons:jest', 'Jest')\", \"('skill-icons:jquery', 'Jquery')\", \"('skill-icons:julia-dark', 'Julia')\", \"('skill-icons:kafka', 'Kafka')\", \"('skill-icons:kotlin-dark', 'Kotlin')\", \"('skill-icons:ktor-dark', 'Ktor')\", \"('skill-icons:kubernetes', 'Kubernetes')\", \"('skill-icons:laravel-dark', 'Laravel')\", \"('skill-icons:latex-dark', 'Latex')\", \"('skill-icons:linkedin', 'Linkedin')\", \"('skill-icons:linux-dark', 'Linux')\", \"('skill-icons:lit-dark', 'Lit')\", \"('skill-icons:lua-dark', 'Lua')\", \"('skill-icons:markdown-dark', 'Markdown')\", \"('skill-icons:mastodon-dark', 'Mastodon')\", \"('skill-icons:materialui-dark', 'Materialui')\", \"('skill-icons:matlab-dark', 'Matlab')\", \"('skill-icons:maven-dark', 'Maven')\", \"('skill-icons:misskey-dark', 'Misskey')\", \"('skill-icons:mongodb', 'Mongodb')\", \"('skill-icons:mysql-dark', 'Mysql')\", \"('skill-icons:neovim-dark', 'Neovim')\", \"('skill-icons:nestjs-dark', 'Nestjs')\", \"('skill-icons:netlify-dark', 'Netlify')\", \"('skill-icons:nextjs-dark', 'Nextjs')\", \"('skill-icons:nginx', 'Nginx')\", \"('skill-icons:nim-dark', 'Nim')\", \"('skill-icons:nodejs-dark', 'Nodejs')\", \"('skill-icons:nuxtjs-dark', 'Nuxtjs')\", \"('skill-icons:ocaml', 'Ocaml')\", \"('skill-icons:octave-dark', 'Octave')\", \"('skill-icons:openshift', 'Openshift')\", \"('skill-icons:openstack-dark', 'Openstack')\", \"('skill-icons:perl', 'Perl')\", \"('skill-icons:photoshop', 'Photoshop')\", \"('skill-icons:php-dark', 'Php')\", \"('skill-icons:plan9-dark', 'Plan9')\", \"('skill-icons:planetscale-dark', 'Planetscale')\", \"('skill-icons:postgresql-dark', 'Postgresql')\", \"('skill-icons:postman', 'Postman')\", \"('skill-icons:powershell-dark', 'Powershell')\", \"('skill-icons:premiere', 'Premiere')\", \"('skill-icons:prisma', 'Prisma')\", \"('skill-icons:processing-dark', 'Processing')\", \"('skill-icons:prometheus', 'Prometheus')\", \"('skill-icons:pug-dark', 'Pug')\", \"('skill-icons:python-dark', 'Python')\", \"('skill-icons:pytorch-dark', 'Pytorch')\", \"('skill-icons:qt-dark', 'Qt')\", \"('skill-icons:r-dark', 'R')\", \"('skill-icons:rabbitmq-dark', 'Rabbitmq')\", \"('skill-icons:rails', 'Rails')\", \"('skill-icons:raspberrypi-dark', 'Raspberrypi')\", \"('skill-icons:react-dark', 'React')\", \"('skill-icons:reactivex-dark', 'Reactivex')\", \"('skill-icons:redis-dark', 'Redis')\", \"('skill-icons:redux', 'Redux')\", \"('skill-icons:regex-dark', 'Regex')\", \"('skill-icons:remix-dark', 'Remix')\", \"('skill-icons:replit-dark', 'Replit')\", \"('skill-icons:rocket', 'Rocket')\", \"('skill-icons:rollupjs-dark', 'Rollupjs')\", \"('skill-icons:ros-dark', 'Ros')\", \"('skill-icons:ruby', 'Ruby')\", \"('skill-icons:rust', 'Rust')\", \"('skill-icons:sass', 'Sass')\", \"('skill-icons:scala-dark', 'Scala')\", \"('skill-icons:selenium', 'Selenium')\", \"('skill-icons:sentry', 'Sentry')\", \"('skill-icons:sequelize-dark', 'Sequelize')\", \"('skill-icons:sketchup-dark', 'Sketchup')\", \"('skill-icons:solidity', 'Solidity')\", \"('skill-icons:solidjs-dark', 'Solidjs')\", \"('skill-icons:spring-dark', 'Spring')\", \"('skill-icons:sqlite', 'Sqlite')\", \"('skill-icons:stackoverflow-dark', 'Stackoverflow')\", \"('skill-icons:styledcomponents', 'Styledcomponents')\", \"('skill-icons:supabase-dark', 'Supabase')\", \"('skill-icons:svelte', 'Svelte')\", \"('skill-icons:svg-dark', 'Svg')\", \"('skill-icons:swift', 'Swift')\", \"('skill-icons:symfony-dark', 'Symfony')\", \"('skill-icons:tailwindcss-dark', 'Tailwindcss')\", \"('skill-icons:tauri-dark', 'Tauri')\", \"('skill-icons:tensorflow-dark', 'Tensorflow')\", \"('skill-icons:threejs-dark', 'Threejs')\", \"('skill-icons:twitter', 'Twitter')\", \"('skill-icons:typescript', 'Typescript')\", \"('skill-icons:unity-dark', 'Unity')\", \"('skill-icons:unrealengine', 'Unrealengine')\", \"('skill-icons:v-dark', 'V')\", \"('skill-icons:vala', 'Vala')\", \"('skill-icons:vercel-dark', 'Vercel')\", \"('skill-icons:vim-dark', 'Vim')\", \"('skill-icons:visualstudio-dark', 'Visualstudio')\", \"('skill-icons:vite-dark', 'Vite')\", \"('skill-icons:vscode-dark', 'Vscode')\", \"('skill-icons:vuejs-dark', 'Vuejs')\", \"('skill-icons:webassembly', 'Webassembly')\", \"('skill-icons:webflow', 'Webflow')\", \"('skill-icons:webpack-dark', 'Webpack')\", \"('skill-icons:windicss-dark', 'Windicss')\", \"('skill-icons:wordpress', 'Wordpress')\", \"('skill-icons:workers-dark', 'Workers')\", \"('skill-icons:xd', 'Xd')\", \"('skill-icons:zig-dark', 'Zig')\"",
                        max_count=10,
                        related_name="job_skills",
                        space_delimiter=False,
                        to="jobs.skillstagmodel",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
    ]
