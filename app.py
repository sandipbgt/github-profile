#! /usr/bin/python3

import requests
from lxml import html
from terminaltables import AsciiTable
import argparse
import sys

GITHUB_BASE = 'https://github.com'
GITHUB_API = 'https://api.github.com'
GITHUB_USER_REPOS_URL = 'https://github.com/{}?tab=repositories'

def get_user_profile(username):
    try:
        response = requests.get(GITHUB_API + '/users/' + username)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("User not found.")
        sys.exit(1)
    user_json = response.json()

    user = {}
    user['username'] = username
    user['fullname'] = user_json.get('name', 'n/a')
    user['email'] = user_json.get('email', 'n/a')
    user['location'] = user_json.get('location', 'n/a')
    user['bio'] = user_json.get('bio', 'n/a')
    user['blog'] = user_json.get('blog', 'n/a')
    user['followers'] = user_json.get('followers', 'n/a')
    user['following'] = user_json.get('following', 'n/a')
    user['created_at'] = user_json.get('created_at', 'n/a')
    user['total_public_repos'] = user_json.get('total_public_repos', 'n/a')
    user['total_public_gists'] = user_json.get('total_public_gists', 'n/a')

    return user

def get_user_repos(username):
    repos = []
    try:
        response = requests.get(GITHUB_USER_REPOS_URL.format(username))
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("User not found.")
        sys.exit(1)

    tree = html.fromstring(response.content)
    for count, item in enumerate(tree.xpath('//div[@class="repo-list-item public source"]'), start=1):

        repo = {}
        repo['sn'] = count
        try:
            repo['name'] = item.xpath('h3/a/text()')[0].strip()
        except IndexError:
            repo['name'] = ''

        try:
            repo['url'] = GITHUB_BASE + item.xpath('h3/a/@href')[0].strip()
        except IndexError:
            repo['url'] = ''

        try:
            repo['description'] = item.xpath('p[@class="repo-list-description"]/text()')[0].strip()
        except IndexError:
            repo['description'] = 'n/a'

        try:
            repo['updated_at'] = item.xpath('p[@class="repo-list-meta"]/relative-time/text()')[0].strip()
        except IndexError:
            repo['updated_at'] = ''

        repos.append(repo)
    return repos

def print_user_profile(username):
    profile = get_user_profile(username)
    print("{:>10} {}".format('Username:', profile['username']))
    print("{:>10} {}".format('Full name:', profile['fullname']))
    print("{:>10} {}".format('E-mail:', profile['email']))
    print("{:>10} {}".format('Location:', profile['location']))
    print("{:>10} {}".format('Blog:', profile['blog']))
    print("{:>10} {}".format('Followers:', profile['followers']))
    print("{:>10} {}".format('Following:', profile['following']))

def print_user_repos(username):
    repos = get_user_repos(username)
    if not repos:
        print("No repositories found.")
        sys.exit(0)

    data = [['S.N', 'NAME', 'DESCRIPTION', 'UPDATED']]
    data.extend([[v['sn'], v['name'], v['description'][:80] + '...', v['updated_at']] for v in repos])
    print(AsciiTable(data).table)

def main():
    parser = argparse.ArgumentParser(description="View public repositories of any GitHub user.")
    parser.add_argument('username', help="GitHub username", action='store')
    args = parser.parse_args()

    print("{:=^150}".format('USER PROFILE'))
    print_user_profile(args.username)
    print("\n{:=^150}".format('USER REPOSITORIES'))
    print_user_repos(args.username)

if __name__ == '__main__':
    main()