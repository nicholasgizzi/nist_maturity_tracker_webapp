# from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
# from app import db
# from app.models import System, SystemMapping, Subcategory, Category, PriorityLevel, Review
# from datetime import datetime, timedelta
# from collections import defaultdict
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy import func

# bp = Blueprint('main', __name__)

# @bp.route('/')
# def dashboard():
#     view = request.args.get('view', 'all').lower()
#     cutoff = datetime.utcnow() - timedelta(days=90)

#     subcategories = Subcategory.query.all()
#     subcat_map = {s.id: s for s in subcategories}

#     def get_priority_score(priority_filter):
#         score_by_function = defaultdict(list)
#         for s in subcategories:
#             # Apply priority filter only if not 'all'
#             if priority_filter != 'all':
#                 if s.priority is None or s.priority.value.lower() != priority_filter:
#                     continue
#             for m in s.system_mappings:
#                 # Group by full function name (uppercase)
#                 func_name = s.category.name.upper()
#                 score_by_function[func_name].append(m.score)
#         # Compute average for each function
#         return {
#             func: round(sum(scores)/len(scores), 2) if scores else None
#             for func, scores in score_by_function.items()
#         }

#     # Current avg
#     current_scores = get_priority_score(view)

#     # Previous avg: use Review history before cutoff (or original mapping if older)
#     previous_scores = defaultdict(list)
#     for s in subcategories:
#         if view != 'all':
#             if s.priority is None or s.priority.value.lower() != view:
#                 continue
#         for m in s.system_mappings:
#             # Get most recent Review before cutoff
#             old = (
#                 Review.query
#                 .filter(Review.mapping_id == m.id, Review.review_date < cutoff)
#                 .order_by(Review.review_date.desc())
#                 .first()
#             )
#             if old:
#                 score_to_use = old.score
#             elif m.last_reviewed and m.last_reviewed < cutoff:
#                 score_to_use = m.score
#             else:
#                 continue
#             func_name = s.category.name.upper()
#             previous_scores[func_name].append(score_to_use)
#     previous_avg = {
#         func: round(sum(scores) / len(scores), 2) if scores else 0
#         for func, scores in previous_scores.items()
#     }

#     change_scores = {
#         f: round((current_scores.get(f) or 0) - (previous_avg.get(f) or 0), 2)
#         for f in current_scores.keys()
#     }

#     return render_template(
#         'dashboard.html',
#         current_scores=current_scores,
#         change_scores=change_scores,
#         view=view
#     )

# @bp.route('/systems')
# def list_systems():
#     systems = System.query.all()
#     return render_template('index.html', systems=systems)

# @bp.route('/systems/<int:system_id>')
# def system_detail(system_id):
#     system = System.query.get_or_404(system_id)
#     return render_template('system_detail.html', system=system)

# @bp.route('/systems/add', methods=['GET', 'POST'])
# def add_system():
#     if request.method == 'POST':
#         name = request.form['name'].strip()
#         # Case-insensitive check for an existing system by name
#         existing = (System.query
#                     .filter(func.lower(System.name) == name.lower())
#                     .first())
#         if existing:
#             flash(f"A system named '{existing.name}' already exists. Redirecting to its page.", 'info')
#             return redirect(url_for('main.system_detail', system_id=existing.id))

#         description = request.form.get('description')
#         owner = request.form.get('owner')
#         notes = request.form.get('notes')

#         new_system = System(name=name, description=description, owner=owner, notes=notes)
#         db.session.add(new_system)
#         # Wrap commit to catch any remaining unique‐constraint failure
#         try:
#             db.session.commit()
#         except IntegrityError:
#             db.session.rollback()
#             # Fallback: find the existing record again
#             dup = (System.query
#                    .filter(func.lower(System.name) == name.lower())
#                    .first())
#             if dup:
#                 flash(f"'{name}' already exists, redirecting to its page.", 'info')
#                 return redirect(url_for('main.system_detail', system_id=dup.id))
#             flash("Failed to add system due to a database error.", 'danger')
#             return redirect(url_for('main.list_systems'))
#         return redirect(url_for('main.list_systems'))

#     return render_template('add_system.html')

# @bp.route('/systems/<int:system_id>/add_mapping', methods=['GET', 'POST'])
# def add_mapping(system_id):
#     system = System.query.get_or_404(system_id)
#     subcategories = Subcategory.query.all()

#     if request.method == 'POST':
#         subcategory_id = request.form['subcategory_id']
#         score = int(request.form['score'])
#         reviewer = request.form.get('reviewer')
#         notes = request.form.get('notes')

#         new_mapping = SystemMapping(
#             system_id=system.id,
#             subcategory_id=subcategory_id,
#             score=score,
#             reviewer=reviewer,
#             notes=notes,
#             last_reviewed=datetime.utcnow()
#         )

