import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table

from models.user import UserRole


SEVERITY_BADGE = {
    'Low': 'success',
    'Medium': 'warning',
    'High': 'danger',
    'Critical': 'dark',
}

STATUS_BADGE = {
    'Active': 'success',
    'Inactive': 'secondary',
    'Under Maintenance': 'warning',
    'Open': 'success',
    'Closed': 'danger',
    'Restricted': 'warning',
}


def _login_page() -> html.Div:
    role_options = [{'label': r.value, 'value': r.value} for r in UserRole]
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className='bi bi-anchor display-3 text-primary mb-2'),
                        html.H2('SMPOOS', className='fw-bold'),
                        html.P('HarbourView International Port Management System',
                               className='text-muted'),
                    ], className='text-center mb-4'),
                    dbc.Card([
                        dbc.CardBody([
                            html.H5('Sign In', className='fw-bold mb-4 text-center'),

                            dbc.Label('User ID', html_for='login-user-id'),
                            dbc.InputGroup([
                                dbc.InputGroupText(html.I(className='bi bi-person')),
                                dbc.Input(id='login-user-id',
                                          placeholder='e.g. U0001',
                                          type='text'),
                            ], className='mb-2'),
                            dbc.Button(
                                [html.I(className='bi bi-box-arrow-in-right me-2'),
                                 'Login with User ID'],
                                id='btn-login-id',
                                color='primary',
                                className='w-100 mb-4',
                            ),

                            dbc.Row([
                                dbc.Col(html.Hr()),
                                dbc.Col(html.Small('or', className='text-muted'),
                                        width='auto', className='d-flex align-items-center px-0'),
                                dbc.Col(html.Hr()),
                            ], className='mb-3 align-items-center'),

                            dbc.Label('Quick login by role (RBAC testing)',
                                      className='text-muted small fw-semibold'),
                            dcc.Dropdown(
                                id='login-role-select',
                                options=role_options,
                                placeholder='Select a role…',
                                clearable=False,
                                className='mb-2',
                            ),
                            dbc.Button(
                                'Login as Role',
                                id='btn-login-role',
                                color='outline-secondary',
                                className='w-100',
                            ),

                            html.Div(id='login-feedback', className='mt-3'),
                        ]),
                    ], className='shadow-sm border-0'),
                ], md=5, lg=4),
            ], justify='center', className='pt-5'),
        ]),
    ], id='login-page',
       style={'minHeight': '100vh', 'paddingTop': '40px', 'backgroundColor': '#f0f4f8'})


def kpi_card(title: str, value, subtitle: str = '', colour: str = 'primary',
             icon: str = '') -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.P(title, className='text-muted mb-1 small fw-bold text-uppercase'),
            html.H3(str(value), className=f'text-{colour} mb-0 fw-bold'),
            html.Small(subtitle, className='text-muted') if subtitle else html.Span(),
        ]),
        className='shadow-sm border-0 h-100',
    )


