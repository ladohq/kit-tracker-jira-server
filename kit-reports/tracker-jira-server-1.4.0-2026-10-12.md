# Отчёт о ките: tracker-jira-server 1.4.0

- Дата: 2026-10-12
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-4-0`), путь задан
- Коммит: 0c5a8a6 (`kit.yaml` `version: 1.4.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.3.0-2026-10-12.md`
  (972c83d, оценивал 4e1153c; на шаге `assess` взят как оценка). База — 4e1153c, её
  называет план. Дифф `git diff 4e1153c -- kit.yaml README.md BLUEPRINT.md agents flows skills`
  затрагивает 5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md,
  skills/tracker/jira.py (BLUEPRINT — в основном коммит чертежа b382529, автор поменял
  только раздел 4).
- Проходы: изменение — около 150 строк текста кита. Сначала я прошёл его сам: дифф
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
| b. Рубрика | 3 находки (0 high, 2 medium, 1 low); 10 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по SKILL.md, всему, что касается `link` в `jira.py`, и изменённым частям BLUEPRINT; тесты: 107, OK |
| Правило остановки | не выполнено: 0 high, 2 medium (F3.1, F5.1). Это совет для гейта выпуска, а не блок |

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

1. Выход 7 только при 404 на чтении KEY2, остальные ошибки пробрасывать как есть (F3.1).
2. Правило `derived` переписать как «как связать», а не «когда связывать» (F5.1).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Границы записи для агентов — в SKILL.md:27-30; см. F5.1.

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.1** [medium] `skills/tracker/jira.py:1007`
  > `            except Failure:`
  После 404 на `POST issueLink` скрипт читает KEY2 и превращает в выход 7 («a task is
  missing or not visible to you») любую ошибку этого чтения, а не только 404. Так 503 и
  429 (должно быть 12), 403 (6), 401 или CAPTCHA (5, с «всем остановиться»), а также
  «Jira не ответила» (9, «send Jira nothing more») становятся выходом 7. Строка 7 SKILL.md
  говорит «check the key», и агент запускает команду снова. При 5 это лишняя неудачная
  попытка входа, а значит риск блокировки. При 9 — новые запросы к Jira, которая не отвечает.
  Fix: `except Failure as second:` → если `second.code != NOT_FOUND`, `raise`; иначе
  нынешний выход 7. Добавить тест: GET KEY2 → 503 даёт выход 12.
  Доказательство (пробы против фейка): POST → 404 «No issue link type…»; GET KEY2 → 503,
  429, 403 или 401 — во всех случаях `exit 7 … a task is missing or not visible to you`;
  GET KEY2 → «Jira did not answer» (9) — `exit 7 cannot link A-1 and A-2: …`.
  Passes: 2/2 (мой проход и полный проход субагента).

- **F3.2** [low] `BLUEPRINT.md:136`
  > `  permission to link (exit 6, no stop for every agent), a 404 on it is a task missing or`
  В R8 написано, что 404 на записи связи — это выход 7. Код (`jira.py:1002-1006`) после
  404 читает KEY2 и, если задача есть, возвращает 11: на проверке Jira 8.13 ответила 404 на
  неизвестный тип (trial-1.4.0, строки 10/10'). Поведение верное и сохраняет другую часть
  R8 («a type Jira refuses is exit 11»), но чертёж его не описывает. Автор отметил это
  в build-report сам.
  Fix: в R8 после «a 404 on it» дописать «(the script then reads KEY2 once: present → the
  type was refused, exit 11; missing → exit 7)», а строку 1.4.0 журнала дополнить этим
  фактом из проверки.
  Passes: 1/2, подтверждено: код `jira.py:1003` «# Jira 8.13 answers an unknown link type
  with 404 too; KEY was just found.» расходится с цитатой R8.

### 4. Независимая проверка

Не применимо: потоков нет. Направление связи проверено на локальной Jira 8.13.19 до того,
как его закрепил тест (trial-1.4.0, R10).

### 5. Противоречия

- **F5.1** [medium] `skills/tracker/SKILL.md:51` (то же правило — в `BLUEPRINT.md:177`, R11)
  > `A task created from another task is linked to it: \`link NEW-KEY OLD-KEY --type derived\`.`
  Это написано как правило («is linked»), а SKILL.md:27 гласит: «Create, transition,
  comment, assign, label or link only when your role, your step or the human asks for
  it». Агент, который заводит баг «найденный при работе над ABC-1», прочтёт строку 51 как
  приказ и создаст связь, о которой никто не просил. Другой агент так не сделает. Что
  значит «created from», тоже не сказано.
  Fix: SKILL.md «To link a task to the task it was created from: `link NEW-KEY OLD-KEY
  --type derived`.», и R11 так же. Если человек хочет, чтобы связь ставилась всегда, без
  просьбы, — то же правило, но в абзаце SKILL.md:27-30 как явное исключение («…; a task
  you create from another task you also link to it with …»). Субагент дал medium, я —
  low; взято medium.
  Passes: 2/2.

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

