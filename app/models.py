from . import db
import enum
from datetime import datetime
from sqlalchemy.orm import validates

class PriorityLevel(enum.Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    subcategories = db.relationship('Subcategory', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.code}>"

class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Enum(PriorityLevel), default=PriorityLevel.MEDIUM)

    system_mappings = db.relationship('SystemMapping', backref='subcategory', lazy=True)

    @validates('priority')
    def validate_priority(self, key, value):
        if isinstance(value, str):
            try:
                value = PriorityLevel[value.upper()]
            except KeyError:
                raise ValueError("Invalid priority level. Must be LOW, MEDIUM, or HIGH.")
        return value

    def __repr__(self):
        return f"<Subcategory {self.code}>"

class System(db.Model):
    __tablename__ = 'systems'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    owner = db.Column(db.String(100))
    notes = db.Column(db.Text)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    mappings = db.relationship('SystemMapping', backref='system', lazy=True)

    def __repr__(self):
        return f"<System {self.name}>"

class SystemMapping(db.Model):
    __tablename__ = 'system_mappings'
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    last_reviewed = db.Column(db.DateTime, default=datetime.utcnow)
    reviewer = db.Column(db.String(100))
    notes = db.Column(db.Text)

    reviews = db.relationship('Review', backref='mapping', lazy=True)

    @validates('score')
    def validate_score(self, key, value):
        if value not in [0, 1, 2, 3, 4, 5]:
            raise ValueError("Score must be between 0 and 5")
        return value

    def __repr__(self):
        return f"<SystemMapping System={self.system_id} Subcategory={self.subcategory_id}>"

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    mapping_id = db.Column(db.Integer, db.ForeignKey('system_mappings.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    reviewer = db.Column(db.String(100))
    review_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    @validates('score')
    def validate_score(self, key, value):
        if value not in [0, 1, 2, 3, 4, 5]:
            raise ValueError("Score must be between 0 and 5")
        return value

    def __repr__(self):
        return f"<Review {self.id} for Mapping={self.mapping_id}>"