def build_layout(repo, analytics) -> html.Div:
    kpis = analytics.get_kpis()

    navbar = dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className='bi bi-anchor me-2'),
                'SMPOOS – HarbourView International Port',
            ], className='fw-bold fs-5'),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(
                    [html.I(className='bi bi-clock me-1'),
                     html.Span(id='live-clock')],
                    className='text-light',
                )),
                html.Span(id='navbar-user-info',
                          className='text-light ms-3 d-flex align-items-center'),
                dbc.Button(
                    [html.I(className='bi bi-box-arrow-right me-1'), 'Logout'],
                    id='btn-logout',
                    color='outline-light',
                    size='sm',
                    className='ms-3',
                ),
            ], className='ms-auto align-items-center'),
        ], fluid=True),
        color='dark',
        dark=True,
        className='mb-3 shadow',
    )

    tabs = dbc.Tabs([
        dbc.Tab(_overview_tab(kpis, analytics),
                label='Overview', tab_id='tab-overview',
                tab_class_name='fw-semibold'),
        dbc.Tab(_locations_tab(repo),
                label='Locations', tab_id='tab-locations',
                tab_class_name='fw-semibold'),
        dbc.Tab(_routes_tab(repo),
                label='Routes', tab_id='tab-routes',
                tab_class_name='fw-semibold'),
        dbc.Tab(_notifications_tab(repo),
                label='Notifications', tab_id='tab-notifications',
                tab_class_name='fw-semibold'),
        dbc.Tab(_users_tab(repo),
                label='Personnel', tab_id='tab-users',
                tab_class_name='fw-semibold'),
        dbc.Tab(_analytics_tab(),
                label='Analytics', tab_id='tab-analytics',
                id='nav-tab-analytics',
                tab_class_name='fw-semibold'),
        dbc.Tab(_audit_tab(),
                label='Audit Log', tab_id='tab-audit',
                id='nav-tab-audit',
                tab_class_name='fw-semibold'),
    ], id='main-tabs', active_tab='tab-overview', className='mb-4')

    return html.Div([
        dcc.Store(id='session-store', storage_type='memory'),
        dcc.Interval(id='clock-interval', interval=1000, n_intervals=0),
        dcc.Interval(id='refresh-interval', interval=30000, n_intervals=0),
        dcc.Store(id='selected-location-store'),
        dcc.Store(id='selected-route-store'),
        _login_page(),
        html.Div(id='main-content', style={'display': 'none'}, children=[
            navbar,
            dbc.Container([tabs], fluid=True),
            _location_modal(),
            _route_status_modal(),
            _notification_modal(),
        ]),
    ])


# ── Tabs ───────────────────────────────────────────────────────────────────────

def _overview_tab(kpis: dict, analytics) -> html.Div:
    suggestions = analytics.suggest_berth_optimisation()
    bottlenecks = analytics.identify_bottlenecks()

    alert_cards = []
    for s in suggestions:
        colour = {'Critical': 'danger', 'High': 'warning',
                  'Medium': 'info'}.get(s['priority'], 'secondary')
        alert_cards.append(
            dbc.Alert([
                html.Strong(f"[{s['priority']}] "), s['message']
            ], color=colour, className='py-2 mb-2')
        )

    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card('Total Locations', kpis['total_locations'],
                             colour='primary'), md=3, className='mb-3'),
            dbc.Col(kpi_card('Active Locations',
                             f"{kpis['active_locations']} ({kpis['location_availability_pct']}%)",
                             colour='success'), md=3, className='mb-3'),
            dbc.Col(kpi_card('Open Routes', kpis['open_routes'],
                             f"of {kpis['total_routes']} total",
                             colour='info'), md=3, className='mb-3'),
            dbc.Col(kpi_card('Critical Alerts', kpis['critical_alerts'],
                             f"{kpis['high_priority_alerts']} high priority",
                             colour='danger'), md=3, className='mb-3'),
        ]),
        dbc.Row([
            dbc.Col(kpi_card('Active Personnel', kpis['active_users'],
                             f"of {kpis['total_users']} total",
                             colour='warning'), md=3, className='mb-3'),
            dbc.Col(kpi_card('Total Notifications', kpis['total_notifications'],
                             colour='secondary'), md=3, className='mb-3'),
            dbc.Col(kpi_card('Active Capacity',
                             f"{kpis['active_capacity_tonnes']:,} t",
                             f"Total: {kpis['total_capacity_tonnes']:,} t",
                             colour='primary'), md=3, className='mb-3'),
            dbc.Col(kpi_card('Berths Under Maintenance',
                             kpis['under_maintenance'],
                             colour='warning'), md=3, className='mb-3'),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5('Port Status Overview', className='mb-3 fw-bold'),
                dcc.Graph(id='overview-location-status-chart',
                          config={'displayModeBar': False}),
            ], md=4, className='mb-4'),
            dbc.Col([
                html.H5('Route Network Status', className='mb-3 fw-bold'),
                dcc.Graph(id='overview-route-status-chart',
                          config={'displayModeBar': False}),
            ], md=4, className='mb-4'),
            dbc.Col([
                html.H5('Alert Severity Distribution', className='mb-3 fw-bold'),
                dcc.Graph(id='overview-severity-chart',
                          config={'displayModeBar': False}),
            ], md=4, className='mb-4'),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5('Recent Critical Alerts',
                        className='mb-3 fw-bold text-danger'),
                html.Div(id='critical-alerts-list'),
            ], md=6),
            dbc.Col([
                html.H5('Optimisation Recommendations',
                        className='mb-3 fw-bold'),
                html.Div(alert_cards if alert_cards
                         else [dbc.Alert('No recommendations at this time.',
                                         color='success', className='py-2')]),
            ], md=6),
        ]),
    ])


