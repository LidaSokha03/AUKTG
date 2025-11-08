class CV:
    # def init(self, user_id: int, firstname: str, lastname: str, email: str, phone: str, education: str, experience: int, skills: list, languages: list, projects: str):
    def __init__(self, user_id: str, firstname: str, lastname: str, email: str, phone: str, education: str, experience: str, skills: str, courses: str, version: int = 1):
        self.user_id = user_id #auto_generated
        self.version = version #1
        self.firstname = firstname #Lida
        self.lastname = lastname #Sokha
        self.email = email #lidasosokha@gmail.com
        self.phone = phone #0964692379 or +380964692379
        self.experience = experience #projects etc
        self.education = education #Bachelor's Degree in BA, UCU
        self.courses = courses #text for start but after this list of languages ['language1, level', 'language2, level']
        self.skills = skills #for the start only in text but after this list of skills ['skill1', 'skill2']
        
