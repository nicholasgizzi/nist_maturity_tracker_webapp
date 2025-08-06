from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import System, SystemMapping
from datetime import datetime
from flask_login import login_required
from flask_login import current_user
from app.models import Review
from app.models import Subcategory
from sqlalchemy.exc import IntegrityError

bp = Blueprint('mappings', __name__, url_prefix='/systems/<int:system_id>/mappings')

@bp.route('/add_mapping', methods=['GET','POST'])
@login_required
def add_mapping(system_id):
    system = System.query.get_or_404(system_id)
    if request.method=='POST':
        sub_id = int(request.form['subcategory_id'])
        sub = Subcategory.query.get_or_404(sub_id)
        sub_name = sub.name
        sys_name = system.name

        m = SystemMapping(
          system_id=system.id,
          subcategory_id=sub_id,
          score=int(request.form['score']),
          reviewer=request.form.get('reviewer'),
          notes=request.form.get('notes'),
          last_reviewed=datetime.utcnow()
        )
        db.session.add(m)
        # Commit the new mapping first
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"add_mapping IntegrityError: {e.orig}")
            flash("Could not save mapping.", 'danger')
            return redirect(url_for('systems.system_detail', system_id=system.id))

        # Then attempt to log it (non-blocking)
        try:
            db.session.add(Review(
                mapping_id=m.id,
                score=m.score,
                reviewer=current_user.username,
                review_date=datetime.utcnow(),
                notes=f"Created mapping {sub_name} for {sys_name}"
            ))
            db.session.commit()
        except Exception as log_err:
            db.session.rollback()
            current_app.logger.warning(f"Failed to log mapping creation: {log_err}")

        flash('Mapping added.', 'success')
        return redirect(url_for('systems.system_detail', system_id=system.id))
    subs = Subcategory.query.all()
    return render_template('add_mapping.html', system=system, subcategories=subs)

@bp.route('/mappings/<int:mapping_id>/edit', methods=['GET','POST'])
def edit_mapping(system_id, mapping_id):
    mapping = SystemMapping.query.get_or_404(mapping_id)
    # capture old values for audit
    old_score = mapping.score
    sub_name = mapping.subcategory.name
    sys_name = mapping.system.name
    if request.method=='POST':
        mapping.score = int(request.form['score'])
        mapping.reviewer = request.form.get('reviewer')
        mapping.notes = request.form.get('notes')
        mapping.last_reviewed = datetime.utcnow()
        # Commit the mapping update first
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"edit_mapping IntegrityError: {e.orig}")
            flash("Could not update mapping.", 'danger')
            return redirect(url_for('systems.system_detail', system_id=system_id))

        # Then attempt to log the update
        try:
            db.session.add(Review(
                mapping_id=mapping.id,
                score=mapping.score,
                reviewer=current_user.username,
                review_date=datetime.utcnow(),
                notes=(
                    f"Changed {sub_name} on {sys_name} "
                    f"from {old_score} to {mapping.score}"
                    + (f"; notes: {mapping.notes}" if mapping.notes else "")
                )
            ))
            db.session.commit()
        except Exception as log_err:
            db.session.rollback()
            current_app.logger.warning(f"Failed to log mapping update: {log_err}")

        flash('Mapping updated.', 'success')
        return redirect(url_for('systems.system_detail', system_id=system_id))
    from app.models import Subcategory
    subs = Subcategory.query.all()
    return render_template('edit_mapping.html', system_id=system_id, mapping=mapping, subcategories=subs)

@bp.route('/mappings/<int:mapping_id>/delete', methods=['POST'])
def delete_mapping(system_id, mapping_id):
    m = SystemMapping.query.get_or_404(mapping_id)
    sub_name = m.subcategory.name
    sys_name = m.system.name
    mapping_id_val = m.id
    # Commit the deletion first
    try:
        db.session.delete(m)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"delete_mapping IntegrityError: {e.orig}")
        flash("Could not delete mapping.", 'danger')
        return redirect(url_for('systems.system_detail', system_id=system_id))

    # Then attempt to log the deletion
    try:
        db.session.add(Review(
            mapping_id=mapping_id_val,
            score=0,
            reviewer=current_user.username,
            review_date=datetime.utcnow(),
            notes=f"Deleted mapping {sub_name} from {sys_name}"
        ))
        db.session.commit()
    except Exception as log_err:
        db.session.rollback()
        current_app.logger.warning(f"Failed to log mapping deletion: {log_err}")

    flash('Mapping deleted.', 'success')
    return redirect(url_for('systems.system_detail', system_id=system_id))
