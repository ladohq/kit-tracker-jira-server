# Отчёт о ките: tracker-jira-server 1.6.0

- Дата: 2026-10-20
- Кит: `.` (worktree запуска `improve/tracker-jira-server`, ветка
  `lado/kit-tracker-jira-server/improve-tracker-jira-server`), путь задан
- Коммит: 6f175cf (`kit.yaml` `version: 1.6.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.5.0-2026-10-20.md`
  (85d77cb, оценивал ceddd32), `git diff ceddd32 6f175cf -- kit.yaml README.md BLUEPRINT.md
  agents flows skills`: 5 файлов, +232 −57. База — коммит, который план называет для
  своего отчёта. План — артефакт `plan`, сборка — `build-report`.
- Проходы: три независимых субагента по изменённому тексту и его окружению, по 12
  критериям и известным дырам, каждый со своего места (1: дифф jira.py против SKILL.md;
  2: изменённые требования BLUEPRINT против SKILL.md и jira.py, взаимозаменяемость с
  tracker-yougile 0.5.0 — его 516680d:BLUEPRINT.md и собранный 94a29f5; 3: SKILL.md по
  разделам, затем README, kit.yaml, jira.py, и проверка вырезанных правил по
  `git diff --word-diff`); затем полный проход четвёртым субагентом по всем пяти файлам,
  которые трогает дифф. Пробы — против фейковой Jira тестов на localhost, без `JIRA_*`;
  к настоящей Jira никто не обращался. Однопроходных находок отброшено: 1 (строка 3
  таблицы кодов «report it» на неизвестное имя `field` — сообщить безопаснее, чем
  выбрать поле по догадке, вреда нет); оставлено как подтверждённые: 1 (F5.2). Находки полного прохода подтверждены мной по коду.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; жёлтых и красных мер нет |
| a. Потоки | 0 нарисовано: потоков нет (R2); в BLUEPRINT.md скелетов нет |
| b. Рубрика | 6 находок в изменённом тексте (0 high, 3 medium, 3 low) + 2 в «Пропущено ранее» (1 medium, 1 low); все 6 находок отчёта 85d77cb RESOLVED; 7 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста (5 файлов дифа ceddd32..6f175cf) с полным проходом по этим 5 файлам; тесты: 146, OK |
| Правило остановки | не выполнено: 0 high, 3 medium (F3.1, F5.2, F12.1) — совет для гейта выпуска, не блок |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
expects commands: uv
```

Expects: `expects commands: uv`. Предупреждения `expects.commands needs LADO 0.30 or newer`
нет: `dependencies.lado: ">=0.30"`.

Read-only: строки `read-only roles: …` нет — ролей нет; `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.6.0

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

```
$ flow_diagram.py . --compare BLUEPRINT.md
no flows in . or BLUEPRINT.md: nothing to do (exit status 0)
```

### Тесты и следы проекта

```
$ uv run --no-project python -m unittest discover -s tests
Ran 146 tests in 9.627s

OK
$ grep -rniE "waiting|LAD-[0-9]|polygon|lado\b" skills README.md kit.yaml tests BACKLOG.md
```
Находит только пути `.lado/`, имя инструмента LADO, `LADO_AGENT`, метку `[LADO: …]`,
`lado kits`/`lado start` и `dependencies.lado` — ничего от проекта. Единственное
`waiting` в репозитории — его собственный `.lado/tracker.yaml:9` (настройки
tracker-yougile, не текст кита).

## Исправить сначала

Блокирующих нет. Если править до выпуска, то в таком порядке:

1. Проверка типа в `field` пропускает системные поля (`description`, `summary`) — требовать
   `custom == textfield` (F12.1).
2. Строка 11 таблицы кодов велит «fix the request once» при поле не того типа или не на
   экране — добавить «report it» и решить с человеком код (вопрос 1) (F3.1).
3. «Use the label your step or the human names» — добавить «your role» (F5.2).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Права записи — одно правило, SKILL.md:30-31, теперь с `field`.

### 2. Передачи между шагами

Не применимо: потоков нет. Вывод `field` пригоден для следующего шага и тот же, что у
tracker-yougile (`KEY: release = v` / `not set` / `old -> new` / `, nothing changed`).

### 3. Готовность и исходы

- **F3.1** [medium] `skills/tracker/SKILL.md:212` (и SKILL.md:101-102)
  > `| 11 | Jira refused the request (bad JQL, a refused field value, unknown type, transition not open, a `field` not a single-line text field or not on the edit screen, a link word not among the four or a link type this Jira lacks, an `attachment:` name the task lacks or one with `!`, `\|` or `]`, a file over Jira's size limit or attachments disabled, a file served from another address than `JIRA_URL` or by a redirect), or `assign` refused a task another account holds | read the line, fix the request once; if it still fails, report it (`assign`: report it, never try another login or `--reassign` on your own; a link type this Jira lacks: report it, the user sets `link_types`; a file too large, attachments disabled or another address: report it) |`
  Поле не того типа и поле не на экране редактирования исправляет пользователь
  (`fields`) или администратор Jira, а строка велит агенту «fix the request once» и, в
  отличие от `link_types` и больших файлов, не говорит «report it»: агент тратит повтор
  или пробует другое имя из `fields` — и пишет значение не в то поле. Сообщение скрипта
  тоже не говорит «report it» («… is of type textarea, not a single-line text field»).
  К тому же та же ошибка настроек в tracker-yougile 0.5.0 — exit 3 («a field's sticker
  has states | report it; the user fixes the file»), здесь — 11, по плану (R8). Проходы
  дали medium (1) и low (2); взят medium.
  Fix: в «What you do» строки 11 — «a `field` of another type or not on the edit screen:
  report it, the user fixes `fields` or the screen»; код (11 или 3, как в yougile) — вопрос
  1. Passes: 2/3

