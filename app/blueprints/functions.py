from flask import Blueprint, render_template, request
from collections import defaultdict
from app.models import Category, Subcategory, SystemMapping
from flask_login import login_required

bp = Blueprint('functions', __name__, url_prefix='/functions')

@bp.route('/<function>')
@login_required
def view_function(function):
    code = function.upper()
    cat = Category.query.filter_by(code=code).first_or_404()
    # allow optional subcategory filter via query string
    subcat_id = request.args.get('subcategory_id', type=int)
    if subcat_id:
        subs = Subcategory.query.filter_by(category_id=cat.id, id=subcat_id).all()
    else:
        subs = Subcategory.query.filter_by(category_id=cat.id).all()
    maps = SystemMapping.query.filter(SystemMapping.subcategory_id.in_([s.id for s in subs])).all()
    by_sys = defaultdict(list)
    for m in maps:
        by_sys[m.system].append(m)
    return render_template('function_detail.html', category=cat, system_map=by_sys)
