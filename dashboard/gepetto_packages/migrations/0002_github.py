# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-09 15:55
from __future__ import unicode_literals

from os.path import expanduser

from django.db import migrations

import requests

GITHUB_API = 'https://api.github.com'
with open(expanduser('~/.githubtoken')) as f:
    TOKEN = f.read().strip()
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.drax-preview+json',
}

PROJECTS = (
    'Humanoid Path Planner',
    'Stack of Tasks'
)

def github_licenses(apps, schema_editor):
    License = apps.get_model('gepetto_packages', 'License')
    for data in requests.get(f'{GITHUB_API}/licenses', headers=HEADERS).json():
        License.objects.create(github_key=data['key'], **{key: data[key] for key in ['name', 'spdx_id', 'url']})


def github_projects(apps, schema_editor):
    Project, License, Package, Repo = (apps.get_model('gepetto_packages', model)
                                       for model in ['Project', 'License', 'Package', 'Repo'])
    for project_name in PROJECTS:
        project = Project(name=project_name)
        project.save()
        for data in requests.get(f'{GITHUB_API}/orgs/{project.slug}/repos', headers=HEADERS).json():
            package = Package(name=data['name'], project=project, homepage=data['homepage'])
            package.save()
            repo = Repo(package=package, url=data['html_url'], homepage=data['homepage'], repo_id=data['id'],
                        default_branch=data['default_branch'], open_issues=data['open_issues'])
            repo_api_url = f'{GITHUB_API}/repos/{project.slug}/{package.slug}'
            repo_data = requests.get(repo_api_url, headers=HEADERS).json()
            if 'license' in repo_data and repo_data['license']:
                license_data = repo_data['license']
                license, _ = License.objects.get_or_create(github_key=license_data['key'], name=license_data['name'])
                repo.license = license
                package.license = license
                package.save()
            repo.open_pr = len(requests.get(f'{repo_api_url}/pulls', headers=HEADERS).json())
            repo.save()

class Migration(migrations.Migration):

    dependencies = [
        ('gepetto_packages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(github_licenses),
        migrations.RunPython(github_projects),
    ]