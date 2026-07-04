import argparse
import sys
import time
from pathlib import Path

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


def architecture_request():
    parser = argparse.ArgumentParser(
        description="Создает ARCHITECTURE.md по TASK.md",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dir",
        type=Path,
        help="Путь до корня проекта с файлом TASK.md",
    )
    args = parser.parse_args()

    if not args.dir.exists():
        print(f"ERROR: Указанная папка не существует", file=sys.stderr)
        sys.exit(1)
    if not (args.dir / Path('TASK.md')).exists():
        print(f"ERROR: TASK.md нет в {args.dir.resolve()}", file=sys.stderr)
        sys.exit(1)

    start = time.perf_counter()

    config = load_config('model.config')
    task_content = (args.dir / Path('TASK.md')).read_text()
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
    architecture_md = '\n'.join('```csv'.join(architecture_data.split('```csv')[:-1]).split('\n')[:-2])

    (args.dir / Path('FILE_STRUCTURE.csv')).write_text(csv_data)
    (args.dir / Path('ARCHITECTURE.md')).write_text(architecture_md)


if __name__ == "__main__":
    architecture_request()