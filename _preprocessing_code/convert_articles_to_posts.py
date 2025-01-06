from pathlib import Path
from typing import List, Dict
import shutil
import logging
import textwrap
import csv
from datetime import datetime

site_root = Path("..")
articles_dir = Path("../../my-articles")
posts_dir = site_root / "_posts"
assets_images_dir = site_root / "assets" / "images"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

assert articles_dir.exists()
assert posts_dir.exists()


# %%
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


# %%
def process_article(article_path: Path, date: str, dry_run: bool = False):
    log.debug(f"start processing {article_path}")

    images_dir = article_path.parent / 'imgs'
    if not images_dir.exists():
        images_dir = article_path.parent / 'img'

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
        for prefix in ["imgs", "img"]:
            text = f"]({prefix}/{image})"
            new_text = f"](/{new_images_dir.relative_to(site_root)}/{image})"
            log.debug(f"replace '{text}' with '{new_text}'")
            article_text = article_text.replace(text, new_text)

            text = f"""src=("{prefix}/{image}")"""
            new_text = f"""src=("/{new_images_dir.relative_to(site_root)}/{image}")"""
            log.debug(f"replace '{text}' with '{new_text}'")
            article_text = article_text.replace(text, new_text)

    languages = {line for line in article_text.split('\n') if line.startswith('```') and len(line) > 3}
    for language in languages:
        log.debug(f"replace '{language} with {language.lower()}")
        article_text = article_text.replace(language + '\n', language.lower() + '\n')

    frontmatter = textwrap.dedent(f"""\
        ---
        title: "{article_path.name[:-3].capitalize()}"
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


# %%

def load_dates() -> Dict[str, str]:
    with open('dates.csv') as csvfile:
        reader = csv.reader(csvfile)
        return {
            name: date for name, date in reader
        }


def get_missed_articles(articles_lst: List[Path], date_by_name: Dict[str, str]) -> List[Path]:
    return [article for article in articles_lst if article.name not in date_by_name]


def append_dates(missed_articles: List[Path]) -> Dict[str, str]:
    current_date: str = datetime.today().strftime('%Y-%m-%d')
    with open('dates.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        for article in missed_articles:
            writer.writerow([article.name, current_date])
    return load_dates()


date_by_name = append_dates(missed_articles=get_missed_articles(articles_lst, load_dates()))

for article in articles_lst:
    process_article(article_path=article, date=date_by_name[article.name], dry_run=False)

# %%
