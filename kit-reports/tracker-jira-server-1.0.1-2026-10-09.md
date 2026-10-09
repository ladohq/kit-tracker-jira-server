# Отчёт о ките: tracker-jira-server 1.0.1

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-markdown`), путь задан
- Коммит: 16909d7 (`kit.yaml` `version: 1.0.1`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.0.0-2026-10-08.md`
  (артефакт `assessment`), база — 1240f8d (её называет план),
  `git diff 1240f8d -- kit.yaml README.md BLUEPRINT.md agents flows skills`: 5 файлов,
  137 строк добавлено, 43 удалено. Первый визит `evaluate`.
- Проходы: изменение небольшое (конвертер около 90 строк в `jira.py`, раздел SKILL.md,
  R12 в BLUEPRINT), три прохода я сделал сам, без субагентов, каждый по всем 12 критериям
  и известным дырам. Проход 1: `jira.py` (`to_wiki`, `_wiki`, `_inline`, `text_arg`,
  argparse) с запусками конвертера на 24 входах (вывод ниже, в находках). Проход 2:
  SKILL.md и README против поведения скрипта. Проход 3: BLUEPRINT R7, R12, разделы 3–5
  против файлов и плана. Затем полный проход по всем пяти файлам, которых касается дифф
  (Re-evaluation 5): новых находок он не дал. Однопроходных находок отброшено: 1 (строки
  продолжения пункта списка без отступа — поведение Jira здесь я подтвердить не могу);
  оставлено как подтверждённые: 0.
- Оговорка: вред в F5.1, F5.2, F5.3 и F5.5 — это то, как Jira Server 8.13 показывает
  получившуюся wiki-разметку. Вывод конвертера подтверждён запусками; поведение Jira я
  знаю, но здесь не проверял: его стоит проверить на тестовой Jira 8.13.19 (R10) до
  выпуска.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 5 находок (0 high, 2 medium, 3 low); 11 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста, с полным проходом по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 59, OK |
| Правило остановки | не выполнено: 0 high, 2 medium (F5.1, F5.2) — совет для гейта выпуска, не блок |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.0.1

| Measure | Where | Value | Green / yellow up to | Zone |
|---|---|---|---|---|
| Worker roles (not supervisor) | kit | 0 | 3 / 5 | green |
| Work steps in a flow | no flows | 0 | 5 / 8 | green |
| Gates in a flow | no flows | 0 | 2 / 3 | green |
| Words in a role prompt | no roles | 0 | 800 / 1500 | green |
| Words in the lead's prompt | no lead role | 0 | 1000 / 1500 | green |
| Own skills | kit | 1 | 5 / 10 | green |
| MCP servers | kit | 0 | 2 / 4 | green |

## Similar paragraphs (one rule, one place; 55% similar or more)

none

Overall: green
```

### Потоки

У кита нет потоков (R2), скелетов нет; сравнивать нечего. Скрипт потоков этого случая
по-прежнему не знает (см. «Found on the way»):

```
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. F5.1 — язык блока кода передаётся в `{code:…}` как есть; незнакомый Jira язык даёт
   ошибку над блоком.
2. F5.2 — нумерованный список, разорванный пустой строкой или блоком кода, в Jira
   начинается снова с 1.

## Находки

### 1. Границы ролей

Не применимо: ролей нет (R2). Право на запись в Jira не изменилось: SKILL.md:25 «only
when your role, your step or the human asks for it».

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

Не применимо: потоков нет. Сбой конвертера — не новый код выхода: `to_wiki` возвращает
исходный текст (`jira.py` `except Exception: return text`), так что таблица кодов
SKILL.md не меняется.

### 4. Независимая проверка

Не применимо: потоков нет. Конвертер покрыт тестами `MarkdownTest` (7 тестов) и тестами
через поддельную Jira (`--wiki`, `--field description=`); 59 тестов, OK.

### 5. Противоречия

SKILL.md обещает, что форматирование сохраняется («keeps headings, … fenced code blocks
(with their language), bullet and numbered lists»), а в двух местах вывод конвертера в
Jira выглядит иначе.

