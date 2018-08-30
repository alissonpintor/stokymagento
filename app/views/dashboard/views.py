from flask import Blueprint, render_template
from flask_login import login_required
import locale


locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
@login_required
def index():
    return render_template('dashboard/main.html')
