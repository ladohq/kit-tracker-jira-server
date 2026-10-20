# Отчёт о ките: tracker-jira-server 1.5.0

- Дата: 2026-10-20
- Кит: `.` (worktree запуска `improve/tracker-jira-server`, ветка
  `lado/kit-tracker-jira-server/improve-tracker-jira-server`), путь задан
- Коммит: ceddd32 (`kit.yaml` `version: 1.5.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: полная оценка (шаг `assess` плана LAD-113). Последний отчёт
  `kit-reports/tracker-jira-server-1.5.0-2026-10-13.md` — повторная оценка (без полной
  таблицы известных дыр по всему киту), а после оценённого им коммита 071e637 текст кита
  менялся (3372ba2, SKILL.md), поэтому он только фон.
- Проходы: три независимых субагента, у каждого — эта рубрика, `lado-kit-format` и папка
  кита, каждый с своего места (1: kit.yaml и README → SKILL.md → jira.py → BLUEPRINT;
  2: jira.py по командам против SKILL.md, с пробами против недоступного localhost без
  `JIRA_*`; 3: BLUEPRINT R1–R12 → SKILL.md по разделам → README, kit.yaml). Зависимых и
  ожидаемых навыков у кита нет. Однопроходных находок отброшено: 0, оставлено как
  подтверждённые: 2 (F5.2, F12.1). Предложение прохода 3 вписать метки в список R1
  слито с F5.1 (то же место по сути, исправление одно).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; жёлтых и красных мер нет |
| a. Потоки | 0 нарисовано: потоков нет (R2); в BLUEPRINT.md скелетов нет («Flow skeletons: none») |
| b. Рубрика | 6 находок (0 high, 3 medium, 3 low); 7 из 12 критериев без находок |
| Охват | полная оценка всего кита, 5 файлов текста (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты и `.lado/tracker.yaml` прочитаны на следы проекта |

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
# Complexity budget: tracker-jira-server 1.5.0

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
$ flow_diagram.py . --out kit-reports/tracker-jira-server-1.5.0-2026-10-20
no flows in .: nothing to do (exit status 0)
$ flow_diagram.py . --compare BLUEPRINT.md
no flows in . or BLUEPRINT.md: nothing to do (exit status 0)
```

### Тесты

```
$ uv run --no-project python -m unittest discover -s tests
Ran 133 tests in 8.108s

OK
```

## Исправить сначала

1. Убрать из описания навыка триггер одного процесса «mark it waiting for release»
   (F10.1).
2. Заменить пример метки `waiting_for_release` в SKILL.md и в подсказке jira.py нейтральным
   и сказать, что метку не выдумывают; вписать метки в список R1 (F5.1).
3. Проверять метки из `labels` настроек на пробелы при чтении настроек (F5.2).
4. Пример настроек `labels: [lado]` — решение человека (вопрос 2; F9.1).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Права записи навыка заданы одним правилом, SKILL.md:29 «Reading is
always fine. Create, transition, comment, assign, label, link or attach only when your
role, your step or the human asks for it», `edit` строже (SKILL.md:30-31).

### 2. Передачи между шагами

Не применимо: потоков нет. Вывод, который берут следующие шаги, задан: id комментария,
строка `attach` `<id> <name> attachment:<name>`, абсолютный путь `download`.

### 3. Готовность и исходы

Каждый код 1–12 таблицы SKILL.md:187-200 совпадает с тем, что поднимает jira.py (проход 2
сверил по каждой `cmd_*`); «already so … that is success» задано для `edit`, `assign`,
`label`, `link`; правило записи, которая могла пройти, — SKILL.md:202-204.

### 4. Независимая проверка

Не применимо: потоков и ревьюеров нет. Действия, добавляющие или меняющие действие,
пробуются на тестовой Jira 8.13.19 до выпуска (R10, README «Where it was tried»).

### 5. Противоречия

- **F5.1** [medium] `skills/tracker/SKILL.md:90` (и `skills/tracker/jira.py:1023`)
  > `  labels; a label is one word, no spaces (`waiting_for_release`).`
  > `                                 "e.g. waiting_for_release" % label)`
  Единственный пример метки в навыке и в отказе скрипта (exit 2) — метка одного процесса,
  что расходится с R1 («not for one project»). Сопоставления слова процесса с меткой
  проекта у кита нет (`labels` — лишь список для новых задач), а Jira молча создаёт любую
  метку: агент, которому шаг говорит «set the waiting-for-release label», возьмёт
  `waiting_for_release` из примера, а после отказа на `--add "waiting for release"` скрипт
  сам подскажет это имя (проба прохода 2) — в проекте с другой меткой появится метка,
  которую никто не смотрит. Пропуск дал R1: его список (BLUEPRINT.md:15 «Nothing project-
  or company-specific (Jira address, project key, issue type or status») не называет
  метки и слова процесса. Проходы дали medium (1, 3) и включили находку в F10.1 (2);
  взят medium, критерий 5 — по расхождению с R1, к которому ближе исправление.
  Fix: нейтральный пример в обоих местах (`needs_review`, как в плане); в пункт **label**
  одну фразу «use the label your step or the human names; do not make one up»; в список
  R1 — «label names, process words». Passes: 3/3

- **F5.2** [medium] `skills/tracker/jira.py:749`
  > `        fields["labels"] = list(config["labels"])`
  `_validate` (jira.py:192-198) не проверяет метки из `labels` на пробелы, хотя SKILL.md:90
  и `label` (exit 2) говорят «a label is one word, no spaces», а Jira метку с пробелом
  отклоняет. С такими настройками каждый `create` падает с exit 11 («Jira refused the
  values: labels»), строка 11 таблицы велит «fix the request once», но запрос агент не
  исправит — настройки меняет пользователь (SKILL.md:172): шаг тратится на повтор.
  Проверка: `parse_config('project: A\nlabels: [lado, agent made]\n', …)['labels']` →
  `['lado', 'agent made']`; тест закрепляет это (`tests/test_jira.py:38`
  `labels: [lado, "agent made"]`, :392).
  Fix: в `_validate` отказывать в метке `labels` с пробелом (exit 3, строка названа) и
  поправить фикстуру теста. Passes: 1/3, confirmed

### 6. Дублирование

- **F6.1** [low] `skills/tracker/SKILL.md:110`
  > `  only when your role, your step or the human asks for it, only to the tasks named, and`
  Правило записи для `attach` повторено целиком, хотя SKILL.md:29 уже называет `attach`
  в общем правиле; копии пока совпадают, но разойдутся при следующей правке (новое
  действие `field` добавит третью точку правки). tracker-yougile 0.4.0 это уже убрал (его
  F6.1). Fix: оставить в SKILL.md:109-111 только новое — «never secrets (`.env`, keys,
  database dumps, files with passwords or tokens)». Passes: 2/3

### 7. Когда звать человека

SKILL.md:182-185 «To **report** a failure: as a worker, send the supervisor that line and
the command with `send_message`; as the lead, tell the human. Then wait …»; exit 5
останавливает всех через лида (`STOP_ALL`, jira.py:52); `--reassign` только по слову
человека или шага (SKILL.md:86-87).

### 8. Повторные визиты

Не применимо: потоков и циклов нет.

### 9. Краткость и «почему»

- **F9.1** [low] `skills/tracker/SKILL.md:164`
  > `labels: [lado]                # added to every task you create`
  Единственный пример настроек ставит метку `lado` на каждую задачу, созданную агентом;
  человек, скопировавший пример, получит её в своём проекте, а агент может счесть её
  существующей (поиск JQL по `labels = lado`). Ни R6, ни README не требуют метки по
  умолчанию. Проходы назвали её по-разному (5, 9); взят критерий 9 — пример, не правило.
  Fix: решение человека (вопрос 2); рекомендация — `labels: [agent-made]` с комментарием
  «the project's own choice», либо убрать ключ из примера и описать фразой.
  Passes: 3/3

Остальное: правила, которые агент мог бы нарушить, несут причину (exit 5 — CAPTCHA;
«a guess may assign the task to someone else»; «`edit` rewrites text a person may have
written»); пустых фраз не найдено.

### 10. Описания навыков

- **F10.1** [medium] `skills/tracker/SKILL.md:10`
  > `  "mark it waiting for release", "close it", "tell the task what changed", "attach the`
  Описание навыка — то, по чему агент выбирает действие, — приводит шаг одного процесса
  (интегратор kit-sdlc; в собственных настройках этого репозитория слово отображено на
  `'Release: Waiting'`, `.lado/tracker.yaml:9`). В Jira нет такого понятия: в одном проекте
  это статус, в другом метка, в третьем ничего; описание толкает агента к метке, а F5.1
  даёт ему её имя, так что поведение будет разным от запуска к запуску.
  Fix: нейтральный пример, по плану — «add the label», «set the task's release» (последний
  — с действием `field`). Passes: 3/3

### 11. Нейтральность к провайдеру

Путь к скрипту — `${SKILL_DIR}/jira.py` с запасным «the folder this SKILL.md is in»
(SKILL.md:20-23); имён инструментов одного CLI нет; абсолютных и домашних путей в jira.py
нет.

### 12. Безопасность и границы

- **F12.1** [low] `README.md:86`
  > `are downloaded into a temporary folder outside the repository, and the credentials go`
  README обещает человеку, что скачанные файлы всегда вне репозитория; так только по
  умолчанию. С `--to` скрипт проверяет лишь, что папка есть и доступна на запись
  (jira.py:1251 `folder = os.path.abspath(args.to)`), так что `--to .` кладёт файл задачи
  (например, лог клиента) в worktree, откуда его может взять коммит. Агента держит лишь
  SKILL.md:117 «or into an existing folder outside the repository given with `--to`».
  Fix: README — «by default into a temporary folder …, or a `--to` folder outside the
  repository»; либо скрипт отказывает (exit 2) в `--to` внутри текущего репозитория,
  поднимаясь до `.git`, как `find_config`. Passes: 1/3, confirmed

Остальное: удаления нет; учётные данные только на схему, хост и порт `JIRA_URL`
(`same_server`), редиректы не следуются; `attach` без секретов; скачанное — данные.

## Проверка на привязку к проекту (требование человека)

| Где | След | Текст кита? |
|---|---|---|
| SKILL.md:10 | «mark it waiting for release» | да — F10.1 |
| SKILL.md:90, jira.py:1023 | `waiting_for_release` | да — F5.1 |
| SKILL.md:164 | `labels: [lado]` | да — F9.1, вопрос 2 |
| SKILL.md:156-169, README.md:35, :59-64 | `ABC`, `KEY-1`, `Bug`, `Code Review`, `customfield_10100`, `jira.example.com` | да, но это общие заглушки — не находка |
| BLUEPRINT.md:8 «The first Jira it serves is a corporate Jira Server 8.13 project», источники LAD-*, журнал | история и источники | да, агенты её не читают; человек оставил историю («историю можешь оставить») |
| tests/test_jira.py:38, :178, :392 (`lado`, `"agent made"`), :721-743 (`waiting_for_release`, `waiting for release`) | значения тестов | нет, но план велит их заменить; `"agent made"` закрепляет F5.2 |
| `.lado/tracker.yaml` (коммит 7c91437) | `board: Development`, `'Release: Waiting'`, `'Component: …'` | нет: собственные настройки этого репозитория для tracker-yougile, к пользователю не попадают; см. «Найдено попутно» |
| kit.yaml, BACKLOG.md | — / `TEST-21`, имена запусков | нет следов в kit.yaml; BACKLOG не текст кита |

`grep -rniE "waiting|LAD-[0-9]|polygon" skills README.md kit.yaml tests` (проверка из
плана) сейчас находит SKILL.md:10, :90, jira.py:1023 и tests/test_jira.py:721-743; `LAD-` и
`polygon` — ни одного.

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Сам навык отличает среду от запроса: коды 4, 5, 9, 10, 12 против 2, 8, 11, и «Any other message that does not start with `jira.py` … comes from `uv` or Python before the script ran» (SKILL.md:178-179) |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей, потоков и слияний нет; запись в Jira — только по SKILL.md:29 |
| 3. Путь вне worktree запуска | Скрипт через `${SKILL_DIR}`; настройки ищутся вверх до первого `.git`; скачивание вне репозитория по умолчанию, `--to` внутри не запрещён — F12.1 |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков и ролей нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: (a) `expects commands: uv`, README требует только `uv`; (b) CLI трекера или хоста там нет; (c) `dependencies.lado: ">=0.30"` |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей и `read_only` нет |

## Не прослежено

Каждый элемент (kit.yaml, `uv`, навык `tracker`, jira.py, тесты, README) назван в R1–R12
(раздел 3). Бюджет весь green; раздел 4 BLUEPRINT.md («Output of the kit-budget script on
the built kit (1.4.0; 1.5.0 adds no role, flow, skill or MCP server, so the values hold)»)
совпадает с выводом выше. Скелетов потоков нет, потоков тоже (R2). `.lado/tracker.yaml` и
BACKLOG.md не прослежены, но и не текст кита.

## Вопросы к человеку

1. Карта `fields`: одна, общая с `epic_link`/`epic_name`, или отдельный ключ для `field`?
   Рекомендую одну `fields`: tracker-yougile 0.5.0 (BLUEPRINT R3, R6, 516680d) берёт имя
   `field` из `fields`, и одинаковое имя ключа в обоих китах — часть взаимозаменяемости;
   `epic_link` и `epic_name` — зарезервированные имена, `field` с ними — exit 3 «not
   usable by `field`», как в плане; SKILL.md пишет это в комментарии примера.
2. `labels: [lado]` в примере настроек (SKILL.md:164, F9.1): оставить? Рекомендую заменить
   выдуманной меткой (`agent-made`) с пометкой, что метки — выбор проекта: tracker-yougile
   0.5.0 тоже перешёл на выдуманную метку и поле (его журнал, строка 0.5.0).
3. Значение `-` у `field`. tracker-yougile 0.5.0 отказывает в значении `-` (exit 2: Yougile
   очищает поле на `-`), план для Jira этого не называет, а в этом ките `-` везде значит
   «текст со stdin» (`comment KEY-1 -`, `--description -`). Рекомендую и здесь exit 2 на
   `-` (значение — в аргументе, очистка — `--clear`): интерфейс тот же, и агент не ждёт
   чтения stdin.
4. Различие интерфейсов вне плана: `create`/`edit` здесь берут `--summary`, в
   tracker-yougile — `--title`; процесс-кит, написавший `--summary`, на другом трекере
   получит exit 2. Рекомендую не расширять этот запуск, а завести отдельную задачу на оба
   кита (например, `--title` как второе имя `--summary` здесь).

## Найдено попутно

- Собственный `.lado/tracker.yaml` репозитория — настройки tracker-yougile (`board:
  Development`, `labels` как карта); jira.py в этом репозитории его не читает:
  `ValueError: .lado/tracker.yaml line 1: unknown key 'board'; known keys: project,
  issue_types, statuses, fields, link_types, labels` (exit 3). Пробу на тестовой Jira перед
  выпуском (R10) нужно запускать из другой папки с её собственным `.lado/tracker.yaml`.
  Это не текст кита и к пользователям не попадает.
