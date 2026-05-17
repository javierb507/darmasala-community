"""Cliente mínimo de la GitHub Issues API.

Solo lo necesario para que la app cree issues automáticas cuando
un usuario reporta un bug desde dentro del producto.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import requests


GITHUB_API = 'https://api.github.com'


class GitHubIssuesError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitHubConfig:
    enabled: bool
    repo: str              # 'owner/name'
    token: str             # secreto, solo de env
    default_labels: list[str]

    @property
    def configured(self) -> bool:
        return bool(self.enabled and self.repo and '/' in self.repo and self.token)


def load_config(config_dict: dict) -> GitHubConfig:
    labels_raw = (config_dict.get('bug_report_labels', '') or '').strip()
    labels = [l.strip() for l in labels_raw.split(',') if l.strip()]
    return GitHubConfig(
        enabled=(config_dict.get('bug_report_enabled', '') or '').lower() in ('1', 'true', 'on', 'yes'),
        repo=config_dict.get('bug_report_repo', '') or '',
        token=os.environ.get('GITHUB_ISSUE_TOKEN', ''),
        default_labels=labels or ['bug', 'reportado-desde-app'],
    )


def create_issue(
    cfg: GitHubConfig,
    title: str,
    body: str,
    extra_labels: Optional[list[str]] = None,
) -> dict:
    if not cfg.configured:
        raise GitHubIssuesError('GitHub bug reporter no está configurado (repo o token faltan).')
    if not title.strip():
        raise GitHubIssuesError('El título no puede estar vacío.')

    url = f'{GITHUB_API}/repos/{cfg.repo}/issues'
    headers = {
        'Authorization': f'Bearer {cfg.token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'DarmaSala-BugReporter',
    }
    labels = list(dict.fromkeys((cfg.default_labels or []) + (extra_labels or [])))
    payload = {
        'title': title.strip()[:200],
        'body': body,
        'labels': labels,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
    except requests.RequestException as exc:
        raise GitHubIssuesError(f'Error de red contactando con GitHub: {exc}') from exc

    if resp.status_code == 401:
        raise GitHubIssuesError('GitHub respondió 401: token inválido o sin permiso "issues:write".')
    if resp.status_code == 404:
        raise GitHubIssuesError(f'GitHub respondió 404: repo {cfg.repo!r} no encontrado o token sin acceso.')
    if resp.status_code >= 400:
        try:
            body_err = resp.json()
        except ValueError:
            body_err = resp.text
        raise GitHubIssuesError(f'GitHub respondió {resp.status_code}: {body_err}')

    return resp.json()
