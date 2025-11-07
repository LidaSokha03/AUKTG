class Profile:
    def __init__(self, user_id: int, tg_username: str, fullname: str, email: str, portfolio: str, education: list, skills: list, languages: list):
        self.user_id = user_id
        self.tg_username = tg_username
        self.fullname = fullname
        self.email = email
        self.cv = None
        self.portfolio = portfolio
