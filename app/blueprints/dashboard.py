from flask import Blueprint, render_template, request
from app.models import Category, Subcategory, SystemMapping
from datetime import datetime, timedelta
from collections import defaultdict
from flask_login import login_required

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def dashboard():
    view = request.args.get('view', 'all').lower()
    cutoff = datetime.utcnow() - timedelta(days=90)

    # grab the six functions in code order
    categories = Category.query.order_by(Category.id).all()
    funcs = [c.code for c in categories]
    name_map = {c.code: c.name for c in categories}
    subcats = Subcategory.query.all()

    function_colors = {
        'GV': '#F8F1C8',
        'ID': '#4DB2E6',
        'PR': '#C079D6',
        'DE': '#FDBE5A',
        'RS': '#D9241F',
        'RC': '#82CF6B'
    }

    def avg_by(since=None):
        # initialize every function to an empty list
        buckets = {f: [] for f in funcs}
        for s in subcats:
            # Skip subcategories that don't match the selected priority view
            if view != 'all' and (s.priority is None or s.priority.value.lower() != view):
                continue
            for m in s.system_mappings:
                if since and m.last_reviewed >= since:
                    continue
                buckets[s.category.code].append(m.score)
        # compute averages (None if no scores)
        return {f: (round(sum(vals)/len(vals),2) if vals else None)
                for f, vals in buckets.items()}

    current = avg_by()                  # all scores ever
    previous = avg_by(since=cutoff)     # those before cutoff
    # subtract; if current None treat as 0
    change = {f: ((current[f] or 0) - (previous[f] or 0))
              for f in funcs}

    return render_template(
        'dashboard.html',
        current_scores=current,
        change_scores=change,
        view=view,
        funcs=funcs,
        name_map=name_map,
        function_colors=function_colors
        )
