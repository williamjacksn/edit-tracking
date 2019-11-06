import edit_tracking.db
import edit_tracking.settings
import edit_tracking.util
import flask
import functools
import jwt
import logging
import requests
import sys
import urllib.parse
import uuid
import waitress
import werkzeug.middleware.proxy_fix

settings = edit_tracking.settings.Settings()

app = flask.Flask(__name__)
app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_port=1)
app.secret_key = settings.secret_key

app.jinja_env.finalize = edit_tracking.util.clean_none


def permission_required(permission: str):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            app.logger.debug(f'Checking permission for {flask.g.email}')
            if flask.g.email is None:
                flask.session['sign-in-target-url'] = flask.request.url
                return flask.redirect(flask.url_for('sign_in'))
            if permission in flask.g.permissions:
                return f(*args, **kwargs)
            flask.g.required_permission = permission
            return flask.render_template('not-authorized.html')

        return decorated_function

    return decorator


@app.before_request
def setup_request():
    app.logger.info(f'{flask.request.method} {flask.request.path}')
    if settings.permanent_sessions:
        flask.session.permanent = True
    flask.g.settings = settings
    flask.g.email = flask.session.get('email')
    flask.g.db = edit_tracking.db.Database(settings.db)
    flask.g.permissions = flask.g.db.get_permissions(flask.g.email)


@app.route('/authorize')
def authorize():
    for key, value in flask.request.values.items():
        app.logger.debug(f'{key}: {value}')
    if flask.session.get('state') != flask.request.values.get('state'):
        return 'State mismatch', 401
    discovery_document = requests.get(settings.openid_discovery_document).json()
    token_endpoint = discovery_document.get('token_endpoint')
    data = {
        'code': flask.request.values.get('code'),
        'client_id': settings.openid_client_id,
        'client_secret': settings.openid_client_secret,
        'redirect_uri': flask.url_for('authorize', _external=True),
        'grant_type': 'authorization_code'
    }
    resp = requests.post(token_endpoint, data=data).json()
    id_token = resp.get('id_token')
    algorithms = discovery_document.get('id_token_signing_alg_values_supported')
    claim = jwt.decode(id_token, verify=False, algorithms=algorithms)
    flask.session['email'] = claim.get('email')
    return flask.redirect(flask.url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@permission_required('admin')
def index():
    db: edit_tracking.db.Database = flask.g.db
    if flask.request.method == 'GET':
        flask.g.records = db.get_edit_tracking()
        flask.g.project_list = sorted(set([r.get('project') for r in flask.g.records]))
        flask.g.editor_list = sorted(set([r.get('editor') for r in flask.g.records]))
        flask.g.editing_transcription_list = sorted(set([r.get('editing_transcription') for r in flask.g.records]))
        return flask.render_template('index.html')
    else:
        for k, v in flask.request.values.lists():
            app.logger.debug(f'{k}: {v}')
        params = flask.request.values.to_dict()

        for k in params:
            if params.get(k) == '':
                params[k] = None

        app.logger.debug(f'params: {params}')
        if params.get('id'):
            db.update_edit_tracking(params)
        else:
            db.add_edit_tracking(params)

        return flask.redirect(flask.url_for('index'))


@app.route('/admin')
@permission_required('admin')
def admin():
    db: edit_tracking.db.Database = flask.g.db
    flask.g.users = db.get_users()
    flask.g.available_permissions = {
        'admin': 'view, create, and edit records; grant permissions to other users'
    }
    return flask.render_template('admin.html')


@app.route('/admin/edit-user', methods=['POST'])
@permission_required('admin')
def admin_edit_user():
    db: edit_tracking.db.Database = flask.g.db
    email = flask.request.values.get('email')
    permissions = flask.request.values.getlist('permissions')
    db.set_permissions(email, permissions)
    return flask.redirect(flask.url_for('admin'))


@app.route('/delete', methods=['POST'])
@permission_required('admin')
def delete():
    db: edit_tracking.db.Database = flask.g.db
    record_id = flask.request.values.get('id')
    db.delete_edit_tracking(record_id)
    return flask.redirect(flask.url_for('index'))


@app.route('/sign-in')
def sign_in():
    state = str(uuid.uuid4())
    flask.session['state'] = state
    redirect_uri = flask.url_for('authorize', _external=True)
    query = {
        'client_id': settings.openid_client_id,
        'response_type': 'code',
        'scope': 'openid email profile',
        'redirect_uri': redirect_uri,
        'state': state
    }
    discovery_document = requests.get(settings.openid_discovery_document).json()
    auth_endpoint = discovery_document.get('authorization_endpoint')
    auth_url = f'{auth_endpoint}?{urllib.parse.urlencode(query)}'
    return flask.redirect(auth_url, 307)


@app.route('/sign-out')
def sign_out():
    flask.session.pop('email')
    return flask.redirect(flask.url_for('index'))


def main():
    logging.basicConfig(format=settings.log_format, level=logging.DEBUG, stream=sys.stdout)
    app.logger.debug(f'edit-tracking {settings.version}')
    if not settings.log_level == 'DEBUG':
        app.logger.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)

    db = edit_tracking.db.Database(settings.db)
    db.migrate()
    if settings.bootstrap_admin:
        app.logger.info(f'Bootstrapping admin permissions for {settings.bootstrap_admin}')
        permissions = db.get_permissions(settings.bootstrap_admin)
        if 'admin' not in permissions:
            permissions.append('admin')
            db.set_permissions(settings.bootstrap_admin, permissions)

    waitress.serve(app, port=settings.port, ident=None)
