from pathlib import Path
from typing import List, Dict
import shutil
import logging
import textwrap

site_root = Path("..")
articles_dir = Path("../../my-articles")
posts_dir = site_root / "_posts"
assets_images_dir = site_root / "assets" / "images"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

assert articles_dir.exists()
assert posts_dir.exists()


#%%
def make_articles_list(articles_dir: Path) -> List[Path]:
    possible_dirs = [d for d in articles_dir.iterdir() if d.is_dir() and d.name != ".git"]

    articles = []
    for d in possible_dirs:
        for d2 in [d] + [dd for dd in d.iterdir() if dd.is_dir()]:
            for f in d2.iterdir():
                if f.is_file() and f.name.endswith(".md"):
                    articles.append(f)
    return articles


articles_lst = make_articles_list(articles_dir)


#%%
def process_article(article_path: Path, date: str, dry_run: bool = False):
    log.debug(f"start processing {article_path}")

    images_dir = article_path.parent / 'imgs'
    article_path_new = posts_dir / f"{date}-{article_path.name.replace(' ', '-')}"

    images_names_list = []
    if images_dir.exists():
        images_names_list = [img.name for img in images_dir.iterdir()]
        relative_images_dir = (images_dir.parent.resolve()).relative_to(articles_dir.resolve())
        new_images_dir = assets_images_dir / relative_images_dir

        log.debug(f"copy images to {new_images_dir}, images = [{', '.join(images_names_list)}]")
        if not dry_run:
            shutil.copytree(images_dir, new_images_dir, dirs_exist_ok=True)

    article_text = article_path.read_text()
    for image in images_names_list:
        text = f"](imgs/{image})"
        new_text = f"](/{new_images_dir.relative_to(site_root)}/{image})"
        log.debug(f"replace '{text}' with '{new_text}'")
        article_text = article_text.replace(text, new_text)

    languages = {line for line in article_text.split('\n') if line.startswith('```') and len(line) > 3}
    for language in languages:
        log.debug(f"replace '{language} with {language.lower()}")
        article_text = article_text.replace(language + '\n', language.lower() + '\n')

    frontmatter = textwrap.dedent(f"""\
        ---
        title: "{article_path.name[:-3]}"
        author: kright
        ---
        """)

    if not article_text.startswith('---'):
        article_text = frontmatter + article_text

    if not dry_run:
        shutil.copy(article_path, article_path_new)
    log.debug(f"copy article {article_path} -> {article_path_new}")

    log.debug(f"write new text to {article_path_new}")
    if not dry_run:
        article_path_new.write_text(article_text)


#%%

date_by_name = {
    "Пишем простую* игровую физику самолёта.md": "2023-09-07",
    "Как можно взять  tensorflow и смешать две картинки в одну.md": "2021-11-25",
    'Шпаргалка по Gradle.md': "2019-06-28",
    'Субъективное видение идеального языка программирования.md': "2019-01-07",
    'telegram bot для персонализированной подборки статей с хабра.md': "2019-11-11",
    'Ностальгии пост: j2me, Gravity Defied, 64kb.md': "2020-05-31",
    'Заметки про увеличение картинок нейронными сетями.md': "2023-05-18",
    'Scala: parser combinators на примере парсера формул.md': "2017-04-03",
    'Learn OpenGL. Урок 5.9 Отложенный рендеринг.md': "2018-08-19",
    'Learn OpenGL. Урок 5.3 карты теней.md': "2018-04-20",
    'Learn Open GL. Урок 5.7 - HDR.md': "2018-08-16",
    'scala 3: transparent inline with Dynamic.md': "2022-01-01",
    'Inut lag в мониторе.md': "2022-01-01",
    'Впечатления от Forza Horizon 4 на руле.md': "2022-01-01",
    'моё домашнее сетевое хранилище из raspberry pi 4b.md': "2022-01-01",
    'Физика вращения 3д тел.md': "2022-11-05",
}

for article in articles_lst:
    process_article(article_path=article, date=date_by_name[article.name], dry_run=False)
#%%