"""
SMPOOS – Smart Maritime Port Operations Optimisation System
CPS7002 Software Design and Development – Assessment 1

Entry point for the Dash web application.
Run:  python app.py
Then open http://127.0.0.1:8050 in a browser.
"""

import os
import sys

import dash
import dash_bootstrap_components as dbc

from data.repository import DataRepository
from analytics.port_analytics import PortAnalytics
from dashboard.layout import build_layout
from dashboard.callbacks import register_callbacks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app() -> dash.Dash:
    repo = DataRepository(data_dir=DATA_DIR)
    repo.load_all()

    summary = repo.summary()
    print(f"[SMPOOS] Data loaded: {summary}")

    analytics = PortAnalytics(
        locations=repo.locations,
        routes=repo.routes,
        users=repo.users,
        notifications=repo.notifications,
    )

    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.FLATLY,
            dbc.icons.BOOTSTRAP,
        ],
        title='SMPOOS – HarbourView Port',
        suppress_callback_exceptions=True,
        meta_tags=[
            {'name': 'viewport',
             'content': 'width=device-width, initial-scale=1'},
        ],
    )

    app.layout = build_layout(repo, analytics)
    register_callbacks(app, repo, analytics)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=8050)