- **F5.1** [medium] `skills/tracker/jira.py:396`
  > `            out.append("{code:%s}" % match.group(2) if match.group(2) else "{code}")`
  Любое слово после ```` ``` ```` уходит в `{code:<слово>}`. В Jira Server 8.x у `{code}`
  фиксированный список языков (bash, c, c++, css, go, java, javascript, json, python,
  sh, sql, xml, yaml и ещё несколько). Для языка вне списка Jira показывает над блоком
  ошибку «Unable to find source-code formatter for language: …». Агенты часто пишут
  ```` ```text ````, ```` ```console ````, ```` ```diff ````, ```` ```typescript ````.
  Запуск: `to_wiki("```text\nhello\n```\n")` → `'{code:text}\nhello\n{code}\n'`;
  ```` ```console ```` → `{code:console}`, ```` ```diff ```` → `{code:diff}`.
  SKILL.md:68 «fenced code blocks (with their language)» обещает, что это работает.
  Fix: держать в `jira.py` короткий список языков, которые знает Jira 8.13 (и пару
  синонимов: `shell`/`zsh`/`console` → `bash`, `ts`/`typescript` → `javascript`), а
  остальные отправлять как `{code}` без языка; проверить список на тестовой Jira 8.13.19.
  Passes: 3/3

- **F5.2** [medium] `skills/tracker/jira.py:411`
  > `        if line.strip():`
  Пустая строка внутри списка проходит в вывод как есть, а блок кода внутри пункта
  закрывает список (`lists = []` у ограждения). В wiki-разметке Jira пустая строка или
  блок кода заканчивают список, поэтому следующий пункт `#` начинает новый список с 1.
  «Рыхлые» списки и шаги с командой внутри агенты пишут часто.
  Запуски: `to_wiki("1. one\n\n2. two\n")` → `'# one\n\n# two\n'` (в Jira «1. one»,
  «1. two»); `to_wiki("1. run:\n   ```bash\n   ls\n   ```\n2. done")` →
  `'# run:\n{code:bash}\n   ls\n{code}\n# done'`.
  Fix: убирать пустые строки между пунктами одного списка (пустая строка, после которой
  снова идёт пункт списка); про блок кода внутри пункта нумерованного списка сказать
  одной фразой в SKILL.md («a code block ends a numbered list in Jira») или отправлять
  такой блок как `{code}` без выхода из списка, если тестовая Jira это показывает.
  Passes: 3/3

- **F5.3** [low] `skills/tracker/jira.py:372`
  > `    text = CODE_SPAN.sub(lambda m: keep("{{%s}}" % m.group(2).strip()), text)`
  Внутри кода конвертер разметку не читает, но Jira читает её внутри `{{…}}`: `*`, `_`,
  `-` всё ещё работают, а `{` или `}` рядом со скобками ломают моноширинный текст.
  Запуск: ``to_wiki("run `**/*.py` and `{x}`")`` → `'run {{**/*.py}} and {{{x}}}'`.
  Fix: экранировать обратной косой чертой символы wiki (`*_-+^~{}[]|`) в содержимом
  `{{…}}`. Passes: 2/3

- **F5.4** [low] `skills/tracker/jira.py:357`
  > `LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")`
  Изображение Markdown попадает под шаблон ссылки, и от него остаётся `!`.
  Запуск: `to_wiki("![alt](http://x/y.png)")` → `'![alt|http://x/y.png]'`. А
  SKILL.md:69-70 говорит «Anything else / is sent as it is».
  Fix: `(?<!!)` перед `\[` в `LINK`, тогда изображение пройдёт как есть. Passes: 2/3

- **F5.5** [low] `skills/tracker/jira.py:417`
  > `            out.append(_inline(line))`
  Строки абзаца, перенесённые по ширине (в Markdown это один абзац), идут в Jira каждая
  отдельно, а Jira показывает каждый перевод строки как разрыв строки. Если агент
  переносит строки на 80–90 символах, текст в Jira выходит рваным.
  Запуск: `to_wiki("This is a long line\nthat continues here.")` → без изменений.
  Fix: в SKILL.md одна фраза — «write each paragraph on one line: Jira keeps line
  breaks», а не склейка строк в конвертере (так дешевле и безопаснее для кода и таблиц).
  Passes: 2/3

### 6. Дублирование

Подмножество Markdown названо в трёх местах: SKILL.md:67-70 (агенту), README.md:71-72
(человеку, коротко) и BLUEPRINT R12 (требование). У каждого из них свой читатель; копии
не расходятся. Нарушения нет.

### 7. Когда звать человека

Не применимо: ролей нет. Правило «report it» для кодов окружения не менялось.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

Новый раздел SKILL.md:65-74 занимает 8 строк вместо 25 (SKILL.md: 1248 → 1210 слов).
Неочевидное правило дано с причиной: «so wiki markup in plain text still works».

### 10. Описания навыков

Описание `tracker` не менялось и по-прежнему говорит, что навык держит и когда его
звать; Markdown для описания не нужен. Внешних навыков нет.

### 11. Нейтральность к провайдеру

Нового пути к файлу нет; запуск по-прежнему `python3 ${SKILL_DIR}/jira.py`; только
стандартная библиотека (`import re`).

### 12. Безопасность и границы

