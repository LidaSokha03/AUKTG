class CV:
    # def init(self, user_id: int, firstname: str, lastname: str, email: str, phone: str, education: str, experience: int, skills: list, languages: list, projects: str):
    def init(self, user_id: str, firstname: str, lastname: str, email: str, phone: str, education: str, experience: str, skills: str, languages: str, projects: str):
        self.user_id = user_id #auto_generated
        self.firstname = firstname #Lida
        self.lastname = lastname #Sokha
        self.email = email #lidasosokha@gmail.com
        self.phone = phone #0964692379 or +380964692379
        self.education = education #Bachelor's Degree in BA, UCU
        self.experience = experience # 8 (int in years)
        self.skills = skills #for the start only in text but after this list of skills ['skill1', 'skill2']
        self.languages = languages #text for start but after this list of languages ['language1, level', 'language2, level']
        self.projects = projects #text