### 4. Независимая проверка

Не применимо: потоков нет. Проба `field` на тестовой Jira 8.13.19 (R10) ещё не сделана —
план ставит её перед гейтом выпуска; README «Where it was tried» пока называет только
1.5.0. Это шаг запуска, не находка текста.

### 5. Противоречия

- **F5.1** [low] `skills/tracker/SKILL.md:30`
  > `Reading is always fine. Create, transition, comment, assign, label, field, link or attach`
  В списке записей стоит всё действие `field`, хотя его чтение — не запись: R11
  (BLUEPRINT.md:243 «(`field` with a value or `--clear` is a write, reading it is not)»),
  README («set a field») и tracker-yougile говорят иначе. Агент может не читать значение
  без просьбы. Fix: «set a field» вместо «field». Passes: 2/3

- **F5.2** [medium] `skills/tracker/SKILL.md:92`
  > `  labels. Use the label your step or the human names; do not make one up. A label is`
  Правило записи (SKILL.md:31 «only when your role, your step or the human asks for it»)
  допускает роль, а новая фраза — нет. Метку называют как раз роли: интегратор kit-sdlc
  в своём промпте (kit-sdlc `agents/integrator.md:55` «waiting-for-release label, or ask
  the human in your note to set it») — агент одного запуска поставит её, другого —
  откажет как «не названную шагом». Fix: «Use the label your role, your step or the human
  names»; так же в R1. Passes: 1/3, confirmed (вторая цитата — SKILL.md:31)

### 6. Дублирование

Правило записи теперь в одном месте (SKILL.md:30-31), у `attach` осталось только «Never
attach secrets» (F6.1 RESOLVED); «already so» для `field` — в общем пункте
**assign**, **label**, **field** (SKILL.md:90-91).

### 7. Когда звать человека

Коды `field` ведут к «report it» (строка 3 — «the user fixes the file»), кроме строки 11
(F3.1). Правило доклада (SKILL.md, раздел «When the script fails») не менялось.

### 8. Повторные визиты

