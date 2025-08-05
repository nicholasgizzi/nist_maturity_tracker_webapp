from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import System, SystemMapping
from datetime import datetime
from flask_login import login_required

bp = Blueprint('mappings', __name__, url_prefix='/systems/<int:system_id>/mappings')

@bp.route('/add_mapping', methods=['GET','POST'])
@login_required
def add_mapping(system_id):
    system = System.query.get_or_404(system_id)
    if request.method=='POST':
        m = SystemMapping(
          system_id=system.id,
          subcategory_id=int(request.form['subcategory_id']),
          score=int(request.form['score']),
          reviewer=request.form.get('reviewer'),
          notes=request.form.get('notes'),
          last_reviewed=datetime.utcnow()
        )
        db.session.add(m)
        db.session.commit()
        flash('Mapping added.', 'success')
        return redirect(url_for('systems.system_detail', system_id=system.id))
    from app.models import Subcategory
    subs = Subcategory.query.all()
    return render_template('add_mapping.html', system=system, subcategories=subs)

@bp.route('/mappings/<int:mapping_id>/edit', methods=['GET','POST'])
def edit_mapping(system_id, mapping_id):
    mapping = SystemMapping.query.get_or_404(mapping_id)
    if request.method=='POST':
        mapping.score = int(request.form['score'])
        mapping.reviewer = request.form.get('reviewer')
        mapping.notes = request.form.get('notes')
        mapping.last_reviewed = datetime.utcnow()
        db.session.commit()
        flash('Mapping updated.', 'success')
        return redirect(url_for('systems.system_detail', system_id=system_id))
    from app.models import Subcategory
    subs = Subcategory.query.all()
    return render_template('edit_mapping.html', system_id=system_id, mapping=mapping, subcategories=subs)

@bp.route('/mappings/<int:mapping_id>/delete', methods=['POST'])
def delete_mapping(system_id, mapping_id):
    m = SystemMapping.query.get_or_404(mapping_id)
    db.session.delete(m)
    db.session.commit()
    flash('Mapping deleted.', 'success')
    return redirect(url_for('systems.system_detail', system_id=system_id))