def _locations_tab(repo) -> html.Div:
    loc_types = ['All'] + sorted({l.type.value for l in repo.locations})
    loc_statuses = ['All'] + sorted({l.status.value for l in repo.locations})

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label('Filter by Type'),
                dcc.Dropdown(
                    id='location-type-filter',
                    options=[{'label': t, 'value': t} for t in loc_types],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Filter by Status'),
                dcc.Dropdown(
                    id='location-status-filter',
                    options=[{'label': s, 'value': s} for s in loc_statuses],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Search Name'),
                dbc.Input(id='location-search', placeholder='Enter location name…',
                          type='text'),
            ], md=4),
            dbc.Col([
                dbc.Label(' '),
                dbc.Button('+ Add Location', id='btn-add-location',
                           color='primary', className='w-100'),
            ], md=2),
        ], className='mb-3'),

        html.Div(id='location-table-container'),

        dbc.Row([
            dbc.Col([
                html.Small(id='location-record-count',
                           className='text-muted'),
            ]),
        ], className='mt-2'),
    ])


def _routes_tab(repo) -> html.Div:
    route_types = ['All'] + sorted({r.route_type.value for r in repo.routes})
    route_statuses = ['All'] + sorted({r.status.value for r in repo.routes})

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label('Filter by Type'),
                dcc.Dropdown(
                    id='route-type-filter',
                    options=[{'label': t, 'value': t} for t in route_types],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Filter by Status'),
                dcc.Dropdown(
                    id='route-status-filter',
                    options=[{'label': s, 'value': s} for s in route_statuses],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Max Distance (km)'),
                dcc.Slider(
                    id='route-distance-slider',
                    min=0, max=30, step=1, value=30,
                    marks={0: '0', 10: '10', 20: '20', 30: '30+'},
                ),
            ], md=4),
            dbc.Col([
                dbc.Label(' '),
                dbc.Button('+ Add Route', id='btn-add-route',
                           color='primary', className='w-100'),
            ], md=2),
        ], className='mb-3'),

        html.Div(id='route-table-container'),
        html.Small(id='route-record-count', className='text-muted mt-2 d-block'),
    ])


def _notifications_tab(repo) -> html.Div:
    alert_types = ['All'] + sorted({n.alert_type.value for n in repo.notifications})
    severities = ['All', 'Critical', 'High', 'Medium', 'Low']

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label('Filter by Type'),
                dcc.Dropdown(
                    id='notif-type-filter',
                    options=[{'label': t, 'value': t} for t in alert_types],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Filter by Severity'),
                dcc.Dropdown(
                    id='notif-severity-filter',
                    options=[{'label': s, 'value': s} for s in severities],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Filter by Location ID'),
                dbc.Input(id='notif-location-filter',
                          placeholder='e.g. L0001', type='text'),
            ], md=3),
            dbc.Col([
                dbc.Label(' '),
                dbc.Button('+ New Alert', id='btn-add-notification',
                           color='danger', className='w-100'),
            ], md=3),
        ], className='mb-3'),

        html.Div(id='notification-table-container'),
        html.Small(id='notif-record-count', className='text-muted mt-2 d-block'),
    ])