Новых действий, которые трудно отменить, нет: конвертер меняет только текст, который и
раньше отправлялся по тем же правилам записи (R11). Метка R9 добавляется после
конвертации и через конвертер не проходит: `mark(text_arg(...))`, `jira.py:643`, `:653`.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Коды разделяют окружение (4, 5, 9, 10, 12 — «report it») и ошибку запроса (2, 8, 11 — «fix»); сбой конвертера не даёт кода, текст уходит как есть. |
| 2. Work outside a flow, merge without a gate | Нет git-работы; запись в Jira — SKILL.md:25 «only when your role, your step or the human asks for it». |
| 3. Path outside the run's worktree | Не изменилось: `.lado/tracker.yaml` «from the current directory up to the repository root». |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

Ничего: R12 называет `tracker`, `jira.py` и тесты (раздел 3 и обратная проверка), меры
бюджета green, потоков и скелетов нет (R2).

## Previous findings

Отчёт 1.0.0 (1240f8d) находок не имел. Изменения плана:

| Пункт плана | Статус | Доказательство |
|---|---|---|
| Конвертер стандартной библиотеки, подмножество | RESOLVED | `jira.py` `to_wiki`, `_wiki`, `_inline`; запуски выше; `test_headings`, `test_emphasis_and_code`, `test_links`, `test_lists_nest_by_indent` |
| До `mark()` | RESOLVED | `jira.py:643` `comment = mark(text_arg(args.comment, args.wiki))`, `:653` |
| Символы wiki не экранируются | RESOLVED | запуск: `ping [~jdoe] about KEY-1 [t\|http://x]` без изменений; `test_wiki_characters_and_the_rest_pass_as_they_are` |
| Сбой → исходный текст | RESOLVED | `to_wiki`: `except Exception: return text`; `test_failure_sends_the_original_text` |
| `--wiki` у трёх команд | RESOLVED | `jira.py:693`, `:707`, `:716` |
| `--field description=` не конвертируется | RESOLVED | `jira.py:554` конвертирует только `args.description`; тест через поддельную Jira |
| `get` без изменений | RESOLVED | `cmd_get` вне диффа |
| Подсказки argparse | RESOLVED | `jira.py:692` «Markdown; '-' reads it from stdin», `:706`, `:715` |
| SKILL.md: раздел, пример, строки таблицы | RESOLVED | SKILL.md:65 «## Writing in Jira: Markdown»; :61 `**Done:**`; :35, :37, :38 `[--wiki]` |
| Тесты | RESOLVED | 59 тестов, OK |
| `kit.yaml` 1.0.1, README | RESOLVED | `version: 1.0.1`; README.md:71-72 |
| BLUEPRINT: R12, R7, разделы 3–5 | RESOLVED | R7 «Text goes to Jira as wiki markup (R12).»; R12; строки раздела 3 и обратная проверка; раздел 4 «(1.0.1)»; журнал 2026-10-09 |

Список build-report сверен с файлами: совпадает.

## Cut rules

| Удалённое правило (файл:строка в базе) | Где теперь |
|---|---|
| SKILL.md:65-89 таблица wiki-разметки (заголовки, выделение, `{code}`, цитата, панель, списки, упоминание, таблица, ссылка) | Заменена по плану (R12): агент пишет Markdown, подмножество — SKILL.md:67-69; упоминание — :70; панели и `{noformat}` — `--wiki`, :71-72 |
| SKILL.md:79 «`{noformat}` for logs» | Логи — блок ```` ``` ```` (→ `{code}`); `{noformat}` — через `--wiki`, SKILL.md:71 |
| SKILL.md:89 «inside `{code}` and `{noformat}` nothing is markup» | В конвертере: содержимое блока не трогается (`test_code_block_content_is_untouched`) |
| SKILL.md:89 «A blank line separates paragraphs» | Так же и в Markdown; правило не нужно |
| BLUEPRINT.md:60-63 R7 «SKILL.md teaches Jira wiki markup … the script converts nothing» | Заменено решением человека: R12 и R7 «Text goes to Jira as wiki markup (R12)» |

Правил не потеряно. Синтаксис панели после `--wiki` агент берёт из своих знаний: так решил
план («SKILL.md says "write Markdown"»).

## Missed earlier

Нет: полный проход по пяти файлам новых находок вне изменённого текста не дал.

## Left by the plan

Нет: план «Leave: none».

## Questions for the human

Нет.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не знает кита без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
- `[kit-builder]` Скрипты `kit-budget` требуют `uv run --script` (PyYAML): при запуске
  через `python3` они падают с `ModuleNotFoundError: No module named 'yaml'`. Скилл это
  говорит («Run it»); заметка только для тех, кто запускает их иначе.
