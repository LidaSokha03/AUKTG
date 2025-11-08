from app.db.models.cv import CV
from app.db.database import db

class Profile:
    def __init__(self, user_id: int, fullname: str = "", email: str = ""):
        self.tg_id = user_id
        self.fullname = fullname
        self.email = email
        self.cv = CV(user_id, "", "", "", "", "", 0, [], [], "", 1)

    def save(self):
        profile_doc = db.profiles.find_one({"tg_id": self.tg_id})

        last_version = 0
        if profile_doc:
            history = profile_doc.get("cv_history", [])
            if history:
                last_version = history[-1].get("version", 0)
            else:
                cv_doc = profile_doc.get("cv", {})
                last_version = cv_doc.get("version", 0)

        next_version = last_version + 1
        self.cv.version = next_version

        cv_data = {
            "version": self.cv.version,
            "firstname": self.cv.firstname,
            "lastname": self.cv.lastname,
            "email": self.cv.email,
            "phone": self.cv.phone,
            "education": self.cv.education,
            "experience": self.cv.experience,
            "skills": self.cv.skills,
            "languages": self.cv.languages,
            "projects": self.cv.projects,
        }

        db.profiles.update_one(
            {"tg_id": self.tg_id},
            {
                "$set": {
                    "fullname": self.fullname,
                    "email": self.email,
                    "cv": cv_data,
                },
                "$push": {
                    "cv_history": cv_data,
                },
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

    def load(self):
        profile = db.profiles.find_one({"tg_id": self.tg_id})
        if profile:
            self.fullname = profile.get("fullname", "")
            self.email = profile.get("email", "")
            cv_data = profile.get("cv", {})
            self.cv = CV(
                self.tg_id,
                cv_data.get("firstname", ""),
                cv_data.get("lastname", ""),
                cv_data.get("email", ""),
                cv_data.get("phone", ""),
                cv_data.get("education", ""),
                cv_data.get("experience", 0),
                cv_data.get("skills", []),
                cv_data.get("languages", []),
                cv_data.get("projects", ""),
                cv_data.get("version", 1),
            )
        return profile

    def exists(self):
        profile = db.profiles.find_one({"tg_id": self.tg_id})
        return profile is not None

    @staticmethod
    def get_by_tg_id(tg_id: int):
        profile_data = db.profiles.find_one({"tg_id": tg_id})
        if profile_data:
            profile = Profile(
                profile_data["tg_id"],
                profile_data.get("fullname", ""),
                profile_data.get("email", ""),)
            cv_data = profile_data.get("cv", {})

            profile.cv = CV(
                profile.tg_id,
                cv_data.get("firstname", ""),
                cv_data.get("lastname", ""),
                cv_data.get("email", ""),
                cv_data.get("phone", ""),
                cv_data.get("education", ""),
                cv_data.get("experience", 0),
                cv_data.get("skills", []),
                cv_data.get("languages", []),
                cv_data.get("projects", ""),
                cv_data.get("version", 1),
            )
            return profile
        return None
