import subprocess
from datetime import datetime

def on_config(config, **kwargs):
    """Add git revision information to the config for use in templates."""
    try:
        # Get the current git commit hash
        full_commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            universal_newlines=True
        ).strip()

        short_commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            universal_newlines=True
        ).strip()

        # Get the commit date
        commit_date = subprocess.check_output(
            ['git', 'show', '-s', '--format=%ci', 'HEAD'],
            universal_newlines=True
        ).strip()

        # Parse and format the date
        commit_datetime = datetime.fromisoformat(commit_date.replace(' ', 'T', 1))
        formatted_date = commit_datetime.strftime('%Y-%m-%d %H:%M UTC')

        # Add git info to config
        if 'extra' not in config:
            config['extra'] = {}

        config['extra']['git'] = {
            'commit': full_commit,
            'short_commit': short_commit,
            'date': formatted_date
        }

    except subprocess.CalledProcessError:
        # Fallback if git commands fail
        config['extra']['git'] = {
            'commit': 'unknown',
            'short_commit': 'unknown',
            'date': 'unknown'
        }

    return config