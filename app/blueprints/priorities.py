from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Subcategory, PriorityLevel
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Review

bp = Blueprint('priorities', __name__, url_prefix='/priorities')

@bp.route('')
@login_required
def priorities_overview():
    subs = Subcategory.query.order_by(Subcategory.category_id).all()
    return render_template('priorities.html', subcategories=subs, view='all')

@bp.route('/<level>')
def priorities_filtered(level):
    try:
        p = PriorityLevel[level.upper()]
    except KeyError:
        abort(404)
    subs = Subcategory.query.filter_by(priority=p).order_by(Subcategory.category_id).all()
    return render_template('priorities.html', subcategories=subs, view=level)

@bp.route('/update_all', methods=['POST'])
def update_priorities_bulk():
    for key,val in request.form.items():
        if key.startswith('priority_') and val:
            sub_id = int(key.split('_',1)[1])
            try:
                lvl = PriorityLevel[val.upper()]
                sub = Subcategory.query.get(sub_id)
                sub.priority = lvl
                # audit log for priority change
                db.session.flush()  # ensure sub.id is available
                db.session.add(Review(
                    mapping_id=None,
                    reviewer=current_user.username,
                    review_date=datetime.utcnow(),
                    notes=f"Priority for subcategory '{sub.name}' set to {lvl.name}"
                ))
            except:
                continue
    db.session.commit()
    flash('Priorities saved.', 'success')
    return redirect(url_for('priorities.priorities_overview'))
