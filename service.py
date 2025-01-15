from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import quiz_data
import json


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()





async def get_question(message, user_id):
    
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    print(current_question_index)

    correct_index = await get_correct_index(current_question_index)
    opts_json = await get_options(current_question_index)
    opts = json.loads(opts_json)
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{await get_question_text(current_question_index)}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)

async def get_question_text(question_index):
    get_question_text = f"""
        DECLARE $question_index AS Uint64;

        SELECT question_text
        FROM `quiz_questions`
        WHERE question_id == $question_index;
    """
    results = execute_select_query(pool, get_question_text, question_index=question_index)

    if len(results) == 0:
        return 0
    if results[0]["question_text"] is None:
        return 0
    return results[0]["question_text"] 

async def get_options(question_index):
    get_options = f"""
        DECLARE $question_index AS Uint64;

        SELECT options
        FROM `quiz_questions`
        WHERE question_id == $question_index;
    """
    results = execute_select_query(pool, get_options, question_index=question_index)

    if len(results) == 0:
        return 0
    if results[0]["options"] is None:
        return 0
    return results[0]["options"]  

async def get_correct_index(question_index):
    get_correct_index = f"""
        DECLARE $question_index AS Uint64;

        SELECT correct_option
        FROM `quiz_questions`
        WHERE question_id == $question_index;
    """
    results = execute_select_query(pool, get_correct_index, question_index=question_index)

    if len(results) == 0:
        return 0
    if results[0]["correct_option"] is None:
        return 0
    return results[0]["correct_option"]  

async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]    

    
    

async def update_quiz_index(user_id, question_index):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`)
        VALUES ($user_id, $question_index);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
    )

async def increment_user_score(user_id):
    update_quiz_state = f"""
        DECLARE $user_id AS Uint64;

        UPDATE quiz_state
        SET user_score_counter = user_score_counter + 1
        WHERE user_id = $user_id;
    """

    execute_update_query(
        pool,
        update_quiz_state,
        user_id=user_id,
    )

async def remove_user_score(user_id):
    update_quiz_state = f"""
        DECLARE $user_id AS Uint64;

        UPDATE quiz_state
        SET user_score_counter = 0
        WHERE user_id = $user_id;
    """

    execute_update_query(
        pool,
        update_quiz_state,
        user_id=user_id,
    )
    
