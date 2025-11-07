from app.db.database import db

class CV:
    def __init__(self, firstname="", lastname="", email="", phone="", education=None, experience=None, skills=None, languages=None, projects=None):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.education = education or []
        self.experience = experience or []
        self.skills = skills or []
        self.languages = languages or []
        self.projects = projects or []

class Profile:
    def __init__(self, tg_id, fullname="", email="", cv=None):
        self.tg_id = tg_id
        self.fullname = fullname
        self.email = email
        self.cv = cv or CV()

    def save(self):
        db.profiles.update_one(
            {"tg_id": self.tg_id},
            {
                "$set": {
                    "fullname": self.fullname,
                    "email": self.email,
                    "cv": {
                        "firstname": self.cv.firstname,
                        "lastname": self.cv.lastname,
                        "email": self.cv.email,
                        "phone": self.cv.phone,
                        "education": self.cv.education,
                        "experience": self.cv.experience,
                        "skills": self.cv.skills,
                        "languages": self.cv.languages,
                        "projects": self.cv.projects,
                    },
                }
            },
            upsert=True,
        )
    @staticmethod
    def save_template(tg_id, template):
        db.profiles.update_one(
            {"tg_id": tg_id},
            {"$set": {"template": template}},
            upsert=True
        )
