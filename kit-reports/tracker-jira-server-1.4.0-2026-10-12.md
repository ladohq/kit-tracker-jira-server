# Отчёт о ките: tracker-jira-server 1.4.0

- Дата: 2026-10-12
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-4-0`), путь задан
- Коммит: 07b1cd7 (`kit.yaml` `version: 1.4.0`). Визит 1 оценивал 0c5a8a6 (отчёт 14dd988).
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.3.0-2026-10-12.md`
  (972c83d, оценивал 4e1153c; на шаге `assess` взят как оценка). База — 4e1153c, её
  называет план. Дифф `git diff 4e1153c -- kit.yaml README.md BLUEPRINT.md agents flows skills`
  затрагивает 5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md,
  skills/tracker/jira.py (BLUEPRINT — в основном коммит чертежа b382529, автор поменял
  только раздел 4).
- Визит 2 шага `evaluate`, после гейта выпуска («исправить F3.1, F3.2; F5.1 - только по
  просьбе»). С визита 1 (0c5a8a6 → 07b1cd7) изменились: `except` в `_link_task` (F3.1),
  тест 503 → 12 и 401 → 5 (тестов 108), R8 и строка 1.4.0 журнала (F3.2), SKILL.md:51 и
  R11 (F5.1).
- Проходы визита 2. Изменение — 14 строк текста кита. Три прохода я сделал сам, по 12
  критериям и известным дырам: 1) `jira.py` 1000-1015 против `Jira.call` и проба из
  визита 1 (KEY2 → «Jira did not answer» теперь даёт `exit 9`, а не 7); 2) SKILL.md:27-51
  против R11; 3) R8 против кода и строк 6/7/11 SKILL.md. Новых находок нет. Полный проход
  по SKILL.md и коду `link` был на визите 1 (ниже); правки визита 2 касаются только мест его
  находок, и я перечитал их вместе с окружением. Однопроходных находок отброшено: 0.
- Проходы визита 1: изменение — около 150 строк текста кита. Сначала я прошёл его сам: дифф
  `jira.py` (`cmd_link`, `_link_task`, `_link_url`, `_link_phrase`, `_print_issue`, парсер)
  против `Jira.call`/`_http_failure`, затем SKILL.md и BLUEPRINT R3–R11 против кода. Вторым
  был полный проход (Re-evaluation 5) по 12 критериям и известным дырам. Его делал
  отдельный субагент: SKILL.md целиком, всё, что касается `link` в `jira.py`, и изменённые
  части BLUEPRINT. Он гонял пробы только против фейковой Jira из тестов. Оба прохода дали
  F3.1 и F5.1. F3.2 нашёл только я; она оставлена как подтверждённая цитатой и кодом.
  Третьего отдельного прохода не было. Однопроходных находок отброшено: 1 (у субагента:
  `link https://… TEST-2` даёт 7, а не 2; вреда нет). Оставлено как подтверждённые: 1.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений; `expects commands: uv` |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 0 открытых находок; F3.1, F3.2, F5.1 визита 1 RESOLVED; 12 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по SKILL.md, всему, что касается `link` в `jira.py`, и изменённым частям BLUEPRINT (визит 1); визит 2 — правки 0c5a8a6 → 07b1cd7 с окружением; тесты: 108, OK |