def _users_tab(repo) -> html.Div:
    roles = ['All'] + sorted({u.role.value for u in repo.users})

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label('Filter by Role'),
                dcc.Dropdown(
                    id='user-role-filter',
                    options=[{'label': r, 'value': r} for r in roles],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Filter by Status'),
                dcc.Dropdown(
                    id='user-active-filter',
                    options=[
                        {'label': 'All', 'value': 'All'},
                        {'label': 'Active', 'value': 'Yes'},
                        {'label': 'Inactive', 'value': 'No'},
                    ],
                    value='All', clearable=False,
                ),
            ], md=3),
            dbc.Col([
                dbc.Label('Search Name/Email'),
                dbc.Input(id='user-search', placeholder='Search…', type='text'),
            ], md=4),
        ], className='mb-3'),

        dbc.Row([
            dbc.Col([
                html.Div(id='user-table-container'),
                html.Small(id='user-record-count',
                           className='text-muted mt-2 d-block'),
            ], md=8),
            dbc.Col([
                html.H6('Role Distribution', className='fw-bold'),
                dcc.Graph(id='user-role-chart',
                          config={'displayModeBar': False},
                          style={'height': '350px'}),
            ], md=4),
        ]),
    ])


def _analytics_tab() -> html.Div:
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5('Location Type Distribution', className='fw-bold mb-2'),
                dcc.Graph(id='analytics-location-type',
                          config={'displayModeBar': False}),
            ], md=6, className='mb-4'),
            dbc.Col([
                html.H5('Capacity by Location Type (tonnes)',
                        className='fw-bold mb-2'),
                dcc.Graph(id='analytics-capacity-type',
                          config={'displayModeBar': False}),
            ], md=6, className='mb-4'),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5('Notification Trends Over Time', className='fw-bold mb-2'),
                dcc.Graph(id='analytics-notif-trend',
                          config={'displayModeBar': False}),
            ], md=8, className='mb-4'),
            dbc.Col([
                html.H5('Alert Type Breakdown', className='fw-bold mb-2'),
                dcc.Graph(id='analytics-alert-types',
                          config={'displayModeBar': False}),
            ], md=4, className='mb-4'),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5('Route Type Distribution', className='fw-bold mb-2'),
                dcc.Graph(id='analytics-route-types',
                          config={'displayModeBar': False}),
            ], md=6, className='mb-4'),
            dbc.Col([
                html.H5('Average Route Distance by Type (km)',
                        className='fw-bold mb-2'),
                dcc.Graph(id='analytics-route-distance',
                          config={'displayModeBar': False}),
            ], md=6, className='mb-4'),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5('Top 10 Most Alerted Locations', className='fw-bold mb-2'),
                dcc.Graph(id='analytics-top-locations',
                          config={'displayModeBar': False}),
            ], md=12, className='mb-4'),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5('Operational Bottlenecks', className='fw-bold mb-2'),
                html.Div(id='analytics-bottlenecks'),
            ], md=12),
        ]),
    ])


def _audit_tab() -> html.Div:
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5('System Audit Trail', className='fw-bold mb-3'),
                html.P('All administrative actions, data modifications, and system '
                       'access events are recorded here for compliance and security review.',
                       className='text-muted small'),
            ]),
        ]),
        html.Div(id='audit-table-container'),
    ])


# ── Modals ─────────────────────────────────────────────────────────────────────

