# seed.py
from app import create_app, db
from app.models import Category, Subcategory

DATA = [
    {
        "code": "GV", "name": "Govern", "subs": [
            ("GV.OC", "Organizational Context"),
            ("GV.RM", "Risk Management Strategy"),
            ("GV.RR", "Roles, Responsibilities, and Authorities"),
            ("GV.PO", "Policy"),
            ("GV.OV", "Oversight"),
            ("GV.SC", "Cybersecurity Supply Chain Risk Management"),
        ]
    },
    {
        "code": "ID", "name": "Identify", "subs": [
            ("ID.AM", "Asset Management"),
            ("ID.RA", "Risk Assessment"),
            ("ID.IM", "Improvement"),
        ]
    },
    {
        "code": "PR", "name": "Protect", "subs": [
            ("PR.AA", "Identity Management, Authentication, and Access Control"),
            ("PR.AT", "Awareness and Training"),
            ("PR.DS", "Data Security"),
            ("PR.PS", "Platform Security"),
            ("PR.IR", "Technology Infrastructure Resilience"),
        ]
    },
    {
        "code": "DE", "name": "Detect", "subs": [
            ("DE.CM", "Continuous Monitoring"),
            ("DE.AE", "Adverse Event Analysis"),
        ]
    },
    {
        "code": "RS", "name": "Respond", "subs": [
            ("RS.MA", "Incident Management"),
            ("RS.AN", "Incident Analysis"),
            ("RS.CO", "Incident Response Reporting and Communication"),
            ("RS.MI", "Incident Mitigation"),
        ]
    },
    {
        "code": "RC", "name": "Recover", "subs": [
            ("RC.RP", "Incident Recovery Plan Execution"),
            ("RC.CO", "Incident Recovery Communication"),
        ]
    },
]

def run():
    app = create_app()
    with app.app_context():
        # 1) Clear existing
        Subcategory.query.delete()
        Category.query.delete()
        db.session.commit()

        # 2) Insert fresh
        for fn in DATA:
            cat = Category(code=fn["code"], name=fn["name"])
            db.session.add(cat)
            for sub_code, sub_name in fn["subs"]:
                sc = Subcategory(
                    code=sub_code,
                    name=sub_name,
                    category=cat
                )
                db.session.add(sc)
        db.session.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    run()