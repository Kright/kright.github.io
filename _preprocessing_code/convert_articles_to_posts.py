from pathlib import Path
from typing import List, Dict
import shutil
import logging
import textwrap
import csv
from datetime import datetime
from slugify import slugify
import re
import urllib.parse

site_root = Path(".")
articles_dir = site_root / "../my-articles"
posts_dir = site_root / "_posts"
assets_images_dir = site_root / "assets" / "images"
dates_file = site_root / "_preprocessing_code" / "dates.csv"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

assert articles_dir.exists()
assert posts_dir.exists()
assert dates_file.exists()


# %%
def make_articles_list(articles_dir: Path) -> List[Path]:
    possible_dirs = [d for d in articles_dir.iterdir() if d.is_dir() and d.name != ".git"]

    articles = []
    for d in possible_dirs:
        for d2 in [d] + [dd for dd in d.iterdir() if dd.is_dir()]:
            for f in d2.iterdir():
                if f.is_file() and (f.name.endswith(".md") or f.name.endswith(".html")):
                    articles.append(f)
    return articles

def generate_old_jekyll_url(name_without_ext, date):
    match = re.match(r'^(\d{4})-(\d{2})-(\d{2})', date)
    if not match:
        return None # Если файл не соответствует формату статьи Jekyll
        
    year, month, day = match.groups()
    
    # 3. Эмулируем поведение Jekyll slugify:
    # Заменяем всё, что не является буквой, цифрой или дефисом, на дефис
    # \w включает буквы (в т.ч. кириллицу), цифры и подчеркивание
    slug = re.sub(r'[^\w\-]+', '-', name_without_ext)
    
    # Схлопываем несколько дефисов подряд в один
    slug = re.sub(r'-+', '-', slug)
    
    # Убираем дефисы по краям (если вдруг спецсимволы были в начале/конце)
    slug = slug.strip('-')
    
    # 4. Собираем старый URL
    # jekyll-redirect-from отлично понимает читаемую кириллицу, поэтому можно
    # возвращать ссылку прямо так, без превращения в страшные %D0%BD:
    url = f"/{year}/{month}/{day}/{slug}.html"
    
    # Но если вы хотите прямо "ту самую" закодированную ссылку, раскомментируйте это:
    encoded_slug = urllib.parse.quote(slug)
    url = f"/{year}/{month}/{day}/{encoded_slug}.html"
    
    return url



articles_lst = make_articles_list(articles_dir)


# %%
def process_article(article_path: Path, date: str, dry_run: bool = False):
    log.debug(f"")
    log.debug(f"start processing {article_path}")

    images_dir = article_path.parent / 'imgs'
    if not images_dir.exists():
        images_dir = article_path.parent / 'img'

    article_path_new = posts_dir / f"{date}-{article_path.name.replace(' ', '-')}"
    article_text = article_path.read_text()

    if article_path.suffix == ".md":
        images_names_list = []
        if images_dir.exists():
            images_names_list = [img.name for img in images_dir.iterdir()]
            relative_images_dir = (images_dir.parent.resolve()).relative_to(articles_dir.resolve())
            new_images_dir = assets_images_dir / relative_images_dir

            log.debug(f"copy images to {new_images_dir}, images = [{', '.join(images_names_list)}]")
            if not dry_run:
                shutil.copytree(images_dir, new_images_dir, dirs_exist_ok=True)

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

    permalink = f"/{date.replace('-', '/')}/{slugify(article_path.stem)}/"
    redirect_from = generate_old_jekyll_url(article_path.stem, date)

    frontmatter = textwrap.dedent(f"""\
        ---
        title: "{article_path.name[:-3].capitalize()}"
        author: kright
        permalink: {permalink}
        redirect_from:
          - {redirect_from}
        ---
        """)

    if not article_text.startswith('---'):
        article_text = frontmatter + article_text
    
    if "\npermalink: " not in article_text:
        article_text = f"---\n" + f"permalink: {permalink}\n" + article_text[4:]
        
    if "\nredirect_from:" not in article_text:
        article_text = textwrap.dedent(f"""\
            ---
            redirect_from:
              - {redirect_from}
            """) + article_text[4:]

    if not dry_run:
        shutil.copy(article_path, article_path_new)
    log.debug(f"copy article {article_path} -> {article_path_new}")

    log.debug(f"write new text to {article_path_new}")
    if not dry_run:
        article_path_new.write_text(article_text)


# %%

def load_dates() -> Dict[str, str]:
    with open(dates_file) as csvfile:
        reader = csv.reader(csvfile)
        return {
            name: date for name, date in reader
        }


def get_missed_articles(articles_lst: List[Path], date_by_name: Dict[str, str]) -> List[Path]:
    return [article for article in articles_lst if article.name not in date_by_name]


def append_dates(missed_articles: List[Path]) -> Dict[str, str]:
    current_date: str = datetime.today().strftime('%Y-%m-%d')
    with open(dates_file, 'a') as csvfile:
        writer = csv.writer(csvfile)
        for article in missed_articles:
            writer.writerow([article.name, current_date])
    return load_dates()


date_by_name = append_dates(missed_articles=get_missed_articles(articles_lst, load_dates()))

for article in articles_lst:
    process_article(article_path=article, date=date_by_name[article.name], dry_run=False)

# %%
