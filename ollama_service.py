import argparse
import sys
import time
from pathlib import Path

import pandas as pd
from ollama import Client

from config_read import load_config

def request_generate(
    system_prompt,
    user_prompt,
    model,
    client,
    temperature = 0.25,
    num_ctx = 32768,
):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        start = time.perf_counter()

        response = client.chat(
            model=model,
            messages=messages,
            options={
                "temperature": temperature,
                "num_ctx": num_ctx,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
            },
        )
        content = response["message"]["content"].strip()

        end = time.perf_counter()
        if end - start > 60:
            print(f"Запрос выполнен за {int((end - start) // 60)} минут {int((end - start) % 60)} секунд")
        else:
            print(f"Запрос выполнен за {int(end - start)} секунд")

        return content

    except Exception as e:
        print(f"\nОшибка при подключении к модели '{model}': {e}", file=sys.stderr)
        sys.exit(1)


def architecture_request(dir : Path):
    """
    Создает ARCHITECTURE.md по TASK.md в переданной директории
    """
    if not dir.exists():
        print(f"ERROR: Указанная папка не существует", file=sys.stderr)
        sys.exit(1)
    if not (dir / Path('TASK.md')).exists():
        print(f"ERROR: TASK.md нет в {dir.resolve()}", file=sys.stderr)
        sys.exit(1)

    config = load_config('model.config')
    task_content = (dir / Path('TASK.md')).read_text()
    architecture_data = request_generate(
        system_prompt=Path('SYS_PRPT_ARCHITECTURE.md').read_text(),
        task_content=Path('USR_PRPT_ARCHITECURE.md').read_text().format(task_content),
        model=config['OLLAMA_MODEL'],
        temperature=config['TEMPERATURE'],
        num_ctx=config['NUM_CTX'],
        client=Client()
    )

    csv_data = architecture_data.split('```csv')[-1]
    if csv_data.endswith('```'):
        csv_data = csv_data[:-3]
    if csv_data.startswith('\n'):
        csv_data = csv_data[1:]
    architecture_md = '\n'.join('```csv'.join(architecture_data.split('```csv')[:-1]).split('\n')[:-2])

    (args.dir / Path('FILE_STRUCTURE.csv')).write_text(csv_data)
    (args.dir / Path('ARCHITECTURE.md')).write_text(architecture_md)


def generate_state_check(
    task_content,
    model,
    client,
    temperature = 0.25,
    num_ctx = 32768,
)

def state_check_request(dir : Path, check_finished : bool, create_tests : bool):
    """
    По ARCHITECTURE.md и FILE_STRUCTURE.csv проверяет нынешнее состояние проекта
    исходя из чего предлагает последующие действия
    """

    files_df = pd.read_csv(dir / Path('FILE_STRUCTURE.csv'))
    if files_df['finished'].astype(bool).all():
        #TODO Сделать проверку всех файлов проекта, так как что-то не работает
        #TODO А также создание тестов при необходимости
        pass
    else:
        files_to_check_df = pd.DataFrame(columns=files_df.columns)
        for _, row in files_df.iterrows():
            if Path(row['path']).exists():
                if not (check_finished ^ bool(row['finished'])): #xnor
                        files_to_check_df.loc[len(files_to_check_df)] = row
        #TODO Сделать проверку тех файлов, которые не доработаны
        #TODO Сделать создание тестов по файлам, которые существуют или которые будут


    print(files_to_check_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        type=str,
        help="Режим проекта. A - создание архитектуры, C - проверка нынешнего состояния проекта"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        help="Путь до корня проекта",
    )
    parser.add_argument(
        "--check-finished",
        type=bool,
        help="Указывает, нужно ли проверить готовые файлы, или проверить не готовые",
        default=False
    )
    parser.add_argument(
        "--create-tests",
        type=bool,
        help="Указывает, нужно ли создавать тесты для файлов для проверки",
        default=False
    )
    args = parser.parse_args()
    if args.mode == 'A':
        architecture_request(args.dir)
    else:
        state_check_request(args.dir, args.check_finished, args.create_tests)