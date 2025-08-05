from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import System, SystemMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from flask_login import login_required

bp = Blueprint('systems', __name__, url_prefix='/systems')

@bp.route('')
@login_required
def list_systems():
    systems = System.query.all()
    return render_template('index.html', systems=systems)

@bp.route('/add', methods=['GET','POST'])
def add_system():
    if request.method == 'POST':
        name = request.form['name'].strip()
        existing = System.query.filter(func.lower(System.name)==name.lower()).first()
        if existing:
            flash(f"‘{existing.name}’ exists, redirecting…", 'info')
            return redirect(url_for('systems.system_detail', system_id=existing.id))
        sys = System(name=name,
                     description=request.form.get('description'),
                     owner=request.form.get('owner'),
                     notes=request.form.get('notes'))
        db.session.add(sys)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Could not save—name conflict.", 'danger')
            return redirect(url_for('systems.list_systems'))
        return redirect(url_for('mappings.add_mapping', system_id=sys.id))
    return render_template('add_system.html')

@bp.route('/<int:system_id>')
def system_detail(system_id):
    system = System.query.get_or_404(system_id)
    return render_template('system_detail.html', system=system)

@bp.route('/<int:system_id>/edit', methods=['GET','POST'])
def edit_system(system_id):
    system = System.query.get_or_404(system_id)
    if request.method=='POST':
        new_name = request.form['name'].strip()
        # If name changed (including case-only), enforce uniqueness among other systems
        if new_name != system.name:
            existing = System.query.filter(
                func.lower(System.name) == new_name.lower(),
                System.id != system.id
            ).first()
            if existing:
                flash(f"‘{existing.name}’ already exists; edit cancelled.", 'danger')
                return redirect(url_for('systems.edit_system', system_id=system.id))
            system.name = new_name
        system.description = request.form.get('description')
        system.owner       = request.form.get('owner')
        system.notes       = request.form.get('notes')
        db.session.commit()
        flash('System updated.', 'success')
        return redirect(url_for('systems.system_detail', system_id=system.id))
    return render_template('edit_system.html', system=system)

@bp.route('/<int:system_id>/delete', methods=['POST'])
def delete_system(system_id):
    system = System.query.get_or_404(system_id)
    # first delete any mappings tied to this system
    SystemMapping.query.filter_by(system_id=system.id).delete()
    db.session.delete(system)
    db.session.commit()
    flash(f"Deleted system '{system.name}'.", 'success')
    return redirect(url_for('systems.list_systems'))
