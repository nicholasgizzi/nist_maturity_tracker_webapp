from flask import Blueprint, render_template, request
from app.models import Category, Subcategory, SystemMapping, Review, System, Risk
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

    def avg_by(since=None, before=None):
        # initialize every function to an empty list
        buckets = {f: [] for f in funcs}
        for s in subcats:
            # Skip subcategories that don't match the selected priority view
            if view != 'all' and (s.priority is None or s.priority.value.lower() != view):
                continue
            for m in s.system_mappings:
                # Filter by date range
                if since and m.last_reviewed < since:
                    continue
                if before and m.last_reviewed >= before:
                    continue
                buckets[s.category.code].append(m.score)
        # compute averages (None if no scores)
        return {f: (round(sum(vals)/len(vals),2) if vals else None)
                for f, vals in buckets.items()}

    current = avg_by()                              # all scores ever
    previous = avg_by(before=cutoff)                # those from more than 90 days ago

    # Better trend calculation - only compare if we have historical data
    change = {}
    for f in funcs:
        if previous[f] is not None and current[f] is not None:
            change[f] = round(current[f] - previous[f], 2)
        else:
            change[f] = 0  # No trend available

    # Executive-focused metrics
    total_systems = System.query.count()
    # Calculate high-risk using actual database columns (severity * likelihood >= 15)
    high_risk_count = Risk.query.filter((Risk.severity * Risk.likelihood) >= 15).count()
    low_maturity_count = sum(1 for score in current.values()
                           if score is not None and score < 2.0)

    # Recent assessments (more meaningful than raw review count)
    recent_assessments = SystemMapping.query \
        .filter(SystemMapping.last_reviewed >= cutoff) \
        .count()

    return render_template(
        'dashboard.html',
        current_scores=current,
        change_scores=change,
        view=view,
        funcs=funcs,
        name_map=name_map,
        function_colors=function_colors,
        total_systems=total_systems,
        high_risk_count=high_risk_count,
        low_maturity_count=low_maturity_count,
        recent_assessments=recent_assessments,
    )
