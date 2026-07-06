import argparse
import sys
import time
from pathlib import Path

import pandas as pd
from ollama import Client

from config_read import load_config

def generate_architecture(
    task_content,
    model,
    client,
    temperature = 0.25,
    num_ctx = 32768,
):
    system_prompt = Path('SYS_PRPT_ARCHITECTURE.md').read_text()
    user_prompt = f"""
    TASK.md content:
    \n{task_content}\n
    Generate the complete ARCHITECTURE.md now following all instructions above. Remember: start directly with `# MindVault Architecture` and output pure Markdown only."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
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

    start = time.perf_counter()

    config = load_config('model.config')
    task_content = (dir / Path('TASK.md')).read_text()
    architecture_data = generate_architecture(
        task_content=task_content,
        model=config['OLLAMA_MODEL'],
        temperature=config['TEMPERATURE'],
        num_ctx=config['NUM_CTX'],
        client=Client()
    )

    end = time.perf_counter()
    if end - start > 60:
        print(f"Запрос выполнен за {int((end - start) // 60)} минут {int((end - start) % 60)} секунд")
    else:
        print(f"Запрос выполнен за {int(end - start)} секунд")

    csv_data = architecture_data.split('```csv')[-1]
    if csv_data.endswith('```'):
        csv_data = csv_data[:-3]
    if csv_data.startswith('\n'):
        csv_data = csv_data[1:]
    architecture_md = '\n'.join('```csv'.join(architecture_data.split('```csv')[:-1]).split('\n')[:-2])

    (args.dir / Path('FILE_STRUCTURE.csv')).write_text(csv_data)
    (args.dir / Path('ARCHITECTURE.md')).write_text(architecture_md)


def state_check_request(dir : Path):
    """
    По ARCHITECTURE.md и FILE_STRUCTURE.csv проверяет нынешнее состояние проекта
    исходя из чего предлагает последующие действия
    """

    files_df = pd.read_csv(dir / Path('FILE_STRUCTURE.csv'))
    if files_df['finished'].astype(bool).all():
        #TODO Сделать проверку всех файлов проекта, так как что-то не работает
        pass
    else:
        unfinished_files_df = pd.DataFrame(columns=files_df.columns)
        for _, row in files_df.iterrows():
            if Path(row['path']).exists():
                if not bool(row['finished']):
                    unfinished_files_df.loc[len(unfinished_files_df)] = row
        #TODO Сделать проверку тех файлов, которые не доработаны
        #TODO Сделать проверку файлов, которые существуют
        #TODO Сделать создание тестов по файлам, которые существуют или которые будут


    print(unfinished_files_df)

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
        help="Указывает, нужно ли проверить готовые файлы, или проверить не готовые"
    )
    args = parser.parse_args()
    if args.mode == 'A':
        architecture_request(args.dir)
    else:
        state_check_request(args.dir)