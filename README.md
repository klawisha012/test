# Шаблон: GitHub Issues + агенты для команды

## Запуск заметок

Нужен Python 3.10+. Внешние зависимости не требуются.

```powershell
python server/notes.py
```

Откройте `http://localhost:8000`: форма, список и удаление работают с реальным
API на том же сервере. Пробельный текст не отправляется. Если заметка уже удалена
в другой вкладке, повторное удаление корректно убирает её из текущего списка.
Заметки сохраняются при перезагрузке страницы, но текущий сервер хранит их
в памяти: остановка процесса очищает список.

Для проверки интерфейса на моках откройте `http://localhost:8000/?mock=1`.
Выбор адаптера находится в `web/app.js`, контракт адаптеров — в `web/notes-api.js`.
Моки хранят данные только до перезагрузки страницы.

Проверки:

```powershell
python -m unittest discover -s tests
node --test tests/notes-api.test.mjs
```

Для второй команды нужен Node.js 22.7+.

Шаблон репозитория для команды, в которой каждый пишет код со своим агентом (Codex, Cursor или Claude Code), а работа приходит из GitHub Issues. Внутри — скиллы Matt Pocock и GitHub Actions, которые сами назначают тикетам владельцев.

## Как устроено

`/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement` → `/code-review`

Спека делится на срезы (поведение, которое можно показать целиком), а каждый срез — на тикеты, по одному на роль. GitHub Actions назначает тикет участнику с нужной ролью и наименьшей нагрузкой. Когда закрыты все тикеты среза, срез и спека закрываются сами. Термины — в [GLOSSARY.md](GLOSSARY.md).

## Быстрый старт

1. Нажмите **Use this template** и создайте репозиторий.
2. Установите Python 3 и [GitHub CLI](https://cli.github.com/), выполните `gh auth login`.
3. Скопируйте `.agents/team.example.json` в `.agents/team.json` и впишите свой репозиторий, роли и участников:

   ```json
   {
     "repository": "my-org/my-app",
     "roles": {"frontend": "Интерфейс", "backend": "API и база данных"},
     "members": [{"login": "alice", "roles": ["frontend"]}, {"login": "bob", "roles": ["backend", "frontend"]}]
   }
   ```

4. Закоммитьте `.agents/team.json` в основную ветку и включите GitHub Actions.
5. Откройте репозиторий в агенте и выполните `/setup-matt-pocock-skills`. Если агент предлагает глобальный скилл с тем же именем, выберите проектный: только он знает о ролях.

## Дальше

- [docs/guide.md](docs/guide.md) — работа в команде, перенос шаблона в существующий репозиторий, обновление скиллов.
- [.agents/workflow/distribution.md](.agents/workflow/distribution.md) — точные правила распределения (англ.).

Скиллы взяты из [mattpocock/skills](https://github.com/mattpocock/skills), лицензия MIT: [LICENSE-mattpocock.txt](LICENSE-mattpocock.txt).
