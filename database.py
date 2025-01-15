import os
import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)    

# Зададим настройки базы данных 
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)


# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Какой оператор используется для проверки равенства в Python?',
        'options': ['=', '==', '===', '!='],
        'correct_option': 1
    },
    {
        'question': 'Какая функция используется для печати на экран в Python?',
        'options': ['print', 'echo', 'display', 'write'],
        'correct_option': 0
    },
    {
        'question': 'Какой метод используется для добавления элемента в конец списка?',
        'options': ['add', 'append', 'insert', 'push'],
        'correct_option': 1
    },
    {
        'question': 'Какой тип данных используется для хранения последовательности символов?',
        'options': ['string', 'char', 'text', 'str'],
        'correct_option': 3
    },
    {
        'question': 'Какой цикл используется для итерации по элементам последовательности?',
        'options': ['for', 'while', 'do-while', 'foreach'],
        'correct_option': 0
    },
    {
        'question': 'Какая функция используется для получения длины списка?',
        'options': ['length', 'size', 'len', 'count'],
        'correct_option': 2
    },
    {
        'question': 'Какой метод используется для удаления элемента из списка по индексу?',
        'options': ['remove', 'delete', 'pop', 'clear'],
        'correct_option': 2
    },
    {
        'question': 'Какой оператор используется для комментариев в Python?',
        'options': ['//', '/* */', '#', '--'],
        'correct_option': 2
    }
    # Добавьте другие вопросы
]
