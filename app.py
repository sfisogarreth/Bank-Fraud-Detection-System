import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta
from flask import Flask, redirect, url_for, render_template, session
from flask_wtf.csrf import CSRFProtect
from config import config_by_name

csrf = CSRFProtect()
os.makedirs('logs', exist_ok=True)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    app.config.from_object(config_by_name[config_name])
    app.secret_key = app.config['SECRET_KEY']
    
    # CSRF Protection — ALL forms must include {{ csrf_token() }}
    csrf.init_app(app)
    
    # Session Security
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
    )
    
    # Logging
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/mazi.log', maxBytes=102400, backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('MAZI Fraud AI startup')
    
    # Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.transactions import transactions_bp
    from routes.investigations import investigations_bp
    from routes.analytics import analytics_bp
    from routes.settings import settings_bp
    from routes.api import api_bp
    from routes.users import users_bp
    from routes.audit_logs import audit_logs_bp
    from routes.reports import reports_bp
    
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(investigations_bp, url_prefix='/investigations')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(users_bp,url_prefix="/users")
    app.register_blueprint(audit_logs_bp,url_prefix="/audit-logs")
    app.register_blueprint(reports_bp,url_prefix="/reports")
    
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.dashboard'))
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('coming_soon.html', page_name='Page Not Found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return render_template('coming_soon.html', page_name='Server Error'), 500
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'version': '1.0.2', 'database': 'sqlite'}, 200
    @app.context_processor
    def inject_user():

        return {

            "current_user":
                session.get("username"),

            "current_role":
                session.get("role")

        }
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)