#         db.session.add(new_mapping)
#         db.session.commit()
#         return redirect(url_for('main.system_detail', system_id=system.id))

#     return render_template('add_mapping.html', system=system, subcategories=subcategories)

# @bp.route('/systems/<int:system_id>/mappings/<int:mapping_id>/edit', methods=['GET', 'POST'])
# def edit_mapping(system_id, mapping_id):
#     # Load the mapping and all subcategories for selection
#     mapping = SystemMapping.query.get_or_404(mapping_id)
#     subcategories = Subcategory.query.all()
#     if request.method == 'POST':
#         # Update mapping from form values
#         mapping.subcategory_id = int(request.form['subcategory_id'])
#         mapping.score = int(request.form['score'])
#         mapping.reviewer = request.form.get('reviewer')
#         mapping.notes = request.form.get('notes')
#         mapping.last_reviewed = datetime.utcnow()
#         db.session.commit()
#         flash('Mapping updated successfully.', 'success')
#         return redirect(url_for('main.system_detail', system_id=system_id))
#     # GET: render the edit form
#     return render_template('edit_mapping.html', mapping=mapping, subcategories=subcategories)

# @bp.route('/functions/<function>')
# def view_function(function):
#     code = function.upper()
#     category = Category.query.filter_by(code=code).first_or_404()
#     subcategories = Subcategory.query.filter_by(category_id=category.id).all()
#     subcat_ids = [s.id for s in subcategories]

#     mappings = SystemMapping.query.filter(
#         SystemMapping.subcategory_id.in_(subcat_ids)
#     ).all()

#     system_map = defaultdict(list)
#     for m in mappings:
#         system_map[m.system].append(m)

#     return render_template('function_detail.html',
#                            category=category,
#                            system_map=system_map)

# @bp.route('/priorities')
# def priorities_overview():
#     # Show all subcategories with their priorities
#     subcategories = Subcategory.query.order_by(Subcategory.category_id).all()
#     return render_template('priorities.html', subcategories=subcategories, view='all')

# @bp.route('/priorities/<level>')
# def priorities_filtered(level):
#     # Filter by level: high, medium, low
#     try:
#         p = PriorityLevel[level.upper()]
#     except KeyError:
#         abort(404)
#     subcategories = Subcategory.query.filter_by(priority=p).order_by(Subcategory.category_id).all()
#     return render_template('priorities.html', subcategories=subcategories, view=level)

# @bp.route('/priorities/update_all', methods=['POST'])
# def update_priorities_bulk():
#     # Iterate over all form fields named priority_<subcat_id>
#     for key, value in request.form.items():
#         if not key.startswith('priority_'):
#             continue
#         subcat_id = int(key.split('_',1)[1])
#         if not value:
#             # Skip undefined
#             continue
#         try:
#             p = PriorityLevel[value.upper()]
#         except KeyError:
#             continue
#         subcat = Subcategory.query.get(subcat_id)
#         if subcat:
#             subcat.priority = p
#     db.session.commit()
#     flash('Priorities updated successfully.', 'success')
#     return redirect(url_for('main.priorities_overview'))

# @bp.route('/systems/<int:system_id>/edit', methods=['GET', 'POST'])
# def edit_system(system_id):
#     # Fetch the system or 404 if not found
#     system = System.query.get_or_404(system_id)

#     if request.method == 'POST':
#         # Update fields from the form
#         system.name        = request.form['name']
#         system.description = request.form.get('description')
#         system.owner       = request.form.get('owner')
#         system.notes       = request.form.get('notes')

#         db.session.commit()
#         flash('System updated successfully.', 'success')
#         return redirect(url_for('main.system_detail', system_id=system.id))

#     # GET: render the edit form
#     return render_template('edit_system.html', system=system)


# # --- Deletion routes ---

# @bp.route('/systems/<int:system_id>/mappings/<int:mapping_id>/delete', methods=['POST'])
# def delete_mapping(system_id, mapping_id):
#     mapping = SystemMapping.query.get_or_404(mapping_id)
#     db.session.delete(mapping)
#     db.session.commit()
#     flash('Mapping deleted successfully.', 'success')
#     return redirect(url_for('main.system_detail', system_id=system_id))


# @bp.route('/systems/<int:system_id>/delete', methods=['POST'])
# def delete_system(system_id):
#     system = System.query.get_or_404(system_id)
#     # First delete all mappings and reviews (if cascade isn’t configured)
#     for m in list(system.mappings):
#         # delete associated reviews
#         for r in list(m.reviews):
#             db.session.delete(r)
#         db.session.delete(m)
#     db.session.delete(system)
#     db.session.commit()
#     flash('System and its mappings deleted successfully.', 'success')
#     return redirect(url_for('main.list_systems'))