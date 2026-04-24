from datetime import datetime
from typing import List

import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context, html, dash_table, no_update
from dash.exceptions import PreventUpdate

from models.location import Location, LocationType, LocationStatus
from models.route import Route, RouteType, RouteStatus
from models.notification import Notification, AlertType, Severity
from models.user import UserRole, ROLE_PERMISSIONS

CHART_TEMPLATE = 'plotly_white'
COLOUR_SEQUENCE = px.colors.qualitative.Set2

STATUS_COLOURS = {
    'Active': '#2ecc71',
    'Inactive': '#95a5a6',
    'Under Maintenance': '#f39c12',
    'Open': '#2ecc71',
    'Closed': '#e74c3c',
    'Restricted': '#f39c12',
}
SEVERITY_COLOURS = {
    'Low': '#2ecc71',
    'Medium': '#f39c12',
    'High': '#e74c3c',
    'Critical': '#2c3e50',
}


def register_callbacks(app, repo, analytics):

    # ── Live Clock ──────────────────────────────────────────────────────────────
    @app.callback(
        Output('live-clock', 'children'),
        Input('clock-interval', 'n_intervals'),
    )
    def update_clock(_):
        return datetime.now().strftime('%d %b %Y  %H:%M:%S')

    # ── Overview charts ─────────────────────────────────────────────────────────
    @app.callback(
        Output('overview-location-status-chart', 'figure'),
        Output('overview-route-status-chart', 'figure'),
        Output('overview-severity-chart', 'figure'),
        Output('critical-alerts-list', 'children'),
        Input('refresh-interval', 'n_intervals'),
    )
    def update_overview(_):
        loc_status = analytics.location_status_distribution()
        fig_loc = px.pie(
            names=list(loc_status.keys()),
            values=list(loc_status.values()),
            color=list(loc_status.keys()),
            color_discrete_map=STATUS_COLOURS,
            template=CHART_TEMPLATE,
            hole=0.4,
        )
        fig_loc.update_traces(textposition='inside', textinfo='percent+label')
        fig_loc.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))

        route_status = analytics.route_status_distribution()
        fig_route = px.pie(
            names=list(route_status.keys()),
            values=list(route_status.values()),
            color=list(route_status.keys()),
            color_discrete_map=STATUS_COLOURS,
            template=CHART_TEMPLATE,
            hole=0.4,
        )
        fig_route.update_traces(textposition='inside', textinfo='percent+label')
        fig_route.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))

        severity = analytics.notification_severity_distribution()
        fig_sev = px.bar(
            x=list(severity.keys()),
            y=list(severity.values()),
            color=list(severity.keys()),
            color_discrete_map=SEVERITY_COLOURS,
            template=CHART_TEMPLATE,
            labels={'x': 'Severity', 'y': 'Count'},
        )
        fig_sev.update_layout(showlegend=False, margin=dict(t=10, b=40, l=40, r=10))

        critical = sorted(
            repo.get_critical_notifications()[:5],
            key=lambda n: n.timestamp, reverse=True,
        )
        alert_items = []
        for notif in critical:
            loc = repo.get_location(notif.location_id)
            loc_name = loc.name if loc else notif.location_id
            alert_items.append(
                dbc.Alert([
                    html.Strong(f'{notif.alert_type.value} '),
                    dbc.Badge('CRITICAL', color='dark', className='me-2'),
                    html.Span(loc_name, className='me-2'),
                    html.Small(notif.timestamp.strftime('%d %b %H:%M'),
                               className='text-muted float-end'),
                    html.Br(),
                    html.Small(notif.message, className='text-muted'),
                ], color='danger', className='py-2 mb-2')
            )
        if not alert_items:
            alert_items = [dbc.Alert('No critical alerts.', color='success')]

        return fig_loc, fig_route, fig_sev, alert_items

    # ── Locations table ─────────────────────────────────────────────────────────
    @app.callback(
        Output('location-table-container', 'children'),
        Output('location-record-count', 'children'),
        Input('location-type-filter', 'value'),
        Input('location-status-filter', 'value'),
        Input('location-search', 'value'),
        Input('refresh-interval', 'n_intervals'),
    )
    def update_location_table(type_filter, status_filter, search, _):
        locs = repo.locations
        if type_filter and type_filter != 'All':
            locs = [l for l in locs if l.type.value == type_filter]
        if status_filter and status_filter != 'All':
            locs = [l for l in locs if l.status.value == status_filter]
        if search:
            term = search.lower()
            locs = [l for l in locs if term in l.name.lower()
                    or term in l.location_id.lower()]

        rows = [l.to_dict() for l in locs[:200]]
        table = dash_table.DataTable(
            data=rows,
            columns=[
                {'name': 'ID', 'id': 'location_id'},
                {'name': 'Name', 'id': 'name'},
                {'name': 'Type', 'id': 'type'},
                {'name': 'Status', 'id': 'status'},
                {'name': 'Capacity (t)', 'id': 'capacity_tonnes',
                 'type': 'numeric',
                 'format': {'specifier': ','}},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px',
                        'fontSize': '13px'},
            style_header={
                'backgroundColor': '#2c3e50', 'color': 'white',
                'fontWeight': 'bold',
            },
            style_data_conditional=[
                {'if': {'filter_query': '{status} = "Active"', 'column_id': 'status'},
                 'color': '#27ae60', 'fontWeight': 'bold'},
                {'if': {'filter_query': '{status} = "Inactive"', 'column_id': 'status'},
                 'color': '#7f8c8d'},
                {'if': {'filter_query': '{status} = "Under Maintenance"',
                        'column_id': 'status'},
                 'color': '#e67e22', 'fontWeight': 'bold'},
                {'if': {'row_index': 'odd'},
                 'backgroundColor': '#f8f9fa'},
            ],
            page_size=15,
            sort_action='native',
            filter_action='native',
            row_selectable='single',
            id='location-data-table',
        )
        count = f"Showing {len(rows)} of {len(repo.locations)} locations"
        return table, count

    # ── Routes table ────────────────────────────────────────────────────────────
    @app.callback(
        Output('route-table-container', 'children'),
        Output('route-record-count', 'children'),
        Input('route-type-filter', 'value'),
        Input('route-status-filter', 'value'),
        Input('route-distance-slider', 'value'),
        Input('refresh-interval', 'n_intervals'),
    )
    def update_route_table(type_filter, status_filter, max_dist, _):
        routes = repo.routes
        if type_filter and type_filter != 'All':
            routes = [r for r in routes if r.route_type.value == type_filter]
        if status_filter and status_filter != 'All':
            routes = [r for r in routes if r.status.value == status_filter]
        if max_dist is not None:
            routes = [r for r in routes if r.distance_km <= max_dist]

        rows = [r.to_dict() for r in routes[:200]]
        table = dash_table.DataTable(
            data=rows,
            columns=[
                {'name': 'ID', 'id': 'route_id'},
                {'name': 'From', 'id': 'start_location'},
                {'name': 'To', 'id': 'end_location'},
                {'name': 'Type', 'id': 'route_type'},
                {'name': 'Distance (km)', 'id': 'distance_km',
                 'type': 'numeric'},
                {'name': 'Status', 'id': 'status'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px',
                        'fontSize': '13px'},
            style_header={
                'backgroundColor': '#2c3e50', 'color': 'white',
                'fontWeight': 'bold',
            },
            style_data_conditional=[
                {'if': {'filter_query': '{status} = "Open"', 'column_id': 'status'},
                 'color': '#27ae60', 'fontWeight': 'bold'},
                {'if': {'filter_query': '{status} = "Closed"', 'column_id': 'status'},
                 'color': '#e74c3c', 'fontWeight': 'bold'},
                {'if': {'filter_query': '{status} = "Restricted"',
                        'column_id': 'status'},
                 'color': '#e67e22', 'fontWeight': 'bold'},
                {'if': {'row_index': 'odd'},
                 'backgroundColor': '#f8f9fa'},
            ],
            page_size=15,
            sort_action='native',
            row_selectable='single',
            id='route-data-table',
        )
        count = f"Showing {len(rows)} of {len(repo.routes)} routes"
        return table, count

    # ── Notifications table ─────────────────────────────────────────────────────
    @app.callback(
        Output('notification-table-container', 'children'),
        Output('notif-record-count', 'children'),
        Input('notif-type-filter', 'value'),
        Input('notif-severity-filter', 'value'),
        Input('notif-location-filter', 'value'),
        Input('refresh-interval', 'n_intervals'),
    )
    def update_notification_table(type_filter, severity_filter, loc_filter, _):
        notifs = repo.notifications
        if type_filter and type_filter != 'All':
            notifs = [n for n in notifs if n.alert_type.value == type_filter]
        if severity_filter and severity_filter != 'All':
            notifs = [n for n in notifs if n.severity.value == severity_filter]
        if loc_filter:
            term = loc_filter.strip().upper()
            notifs = [n for n in notifs if term in n.location_id.upper()]

        notifs_sorted = sorted(notifs, key=lambda n: n.timestamp, reverse=True)
        rows = [n.to_dict() for n in notifs_sorted[:200]]

        table = dash_table.DataTable(
            data=rows,
            columns=[
                {'name': 'ID', 'id': 'notification_id'},
                {'name': 'Alert Type', 'id': 'alert_type'},
                {'name': 'Location', 'id': 'location_id'},
                {'name': 'Severity', 'id': 'severity'},
                {'name': 'Message', 'id': 'message'},
                {'name': 'Timestamp', 'id': 'timestamp'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px',
                        'fontSize': '13px'},
            style_header={
                'backgroundColor': '#2c3e50', 'color': 'white',
                'fontWeight': 'bold',
            },
            style_data_conditional=[
                {'if': {'filter_query': '{severity} = "Critical"',
                        'column_id': 'severity'},
                 'backgroundColor': '#2c3e50', 'color': 'white',
                 'fontWeight': 'bold'},
                {'if': {'filter_query': '{severity} = "High"',
                        'column_id': 'severity'},
                 'color': '#e74c3c', 'fontWeight': 'bold'},
                {'if': {'filter_query': '{severity} = "Medium"',
                        'column_id': 'severity'},
                 'color': '#e67e22'},
                {'if': {'filter_query': '{severity} = "Low"',
                        'column_id': 'severity'},
                 'color': '#27ae60'},
                {'if': {'row_index': 'odd'},
                 'backgroundColor': '#f8f9fa'},
            ],
            page_size=15,
            sort_action='native',
        )
        count = f"Showing {len(rows)} of {len(repo.notifications)} notifications"
        return table, count

    # ── Users table ─────────────────────────────────────────────────────────────
    @app.callback(
        Output('user-table-container', 'children'),
        Output('user-record-count', 'children'),
        Output('user-role-chart', 'figure'),
        Input('user-role-filter', 'value'),
        Input('user-active-filter', 'value'),
        Input('user-search', 'value'),
        Input('refresh-interval', 'n_intervals'),
    )
    def update_user_table(role_filter, active_filter, search, _):
        users = repo.users
        if role_filter and role_filter != 'All':
            users = [u for u in users if u.role.value == role_filter]
        if active_filter and active_filter != 'All':
            users = [u for u in users
                     if (u.active and active_filter == 'Yes')
                     or (not u.active and active_filter == 'No')]
        if search:
            term = search.lower()
            users = [u for u in users
                     if term in u.name.lower() or term in u.email.lower()]

        rows = [u.to_dict() for u in users[:200]]
        table = dash_table.DataTable(
            data=rows,
            columns=[
                {'name': 'ID', 'id': 'user_id'},
                {'name': 'Name', 'id': 'name'},
                {'name': 'Role', 'id': 'role'},
                {'name': 'Email', 'id': 'email'},
                {'name': 'Active', 'id': 'active'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px',
                        'fontSize': '13px'},
            style_header={
                'backgroundColor': '#2c3e50', 'color': 'white',
                'fontWeight': 'bold',
            },
            style_data_conditional=[
                {'if': {'filter_query': '{active} = "Yes"', 'column_id': 'active'},
                 'color': '#27ae60', 'fontWeight': 'bold'},
                {'if': {'filter_query': '{active} = "No"', 'column_id': 'active'},
                 'color': '#e74c3c'},
                {'if': {'row_index': 'odd'},
                 'backgroundColor': '#f8f9fa'},
            ],
            page_size=15,
            sort_action='native',
        )
        count = f"Showing {len(rows)} of {len(repo.users)} personnel"

        role_dist = analytics.user_role_distribution()
        fig_role = px.pie(
            names=list(role_dist.keys()),
            values=list(role_dist.values()),
            color_discrete_sequence=COLOUR_SEQUENCE,
            template=CHART_TEMPLATE,
            hole=0.35,
        )
        fig_role.update_traces(textposition='inside', textinfo='percent+label')
        fig_role.update_layout(
            showlegend=True,
            legend=dict(font=dict(size=10)),
            margin=dict(t=10, b=10, l=10, r=10),
        )

        return table, count, fig_role

    # ── Analytics charts ────────────────────────────────────────────────────────
    @app.callback(
        Output('analytics-location-type', 'figure'),
        Output('analytics-capacity-type', 'figure'),
        Output('analytics-notif-trend', 'figure'),
        Output('analytics-alert-types', 'figure'),
        Output('analytics-route-types', 'figure'),
        Output('analytics-route-distance', 'figure'),
        Output('analytics-top-locations', 'figure'),
        Output('analytics-bottlenecks', 'children'),
        Input('refresh-interval', 'n_intervals'),
    )
    def update_analytics(_):
        loc_types = analytics.location_type_distribution()
        fig_loc_type = px.bar(
            x=list(loc_types.keys()),
            y=list(loc_types.values()),
            color=list(loc_types.keys()),
            color_discrete_sequence=COLOUR_SEQUENCE,
            template=CHART_TEMPLATE,
            labels={'x': 'Type', 'y': 'Count'},
        )
        fig_loc_type.update_layout(
            showlegend=False, margin=dict(t=10, b=60, l=40, r=10)
        )

        cap_type = analytics.capacity_by_type()
        fig_cap = px.bar(
            x=list(cap_type.keys()),
            y=[v / 1_000_000 for v in cap_type.values()],
            color=list(cap_type.keys()),
            color_discrete_sequence=COLOUR_SEQUENCE,
            template=CHART_TEMPLATE,
            labels={'x': 'Type', 'y': 'Capacity (M tonnes)'},
        )
        fig_cap.update_layout(
            showlegend=False, margin=dict(t=10, b=60, l=60, r=10)
        )

        trend = analytics.notification_trend()
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=list(trend.keys()),
            y=list(trend.values()),
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6),
        ))
        fig_trend.update_layout(
            template=CHART_TEMPLATE,
            xaxis_title='Date', yaxis_title='Notifications',
            margin=dict(t=10, b=40, l=60, r=10),
        )

        alert_types = analytics.notification_type_distribution()
        fig_alert = px.pie(
            names=list(alert_types.keys()),
            values=list(alert_types.values()),
            color_discrete_sequence=COLOUR_SEQUENCE,
            template=CHART_TEMPLATE,
            hole=0.35,
        )
        fig_alert.update_traces(textposition='inside', textinfo='percent')
        fig_alert.update_layout(margin=dict(t=10, b=10, l=10, r=10))

        route_types = analytics.route_type_distribution()
        fig_route_type = px.bar(
            x=list(route_types.values()),
            y=list(route_types.keys()),
            orientation='h',
            color=list(route_types.keys()),
            color_discrete_sequence=COLOUR_SEQUENCE,
            template=CHART_TEMPLATE,
            labels={'x': 'Count', 'y': 'Route Type'},
        )
        fig_route_type.update_layout(
            showlegend=False, margin=dict(t=10, b=40, l=10, r=10)
        )

        avg_dist = analytics.average_route_distance_by_type()
        fig_dist = px.bar(
            x=list(avg_dist.keys()),
            y=list(avg_dist.values()),
            color=list(avg_dist.keys()),
            color_discrete_sequence=COLOUR_SEQUENCE,
            template=CHART_TEMPLATE,
            labels={'x': 'Route Type', 'y': 'Avg Distance (km)'},
        )
        fig_dist.update_layout(
            showlegend=False, margin=dict(t=10, b=80, l=60, r=10)
        )

        top_locs = analytics.top_alert_locations(10)
        loc_ids = [t[0] for t in top_locs]
        loc_counts = [t[1] for t in top_locs]
        loc_names = []
        for lid in loc_ids:
            loc = repo.get_location(lid)
            loc_names.append(loc.name if loc else lid)

        fig_top = px.bar(
            x=loc_names,
            y=loc_counts,
            color=loc_names,
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=CHART_TEMPLATE,
            labels={'x': 'Location', 'y': 'Alert Count'},
        )
        fig_top.update_layout(
            showlegend=False,
            margin=dict(t=10, b=100, l=60, r=10),
            xaxis_tickangle=-30,
        )

        bottlenecks = analytics.identify_bottlenecks()
        if bottlenecks:
            cards = [
                dbc.Alert([
                    html.Strong(f"{b['area']}: "),
                    html.Span(b['issue']),
                    html.Br(),
                    html.Small(f"Impact: {b['impact']}", className='text-muted'),
                ], color='warning', className='mb-2')
                for b in bottlenecks
            ]
        else:
            cards = [dbc.Alert('No significant bottlenecks identified.',
                               color='success')]

        return (fig_loc_type, fig_cap, fig_trend, fig_alert,
                fig_route_type, fig_dist, fig_top, cards)

    # ── Location modal – open ───────────────────────────────────────────────────
    @app.callback(
        Output('location-modal', 'is_open'),
        Output('modal-loc-id', 'value'),
        Output('modal-loc-name', 'value'),
        Output('modal-loc-type', 'value'),
        Output('modal-loc-status', 'value'),
        Output('modal-loc-capacity', 'value'),
        Output('modal-loc-feedback', 'children'),
        Input('btn-add-location', 'n_clicks'),
        Input('modal-loc-cancel', 'n_clicks'),
        Input('modal-loc-save', 'n_clicks'),
        State('modal-loc-id', 'value'),
        State('modal-loc-name', 'value'),
        State('modal-loc-type', 'value'),
        State('modal-loc-status', 'value'),
        State('modal-loc-capacity', 'value'),
        State('location-modal', 'is_open'),
        prevent_initial_call=True,
    )
    def toggle_location_modal(open_clicks, cancel_clicks, save_clicks,
                              loc_id, loc_name, loc_type, loc_status,
                              loc_capacity, is_open):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'btn-add-location':
            return True, '', '', 'Berth', 'Active', 5000, ''

        if trigger == 'modal-loc-cancel':
            return False, no_update, no_update, no_update, no_update, no_update, ''

        if trigger == 'modal-loc-save':
            if not loc_id or not loc_name:
                feedback = dbc.Alert('ID and Name are required.', color='danger')
                return True, loc_id, loc_name, loc_type, loc_status, loc_capacity, feedback
            try:
                new_loc = Location(
                    location_id=loc_id,
                    name=loc_name,
                    type=LocationType(loc_type),
                    status=LocationStatus(loc_status),
                    capacity_tonnes=int(loc_capacity or 0),
                )
                if repo.add_location(new_loc, performed_by='dashboard_user'):
                    feedback = dbc.Alert(f'Location {loc_id} added.', color='success')
                    return False, '', '', 'Berth', 'Active', 5000, feedback
                else:
                    feedback = dbc.Alert(f'ID {loc_id} already exists.',
                                         color='warning')
                    return True, loc_id, loc_name, loc_type, loc_status, loc_capacity, feedback
            except Exception as e:
                feedback = dbc.Alert(f'Error: {e}', color='danger')
                return True, loc_id, loc_name, loc_type, loc_status, loc_capacity, feedback

        raise PreventUpdate

    # ── Notification modal – open ───────────────────────────────────────────────
    @app.callback(
        Output('notification-modal', 'is_open'),
        Output('modal-notif-feedback', 'children'),
        Input('btn-add-notification', 'n_clicks'),
        Input('modal-notif-cancel', 'n_clicks'),
        Input('modal-notif-save', 'n_clicks'),
        State('modal-notif-type', 'value'),
        State('modal-notif-severity', 'value'),
        State('modal-notif-location', 'value'),
        State('modal-notif-message', 'value'),
        State('notification-modal', 'is_open'),
        prevent_initial_call=True,
    )
    def toggle_notification_modal(open_c, cancel_c, save_c,
                                  n_type, n_sev, n_loc, n_msg, is_open):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'btn-add-notification':
            return True, ''
        if trigger == 'modal-notif-cancel':
            return False, ''
        if trigger == 'modal-notif-save':
            if not n_loc or not n_msg:
                return True, dbc.Alert('Location and Message are required.',
                                       color='danger')
            try:
                existing_ids = {n.notification_id for n in repo.notifications}
                new_id = f'N{len(repo.notifications) + 1:04d}'
                while new_id in existing_ids:
                    new_id = f'N{int(new_id[1:]) + 1:04d}'

                notif = Notification(
                    notification_id=new_id,
                    alert_type=AlertType(n_type),
                    location_id=n_loc.strip().upper(),
                    severity=Severity(n_sev),
                    message=n_msg,
                    timestamp=datetime.now(),
                )
                repo.add_notification(notif, performed_by='dashboard_user')
                return False, dbc.Alert(f'Alert {new_id} created.', color='success')
            except Exception as e:
                return True, dbc.Alert(f'Error: {e}', color='danger')

        raise PreventUpdate

    # ── Login / logout ──────────────────────────────────────────────────────────
    LOGIN_STYLE = {'minHeight': '100vh', 'paddingTop': '40px',
                   'backgroundColor': '#f0f4f8'}

    @app.callback(
        Output('session-store', 'data'),
        Output('login-page', 'style'),
        Output('main-content', 'style'),
        Output('login-feedback', 'children'),
        Input('btn-login-id', 'n_clicks'),
        Input('btn-login-role', 'n_clicks'),
        Input('btn-logout', 'n_clicks'),
        State('login-user-id', 'value'),
        State('login-role-select', 'value'),
        prevent_initial_call=True,
    )
    def handle_auth(_n1, _n2, _n3, user_id_input, role_input):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'btn-logout':
            return None, LOGIN_STYLE, {'display': 'none'}, ''

        if trigger == 'btn-login-id':
            if not user_id_input:
                return no_update, no_update, no_update, dbc.Alert(
                    'Please enter a User ID.', color='warning', className='mb-0')
            uid = user_id_input.strip().upper()
            user = repo.get_user(uid)
            if not user:
                return no_update, no_update, no_update, dbc.Alert(
                    f'User "{uid}" not found.', color='danger', className='mb-0')
            if not user.active:
                return no_update, no_update, no_update, dbc.Alert(
                    f'Account {uid} is inactive.', color='warning', className='mb-0')
            session = {'user_id': user.user_id, 'name': user.name,
                       'role': user.role.value}
            return session, {'display': 'none'}, {}, ''

        if trigger == 'btn-login-role':
            if not role_input:
                return no_update, no_update, no_update, dbc.Alert(
                    'Please select a role.', color='warning', className='mb-0')
            matching = [u for u in repo.users
                        if u.role.value == role_input and u.active]
            if not matching:
                return no_update, no_update, no_update, dbc.Alert(
                    f'No active {role_input} users found.',
                    color='danger', className='mb-0')
            user = matching[0]
            session = {'user_id': user.user_id, 'name': user.name,
                       'role': user.role.value}
            return session, {'display': 'none'}, {}, ''

        raise PreventUpdate

    # ── Navbar user info ────────────────────────────────────────────────────────
    @app.callback(
        Output('navbar-user-info', 'children'),
        Input('session-store', 'data'),
    )
    def update_navbar_user(session_data):
        if not session_data:
            return ''
        return [
            html.I(className='bi bi-person-circle me-1'),
            html.Span(f"{session_data['name']} "),
            dbc.Badge(session_data['role'], color='info', pill=True, className='ms-1'),
        ]

    # ── Permission enforcement ──────────────────────────────────────────────────
    @app.callback(
        Output('nav-tab-analytics', 'disabled'),
        Output('nav-tab-audit', 'disabled'),
        Output('btn-add-location', 'style'),
        Output('btn-add-route', 'style'),
        Output('btn-add-notification', 'style'),
        Input('session-store', 'data'),
    )
    def apply_permissions(session_data):
        hidden = {'display': 'none'}
        if not session_data:
            return True, True, hidden, hidden, hidden
        role = UserRole(session_data['role'])
        perms = ROLE_PERMISSIONS.get(role, set())
        return (
            'view_analytics' not in perms,
            'view_audit_log' not in perms,
            {} if 'manage_locations' in perms else hidden,
            {} if 'manage_routes' in perms else hidden,
            {} if 'manage_notifications' in perms else hidden,
        )

    # ── Audit log table ─────────────────────────────────────────────────────────
    @app.callback(
        Output('audit-table-container', 'children'),
        Input('refresh-interval', 'n_intervals'),
        Input('main-tabs', 'active_tab'),
    )
    def update_audit_table(_, active_tab):
        if active_tab != 'tab-audit':
            raise PreventUpdate
        entries = repo.get_audit_log_dicts()[:200]
        table = dash_table.DataTable(
            data=entries,
            columns=[
                {'name': 'Timestamp', 'id': 'timestamp'},
                {'name': 'Action', 'id': 'action'},
                {'name': 'Entity Type', 'id': 'entity_type'},
                {'name': 'Entity ID', 'id': 'entity_id'},
                {'name': 'Performed By', 'id': 'performed_by'},
                {'name': 'Details', 'id': 'details'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '12px'},
            style_header={
                'backgroundColor': '#2c3e50', 'color': 'white',
                'fontWeight': 'bold',
            },
            style_data_conditional=[
                {'if': {'filter_query': '{action} contains "REMOVE"'},
                 'color': '#e74c3c'},
                {'if': {'filter_query': '{action} = "ADD"'},
                 'color': '#27ae60'},
                {'if': {'row_index': 'odd'},
                 'backgroundColor': '#f8f9fa'},
            ],
            page_size=20,
            sort_action='native',
        )
        return table