Не применимо: потоков нет. Повтор `field` после exit 9 безопасен: значение, которое уже
стоит, даёт «nothing changed».

### 9. Краткость и «почему»

- **F9.1** [low] `skills/tracker/SKILL.md:93`
  > `  any word without spaces (`needs_review`); in `tracker-yougile` only a word of its`
  Конец фразы («so a process kit that runs on both uses label words without spaces») —
  совет автору процесс-кита; агент, работающий по навыку, по нему ничего не делает: он
  берёт метку, которую ему назвали. Фразу просил план («a sentence that labels in Jira are
  any word without spaces, in Yougile a word of `labels`»), и в R3 она есть. Fix: решение
  человека; если убирать — закончить на «(`needs_review`)», правило оставить в BLUEPRINT и
  README. Passes: 2/3 (проход 1 и полный проход)

### 10. Описания навыков

Описание называет `field` и повод («set the task's release»), процессной фразы «mark it
waiting for release» нет (F10.1 RESOLVED); kit.yaml и README согласованы.

### 11. Нейтральность к провайдеру

`${SKILL_DIR}` с запасным путём; имён инструментов CLI нет; новых путей в jira.py нет.

### 12. Безопасность и границы

- **F12.1** [medium] `skills/tracker/jira.py:1108`
  > `    if schema.get("type") != "string" or schema.get("custom", TEXT_FIELD) != TEXT_FIELD:`
  У системного поля нет ключа `custom`, и по умолчанию он считается `textfield`: проверку
  проходят `summary`, `description` и `environment`, хотя R7 (BLUEPRINT.md:177 «multi-line
  or option field») и SKILL.md:96 обещают только однострочное текстовое поле. Проба
  (проходы 2, 3 и полный): `fields: release: description`, `field TEST-1 release x` — exit 0,
  PUT `{'fields': {'description': 'x'}}`: описание, написанное человеком, заменено одной
  строкой без метки `[LADO: …]` (R9) и по правилу записи `field` (роль, шаг или человек), а
  не по более строгому правилу `edit` (только человек или шаг, R11). Нужна одна неверная
  строка настроек — оттого не high; проходы дали low (1, 3) и medium (2), взят medium.
  Fix: требовать `schema.get("custom") == TEXT_FIELD` без значения по умолчанию (системное
  поле — exit 11 с типом); добавить в `test_field_not_single_line_text_is_refused` случаи
  `summary` и `description`. Passes: 3/3

- **F12.2** [low] `skills/tracker/jira.py:1346`
  > `        repository = find_repository(os.getcwd())`
  Поиск останавливается на ближайшем `.git` — в worktree LADO это его собственный файл
  `.git`, а worktree лежит внутри основной копии (`<repo>/.lado/worktrees/…`, как у этого
  кита). Поэтому `download … --to <основная копия>/docs` не отказан: файл задачи ложится
  среди неотслеживаемых файлов человека (известная дыра 3). Агента держит лишь
  SKILL.md:129 «an existing `--to` folder outside the repository». Проба (полный проход,
  вложенный worktree с файлом `.git`): exit 0, путь в основной копии. Проходы 1 и 2 видели
  то же, но сочли маловероятным.
  Fix: отказывать и в папке внутри основной копии (её путь — из `gitdir:` файла `.git` или
  `git rev-parse --git-common-dir`), либо в SKILL.md:129 — «outside the repository and the
  checkout that holds it». Passes: 2/3 (проход 3 и полный проход)

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Навык по-прежнему отличает среду (4, 5, 9, 10, 12; сообщения `uv`/Python) от запроса (2, 8, 11) |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и слияний нет; запись `field` — в общем правиле SKILL.md:30-31 |
| 3. Путь вне worktree запуска | F12.2 (`--to` в основную копию); по умолчанию — `mkdtemp`, `--to` внутри репозитория — exit 2 |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; новых команд нет (`/rest/api/2/field` — тот же скрипт) |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего, что блокирует. `field` прослежен в R3, R6, R7, R8, R10, R11, разделе 3 и строке
журнала 1.6.0; бюджет green (раздел 4 обновлён выводом этой сборки); потоков и скелетов
нет. Одно поведение не названо в BLUEPRINT: id из `fields`, которого нет в этой Jira, —
exit 3 («this Jira has no field … of 'fields.release: …'»). Build-report называет его
сам; оно следует из R6 («an action that needs a missing setting names it») и совпадает с
tracker-yougile (неизвестный стикер — exit 3), SKILL.md (строка 3 и пункт **field**) его
описывает. Совет: одна фраза в R8 при следующей правке BLUEPRINT.

## Прежние находки

Отчёт 85d77cb (полная оценка ceddd32):

| Находка | Статус | Доказательство |
|---|---|---|
| F10.1 [medium] SKILL.md:10 «mark it waiting for release» | RESOLVED | SKILL.md:9-11 «"add the label", "set the task's release"»; grep пуст |
| F5.1 [medium] пример `waiting_for_release` | RESOLVED | SKILL.md:92-93 «Use the label your step or the human names; do not make one up. A label is any word without spaces (`needs_review`)»; jira.py:1055 «e.g. needs_review»; R1 называет «label names, process words». Новое замечание — F5.2 |
| F5.2 [medium] метка с пробелом в `labels` проходит | RESOLVED | jira.py:202-206 `_validate`: «label '%s' has a space; a label is one word, e.g. needs_review» (exit 3, строка названа); тест `test_label_with_a_space_is_refused`; фикстура `labels: [agent-made, triaged]` |
| F6.1 [low] повтор правила записи у `attach` | RESOLVED | SKILL.md:122-123 только «Never attach secrets (`.env`, keys, database dumps, files with passwords or tokens)» |
| F9.1 [low] `labels: [lado]` | RESOLVED | SKILL.md:176 `labels: [agent-made]          # added to every task you create; the project's own words` |
| F12.1 [low] README:86 обещает «вне репозитория» | RESOLVED | README «by default into a temporary folder, or into a `--to` folder outside the repository, never inside it»; jira.py:1345-1352 `--to` внутри — exit 2; тест `test_download_into_the_repository_is_refused`. Остаток — F12.2 |

План (артефакт `plan`):

| Пункт плана | Статус | Доказательство |
|---|---|---|
| `field`: вывод, already so, `--clear` | RESOLVED | `cmd_field` (jira.py:1087-1130), строки как в R3 tracker-yougile; тесты `FieldTest` (11) |
| exit 2 до запроса: значение с `--clear`, пустое, с переносом, `-` | RESOLVED | jira.py:1089-1100; `test_bad_values_are_refused_before_any_request` |
| имя из `fields` кроме epic_*, иначе exit 3 с именами | RESOLVED | `_field_id`; `test_unknown_and_epic_names_are_refused` |
| тип из `/rest/api/2/field`, другой — 11 с типом | STILL OPEN частично | textarea и дата отказаны (тест), системные строковые поля проходят — F12.1 |
| PUT `{"fields": {id: value}}`, `null` очищает; не на экране — 11 | RESOLVED | jira.py:1124-1126; `test_refused_by_jira` |
| `get`: `Fields:` / `Fields: none` / без строки | RESOLVED | `_print_issue`; `test_get_shows_fields`, `test_get_without_usable_names_has_no_fields_line` |
| SKILL.md: описание, таблица (13), правило записи, пример `release`, фраза о метках | RESOLVED | SKILL.md:6-11, :48, :30, :180, :92-94 (замечания F5.1, F9.1) |
| kit.yaml и README называют `field`, README — как завести поле | RESOLVED | kit.yaml description; README:77-80 |
| следы проекта по всему киту | RESOLVED | grep выше пуст |
| BACKLOG: `--summary`/`--title` | RESOLVED | BACKLOG.md, пункт добавлен |
| `version: 1.6.0` | RESOLVED | kit.yaml:2 |
| проба на тестовой Jira | открыт по плану | шаг перед гейтом выпуска |

## Вырезанные правила

| Удалённое правило (файл:строка в базе) | Где оно теперь |
|---|---|
| SKILL.md:109-110 «Attaching is a write: only when your role, your step or the human asks for it, only to the tasks named» | SKILL.md:30-31, общее правило, `attach` в списке |
| SKILL.md:110-111 «never secrets (`.env`, keys, database dumps, …)» | SKILL.md:122-123 «Never attach secrets (…)» |
| SKILL.md:88-90 «**assign**, **label**: … already so … success»; «a label is one word, no spaces» | SKILL.md:90-93, тот же пункт с `field`; «any word without spaces» |
| SKILL.md:116-117 «into a new temporary folder outside the repository, or into an existing folder outside the repository given with `--to`» | SKILL.md:128-129, «by default into a new temporary folder, or into an existing `--to` folder outside the repository (one inside is exit 2)»; `mkdtemp` вне репозитория по устройству |
| README:86 «downloaded into a temporary folder outside the repository» | README, «by default into a temporary folder, or into a `--to` folder outside the repository, never inside it» |
| SKILL.md:29 правило записи без `field` | SKILL.md:30-31, дополнено |
| строки 2, 3, 11 таблицы кодов | те же строки, только дополнения |
| BLUEPRINT R1, R3, R6, R7, R8, R10, R11 | те же требования, только дополнения (R11: «the rule is said once») |

Ни одно правило не потеряно.

## Пропущено ранее

- **F5.3** [medium] `skills/tracker/jira.py:1319`
  > `                                        "(do not attach again; send it with comment): %s"`
  Когда после загрузки `attach` комментарий не прошёл, скрипт при любом коде пишет «the
  comment was not added … send it with comment». После exit 5 это ещё одна попытка входа
  против строки 5 («one more try can lock the login») и `STOP_ALL` в той же строке; после
  9 или 5xx комментарий мог быть добавлен — повтор даст дубль, а после 9 нарушает «send
  Jira nothing more». `transition --comment` разбирает каждый код (jira.py:930-953), R8
  требует это только для перехода. Проба полного прохода: 401 на комментарии — exit 5,
  «… but the comment was not added (do not attach again; send it with comment): Jira
  refused the credentials (401) …»; 502 — exit 12, тот же совет.
  Fix: взять для комментария `attach` совет `transition` («may not have been added» и
  проверка `get` после 9/5xx, «report it» после 4/5/6/7/10/429, «fix and send» только после
  11); дополнить R8. Passes: full pass, confirmed

- **F3.2** [low] `skills/tracker/jira.py:1388`
  > `            raise Failure(getattr(failure, "code", USAGE),`
  Локальная ошибка записи при `download` (`OSError`: диск полон, временная папка
  недоступна) уходит с exit 2, а строка 2 велит «fix the command (`--help`)» — исправлять
  нечего, агент тратит повтор. Fix: exit 1 для `OSError`, либо назвать «a file that cannot
  be written» в строке 2 с «report it». Passes: full pass, confirmed

Обе находки не блокируют и не идут в правило остановки.

## Оставлено планом

Ничего: план не оставлял находок («Leave: none»).

## Вопросы к человеку

1. Поле не того типа в `field`: exit 11 (как сейчас и как решено в плане) или exit 3, как
   у tracker-yougile для стикера с состояниями? Рекомендую exit 3 «report it; the user
   fixes the file» для поля не того типа (это ошибка настроек, и коды обоих китов совпадут),
   а поле не на экране оставить 11 с «report it» в строке 11 (F3.1).
2. Исправлять ли F12.1, F3.1, F5.2 (medium) до выпуска? Рекомендую да: правки в 1–2
   строки и тест, а F12.1 закрывает перезапись описания без метки. Low (F5.1, F9.1, F12.2)
   и «Пропущено ранее» (F5.3, F3.2) — по желанию; F5.3 советую взять туда же, это тот же
   класс правил, что R8 уже держит для `transition`.
