from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import asyncio

from app.states.interview import Interview

router = Router()

QUESTIONS = [
    "Що таке ООП?",
    "Назви принципи SOLID",
    "Що таке інкапсуляція?",
    "Чим відрізняється TCP від UDP?",
    "Що таке база даних?"
]


@router.message(F.text == "/interview")
async def start_interview(message: Message, state: FSMContext):
    await state.update_data(answers=[], index=0)
    await message.answer("Починаємо інтерв'ю!")
    await ask_next(message, state)


async def ask_next(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("index", 0)

    if index >= len(QUESTIONS):
        await finish_interview(message, state)
        return

    question = QUESTIONS[index]
    await state.update_data(current_question=question, timer_active=True)
    await state.set_state(Interview.asking)

    await message.answer(f"{question}\nУ тебе є 60 секунд на відповідь")

    async def timer():
        await asyncio.sleep(60)
        data = await state.get_data()
        
        if data.get("timer_active"):
            answers = data["answers"]
            answers.append("(не відповів)")
            await state.update_data(answers=answers, index=data["index"] + 1, timer_active=False)
            await ask_next(message, state)

    asyncio.create_task(timer())


@router.message(Interview.asking)
async def save_answer(message: Message, state: FSMContext):
    data = await state.get_data()

    if not data.get("timer_active"):
        return

    await state.update_data(timer_active=False)

    answers = data["answers"]
    answers.append(message.text)

    await state.update_data(answers=answers, index=data["index"] + 1)

    await ask_next(message, state)


async def finish_interview(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data["answers"]

    valid = sum(1 for a in answers if a != "(не відповів)")
    total = len(QUESTIONS)

    score = valid * 2

    checklist = [
        "Відповів хоча б на 1 питання" if valid > 0 else "Не відповів на жодне питання",
        f"Відповів на {valid} із {total}" if valid >= total // 2 else f"Лише {valid} із {total}",
        "Не здавайся" if valid > 2 else "Потрібно більше практики"
    ]

    checklist_text = "\n".join(checklist)

    await message.answer(
        f"Інтерв'ю завершено!\n"
        f"Твій бал: {score}/{total * 2}\n\n"
        f"Чек-лист:\n{checklist_text}"
    )

    await state.clear()