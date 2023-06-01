from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests

app = Flask(__name__)
CORS(app)

@app.route('/api/github/<username>', methods=['GET'])
def github_stats(username):
    forked = request.args.get('forked', 'true').lower() in ['true', '1']

    # Make request to Github API
    repo_api_url = f'https://api.github.com/users/{username}/repos'
    repos = requests.get(repo_api_url).json()

    # Filter out forked repos if necessary
    if not forked:
        repos = [repo for repo in repos if not repo['fork']]

    # Calculate aggregated statistics
    stats = {
        'total_repo_count': len(repos),
        'total_stargazers': sum(repo['stargazers_count'] for repo in repos),
        'total_forks': sum(repo['forks_count'] for repo in repos),
        'avg_repo_size': sum(repo['size'] for repo in repos) / len(repos) if repos else 0, # in KB
    }

    # Calculate language usage
    languages = {}
    for repo in repos:
        if repo['language']:
            if repo['language'] in languages:
                languages[repo['language']] += 1
            else:
                languages[repo['language']] = 1
    stats['languages'] = sorted(languages.items(), key=lambda x: x[1], reverse=True)

    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True)