def _location_modal() -> dbc.Modal:
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Manage Location'), close_button=True),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Location ID'),
                    dbc.Input(id='modal-loc-id', placeholder='e.g. L0501', type='text'),
                ], md=4),
                dbc.Col([
                    dbc.Label('Name'),
                    dbc.Input(id='modal-loc-name', placeholder='Berth X Area Y',
                              type='text'),
                ], md=8),
            ], className='mb-3'),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Type'),
                    dcc.Dropdown(
                        id='modal-loc-type',
                        options=[
                            {'label': 'Berth', 'value': 'Berth'},
                            {'label': 'Storage Yard', 'value': 'Storage Yard'},
                            {'label': 'Fuel Dock', 'value': 'Fuel Dock'},
                            {'label': 'Customs Zone', 'value': 'Customs Zone'},
                            {'label': 'Maintenance Area', 'value': 'Maintenance Area'},
                        ],
                        value='Berth', clearable=False,
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label('Status'),
                    dcc.Dropdown(
                        id='modal-loc-status',
                        options=[
                            {'label': 'Active', 'value': 'Active'},
                            {'label': 'Inactive', 'value': 'Inactive'},
                            {'label': 'Under Maintenance',
                             'value': 'Under Maintenance'},
                        ],
                        value='Active', clearable=False,
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label('Capacity (tonnes)'),
                    dbc.Input(id='modal-loc-capacity', type='number',
                              min=0, value=5000),
                ], md=4),
            ], className='mb-3'),
            html.Div(id='modal-loc-feedback'),
        ]),
        dbc.ModalFooter([
            dbc.Button('Save', id='modal-loc-save', color='primary'),
            dbc.Button('Cancel', id='modal-loc-cancel', color='secondary',
                       className='ms-2'),
        ]),
    ], id='location-modal', is_open=False, size='lg')


def _route_status_modal() -> dbc.Modal:
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Update Route Status'), close_button=True),
        dbc.ModalBody([
            html.P(id='modal-route-info', className='text-muted'),
            dbc.Label('New Status'),
            dcc.Dropdown(
                id='modal-route-status',
                options=[
                    {'label': 'Open', 'value': 'Open'},
                    {'label': 'Closed', 'value': 'Closed'},
                    {'label': 'Restricted', 'value': 'Restricted'},
                ],
                value='Open', clearable=False,
            ),
            html.Div(id='modal-route-feedback', className='mt-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button('Update', id='modal-route-save', color='primary'),
            dbc.Button('Cancel', id='modal-route-cancel', color='secondary',
                       className='ms-2'),
        ]),
    ], id='route-modal', is_open=False)


def _notification_modal() -> dbc.Modal:
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Create New Alert'), close_button=True),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Alert Type'),
                    dcc.Dropdown(
                        id='modal-notif-type',
                        options=[
                            {'label': t, 'value': t}
                            for t in [
                                'Weather Warning', 'Equipment Failure',
                                'Berth Closure', 'Security Notice',
                                'Congestion Alert', 'Hazardous Cargo Warning',
                            ]
                        ],
                        value='Weather Warning', clearable=False,
                    ),
                ], md=6),
                dbc.Col([
                    dbc.Label('Severity'),
                    dcc.Dropdown(
                        id='modal-notif-severity',
                        options=[
                            {'label': s, 'value': s}
                            for s in ['Low', 'Medium', 'High', 'Critical']
                        ],
                        value='Medium', clearable=False,
                    ),
                ], md=6),
            ], className='mb-3'),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Location ID'),
                    dbc.Input(id='modal-notif-location',
                              placeholder='e.g. L0001', type='text'),
                ], md=6),
            ], className='mb-3'),
            dbc.Label('Message'),
            dbc.Textarea(id='modal-notif-message',
                         placeholder='Enter alert message…', rows=3),
            html.Div(id='modal-notif-feedback', className='mt-2'),
        ]),
        dbc.ModalFooter([
            dbc.Button('Submit Alert', id='modal-notif-save', color='danger'),
            dbc.Button('Cancel', id='modal-notif-cancel', color='secondary',
                       className='ms-2'),
        ]),
    ], id='notification-modal', is_open=False)
