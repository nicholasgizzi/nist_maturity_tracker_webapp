from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Risk
from flask_login import login_required, current_user
from datetime import datetime

bp = Blueprint('risks', __name__, url_prefix='/risks')

@bp.route('')
@login_required
def list_risks():
    all_risks = Risk.query.order_by(Risk.priority.desc()).all()
    return render_template('risk_register.html', risks=all_risks)

@bp.route('/add', methods=['GET','POST'])
@login_required
def add_risk():
    if request.method == 'POST':
        # grab form fields
        desc = request.form['description']
        sev  = int(request.form['severity'])
        lik  = int(request.form['likelihood'])
        det  = request.form.get('details', '').strip()  # capture details
        # calculate priority (e.g. sev * lik)
        prio = sev * lik
        # auto-generate code, e.g. R001, R002, ...
        next_id = Risk.query.count() + 1
        code = f"R{next_id:03d}"
        new = Risk(
          code=code,
          description=desc,
          severity=sev,
          likelihood=lik,
          priority=prio,
          details=det,   # include details
          owner=current_user.username,
          created_at=datetime.utcnow()
        )
        db.session.add(new)
        db.session.commit()
        flash('Risk registered', 'success')
        return redirect(url_for('risks.list_risks'))
    # GET
    # we need the next code to prefill
    next_id = Risk.query.count() + 1
    return render_template(
      'add_risk.html',
      next_code=f"R{next_id:03d}"
    )

@bp.route('/<int:risk_id>')
@login_required
def view_risk(risk_id):
    """Show details for a single risk."""
    risk = Risk.query.get_or_404(risk_id)
    return render_template('risk_detail.html', risk=risk)