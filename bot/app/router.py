from aiogram import Router

# імпортуємо всі твої handlers
from bot.app.handlers import start, dashboard, profile, cv_template, language

router = Router()

# підключаємо їх в правильному порядку
router.include_router(start.router)
router.include_router(dashboard.router)
router.include_router(profile.router)
router.include_router(cv_template.router)
router.include_router(language.router)