Запись `link` подчиняется общему правилу SKILL.md:27 (см. F5.1). Связи между проектами
разрешены по решению человека. Ошибки аргументов (`--type` с URL, `--title` с ключом,
связь задачи с самой собой) дают выход 2 до любого запроса.

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Сообщения `uv`/Python SKILL.md по-прежнему отличает от сообщений скрипта |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и потоков нет; `link` — только по просьбе роли, шага или человека (SKILL.md:27), см. F5.1 |
| 3. Путь вне worktree запуска | Нет: `${SKILL_DIR}/jira.py`; `.lado/tracker.yaml` ищется от текущей папки |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; новых команд нет |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего. Задача–задача `link` прослежена в R3, R6 (`link_types`), R7 (`POST issueLink`),
R8, R10 (проверка направления) и R11; журнал раздела 5 имеет строку 1.4.0. Бюджет
зелёный; раздел 4 «Output of the kit-budget script on the built kit (1.4.0)» совпадает с
выводом выше. Скелетов потоков нет: потоков нет (R2). Чтение KEY2 после 404 не названо в
R8 — см. F3.2.

## Прежние находки

В отчёте 1.3.0 открытых находок не было.

| Пункт плана | Статус | Доказательство |
|---|---|---|
| Парсер: URL / ключ / иначе 2; сам с собой, `--type` с URL, `--title` с ключом — 2 до запроса | RESOLVED | `jira.py` `cmd_link`: «a task cannot be linked to itself», «--title is for a link to a URL, not to a task»; trial строка 7 |
| Слова → имена, `link_types`, неизвестное слово — 11 со списком | RESOLVED | `LINK_WORDS`, `CONFIG_MAPS = (…, "link_types")`, «link type '%s' is unknown; use one of: %s» |
| «Already linked» — один GET, тот же тип, направление; любое для симметричного | RESOLVED | `_link_task`: `if kind.get("inward") == kind.get("outward"): ends.append("inwardIssue")`; trial строки 4, 6 |
| `POST issueLink` с `type: {name}`, без обратного чтения | RESOLVED | `body = {"type": {"name": name}, "inwardIssue": {"key": key}, …}` |
| 401 без заголовка и 403 → 6; 404 → 7; 400 → 11 с `link_types` | RESOLVED, с отступлением | 404 при существующей KEY2 → 11 (проверка на Jira, build-report); см. F3.1 и F3.2 |
| `get`: строка `Links:` | RESOLVED | `_print_issue`: `print("Links: " + "; ".join(links))`; trial строки 2, 3 |
| Направление проверено на тестовой Jira до теста | RESOLVED | trial-1.4.0: «`inwardIssue` = KEY, `outwardIssue` = KEY2 gives "KEY blocks KEY2"» |
| Тесты | RESOLVED | `Ran 107 tests … OK` |
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

Ни одно правило не потеряно.

## Пропущено ранее

Нет.

## Оставлено планом

Ничего: «Leave: none».

## Вопросы к человеку

1. Правило `derived` (F5.1): ставить связь «всегда при создании задачи из другой», без
   просьбы, или только когда роль, шаг или человек просят? Рекомендую второе — это
   соответствует общему правилу записи; формулировка в F5.1.