| Правило остановки | выполнено: 0 high, 0 medium в изменённом тексте |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
expects commands: uv
```

Expects: `expects commands: uv`. Предупреждения `expects.commands needs LADO 0.30 or newer`
нет: `dependencies.lado: ">=0.30"`.

Read-only: строки `read-only roles: …` нет, потому что ролей нет; `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.4.0

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
no flows in . or BLUEPRINT.md: nothing to do (exit status 0)
```

## Исправить сначала

Ничего: открытых находок нет.

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Границы записи для агентов — в SKILL.md:27-30.

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

Каждый путь ошибки `link` имеет свой код: после 404 на POST чтение KEY2 даёт 11 (задача
есть) или 7 (`if missing.code != NOT_FOUND: raise` — прочие сохраняют свой код,
`jira.py:1007-1009`); R8 описывает это (`BLUEPRINT.md:138-140`). F3.1 и F3.2 визита 1
RESOLVED (см. «Прежние находки»).

### 4. Независимая проверка

Не применимо: потоков нет. Направление связи проверено на локальной Jira 8.13.19 до того,
как его закрепил тест (trial-1.4.0, R10).

### 5. Противоречия

SKILL.md:51 «To link a task to the task it was created from: `link NEW-KEY OLD-KEY --type
derived`.» говорит, как связать, а когда — решает SKILL.md:27 («link only when your role,
your step or the human asks for it»); R11: «under the same rule: only when asked». F5.1
визита 1 RESOLVED.

### 6. Дублирование

Повторов нет. Значение слов и «already linked» описаны в одном месте (пункт **link**
SKILL.md:85-88). Строки 6/7/11 таблицы кодов ссылаются на случаи `link`, не повторяя их.

### 7. Когда звать человека

Неизвестный этой Jira тип ведёт к «report it, the user sets `link_types`» (SKILL.md,
строка 11): агент правит не настройки, а только сообщает.

### 8. Повторные визиты

Не применимо: потоков нет. Повтор той же связи — успех без изменений: «A link already
there changes nothing and says so: that is success.»

### 9. Краткость и «почему»

Правило о `derived` объяснено: «Jira has no "derived" type, so `derived` shows there as
"relates to".» Направление в коде тоже: «Jira's REST API names the ends backwards».

### 10. Описания навыков

Описание навыка называет новое действие: «link a branch or commit, link a task to a
task». Описание kit.yaml и README согласованы с ним.

### 11. Нейтральность к провайдеру

Нового пути и имён CLI нет; скрипт по-прежнему через `${SKILL_DIR}/jira.py`.

### 12. Безопасность и границы

Запись `link`, и `derived` тоже, подчиняется общему правилу SKILL.md:27. Связи между проектами
разрешены по решению человека. Ошибки аргументов (`--type` с URL, `--title` с ключом,
связь задачи с самой собой) дают выход 2 до любого запроса.

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Сообщения `uv`/Python SKILL.md по-прежнему отличает от сообщений скрипта |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и потоков нет; `link` — только по просьбе роли, шага или человека (SKILL.md:27), `derived` тоже (R11) |
| 3. Путь вне worktree запуска | Нет: `${SKILL_DIR}/jira.py`; `.lado/tracker.yaml` ищется от текущей папки |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; новых команд нет |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего. Задача–задача `link` прослежена в R3, R6 (`link_types`), R7 (`POST issueLink`),
R8, R10 (проверка направления) и R11; журнал раздела 5 имеет строку 1.4.0. Бюджет
зелёный; раздел 4 «Output of the kit-budget script on the built kit (1.4.0)» совпадает с
выводом выше. Скелетов потоков нет: потоков нет (R2). Чтение KEY2 после 404 названо в R8
(`BLUEPRINT.md:138-140`).

## Прежние находки

Визит 1 (отчёт 14dd988, коммит 0c5a8a6):

| Находка | Статус | Доказательство |
|---|---|---|
| F3.1 [medium] `jira.py:1007` любая ошибка чтения KEY2 → 7 | RESOLVED | `jira.py:1007-1009` «except Failure as missing: / if missing.code != NOT_FOUND: / raise»; проба визита 1 (KEY2 → «Jira did not answer») теперь `exit 9 Jira did not answer in 30 seconds`; тест 503 → 12, 401 → 5; `Ran 108 tests … OK` |
| F3.2 [low] R8 без чтения KEY2 | RESOLVED | `BLUEPRINT.md:138-140` «after a 404 the script reads KEY2 once: KEY2 there is exit 11, KEY2 missing exit 7, any other failure of that read keeps its own code»; строка 1.4.0 журнала дополнена |
| F5.1 [medium] SKILL.md:51 правило `derived` как приказ | RESOLVED | SKILL.md:51 «To link a task to the task it was created from: …»; `BLUEPRINT.md:179-180` «under the same rule: only when asked» — по решению человека «F5.1 - только по просьбе» |

В отчёте 1.3.0 открытых находок не было. Пункты плана:

| Пункт плана | Статус | Доказательство |
|---|---|---|
| Парсер: URL / ключ / иначе 2; сам с собой, `--type` с URL, `--title` с ключом — 2 до запроса | RESOLVED | `jira.py` `cmd_link`: «a task cannot be linked to itself», «--title is for a link to a URL, not to a task»; trial строка 7 |
| Слова → имена, `link_types`, неизвестное слово — 11 со списком | RESOLVED | `LINK_WORDS`, `CONFIG_MAPS = (…, "link_types")`, «link type '%s' is unknown; use one of: %s» |
| «Already linked» — один GET, тот же тип, направление; любое для симметричного | RESOLVED | `_link_task`: `if kind.get("inward") == kind.get("outward"): ends.append("inwardIssue")`; trial строки 4, 6 |
| `POST issueLink` с `type: {name}`, без обратного чтения | RESOLVED | `body = {"type": {"name": name}, "inwardIssue": {"key": key}, …}` |
| 401 без заголовка и 403 → 6; 404 → 7; 400 → 11 с `link_types` | RESOLVED, с отступлением | 404 при существующей KEY2 → 11 (проверка на Jira, build-report), описано в R8; F3.1, F3.2 RESOLVED |
| `get`: строка `Links:` | RESOLVED | `_print_issue`: `print("Links: " + "; ".join(links))`; trial строки 2, 3 |
| Направление проверено на тестовой Jira до теста | RESOLVED | trial-1.4.0: «`inwardIssue` = KEY, `outwardIssue` = KEY2 gives "KEY blocks KEY2"» |
| Тесты | RESOLVED | `Ran 108 tests … OK` |
| SKILL.md, README, kit.yaml 1.4.0 | RESOLVED | строка действий, пункт **link**, правило `derived`, пример `link_types`, строки 6/7/11; README:5, :72; kit.yaml `version: 1.4.0` |

## Вырезанные правила

| Удалённое правило (файл:строка в базе) | Где оно теперь |
|---|---|
| kit.yaml:4-7 описание («link a branch or commit to tasks») | kit.yaml:4-8, то же, дополнено «or another task» |
| README.md:4-6 вступление | README.md:4-7, то же, дополнено |
| README.md:70-71 разделы настроек | README.md:71-73, дополнено именами типов связей |
| SKILL.md:5-7 описание | SKILL.md:5-8, то же, дополнено |
| SKILL.md строки кодов 6, 7, 11 | те же строки, только дополнения; правило `assign` в строке 11 на месте |
| BLUEPRINT R3, R6, R7, R8, R10, R11, раздел 4 | те же требования, только дополнения |
| jira.py `cmd_link` (тело для URL) | `_link_url`, тот же запрос; `test_link` проходит |
| (визит 2) SKILL.md:51 «A task created from another task is linked to it» | SKILL.md:51 «To link a task to the task it was created from»; изменено по решению человека (F5.1), «когда» — SKILL.md:27 |
| (визит 2) BLUEPRINT R11 «A task created from another task is linked to it with» | BLUEPRINT.md:179-180, с «only when asked» |
| (визит 2) BLUEPRINT R8 и строка журнала 1.4.0 | те же, только дополнения |
| (визит 2) jira.py `except Failure:` | `jira.py:1007-1011`: правило «нет KEY2 → 7» на месте, сужено до 404 |

Ни одно правило не потеряно.

## Пропущено ранее

Нет.

## Оставлено планом

Ничего: «Leave: none».

## Вопросы к человеку

Нет.
