# Отчёт о ките: tracker-jira-server 1.2.0

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-whoami`), путь задан
- Коммит: 8aeda44 (`kit.yaml` `version: 1.2.0`). Визит 1 оценивал 65946fd (отчёт d6590ef).
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.1.0-2026-10-09.md`
  (полная оценка, b3e0aec). База — b3e0aec, её называет план. Дифф
  `git diff b3e0aec -- kit.yaml README.md BLUEPRINT.md agents flows skills` затрагивает
  5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md,
  skills/tracker/jira.py.
- Визит 2 шага `evaluate`, после отклонения на гейте выпуска. С визита 1 (65946fd → 8aeda44)
  изменились:
  - `jira.py`: совет после сбоя комментария, проверка держателя по `name` или `key`,
    снятие исполнителя при 404;
  - SKILL.md: показ аккаунтов и строки не от `jira.py`;
  - BLUEPRINT: строка решения триажа 2026-10-08;
  - `.gitignore`, `.pyc` убран из индекса;
  - тесты: 88.
- Проходы визита 2. Изменение — около 30 строк, три прохода я сделал сам, по 12 критериям
  и известным дырам:
  1. ветки совета в `cmd_transition` против таблицы кодов SKILL.md и R8;
  2. новые абзацы SKILL.md против кода (`_person`, `main`);
  3. `cmd_assign` и правка BLUEPRINT против R3 и решения на гейте.

  Новых находок эти проходы не дали. Затем был полный проход (Re-evaluation 5) по всем
  пяти файлам целиком. Его сделал отдельный субагент без `kit-reports/` и без переменных
  `JIRA_*`, пробы шли против фейковой Jira. Он дал 3 находки и одну строку для «Not
  traced», все в тексте 8aeda44. Каждую я подтвердил по файлам («full pass, confirmed»).
  Однопроходных находок отброшено: 0.
- Проходы визита 1: см. историю этого файла в git (d6590ef).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений; `expects commands: uv` |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 3 открытые находки (0 high, 1 medium, 2 low); все 7 находок визита 1 RESOLVED; 10 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 88, OK |
| Правило остановки | не выполнено: 0 high, 1 medium (F5.5). Это совет к гейту выпуска, а не блокировка |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
expects commands: uv
```

Expects: `expects commands: uv`. Предупреждения `expects.commands needs LADO 0.30 or newer`
нет: `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.2.0

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

У кита нет потоков (R2) и нет скелетов, поэтому сравнивать нечего. Скрипт потоков такой кит
не обрабатывает. Причина вне кита (см. «Found on the way»), так что на решение это не
влияет:

```
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. SKILL.md:123-124: «nothing reached Jira» — только для сообщений uv и «can't open
   file». Трассировка Python — это падение скрипта (код 1, строка 1 таблицы): запись
   могла пройти (F5.5).

## Находки

Нумерация продолжает визит 1: F3.1, F3.2, F5.1–F5.4 и F12.1 закрыты (см. «Previous
findings»). Новые находки — F3.3, F3.4, F5.5.

### 1. Границы ролей

Не применимо: ролей нет. Область записи SKILL.md:26-28 не менялась; `--reassign` — только
«when the human or your step says to take it from them» (SKILL.md:71).

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.3** [low] `skills/tracker/jira.py:822`
  > if failure.status != 404 else "404"))
  Снятие исполнителя с ответом 404 теперь печатает «Jira refused to unassign T-1: 404»
  с кодом 11 и теряет причину: задачи нет или она не видна. Строка 11 велит «fix the
  request once», но чинить нечего, и агент тратит попытку.
  Fix: «Jira refused to unassign %s: the task is gone or not visible to you (404)», или
  оставить `failure.message` (`missing_issue`) с кодом 7.
  Passes: full pass, confirmed — `jira.py:819` `if failure.code in (NOT_FOUND, REFUSED):`
  переводит 404 (NOT_FOUND) в REFUSED с текстом «404». Это ответ на F3.2 визита 1: ложное
  «check the key» ушло, но причину сообщение теперь не называет.

- **F3.4** [low] `skills/tracker/jira.py:753`
  > advice = "send the comment with comment"
  Если Jira отвергла сам комментарий (код 11, например «comment (too long)»), совет —
  отправить его снова как есть. Тот же текст упадёт ещё раз. Комментарий в коде
  (`jira.py:742-743`, «only a refused comment is fixed and sent again at once») говорит
  «fix», а сообщение — нет.
  Fix: «fix the text the line names, then send the comment with comment».
  Passes: full pass, confirmed. Проба: `… the comment was not added (do not run the transition again; send the comment with comment): Jira refused the values: comment (too long)`.
  Совет был тем же и в 1.1.0, но ветка переписана в 8aeda44, поэтому находка здесь.

### 4. Независимая проверка

Не применимо: потоков нет. 88 тестов, OK. Пробы на тестовой Jira для 1.2.0 ещё не было
(вопрос 2).

### 5. Противоречия

- **F5.5** [medium] `skills/tracker/SKILL.md:124`
  > nothing reached Jira: if it says it cannot open `jira.py`, fix the path (see above);
  Абзац относит к uv или Python каждое сообщение, которое не начинается с `jira.py`, и
  говорит, что в Jira ничего не ушло. Но падение самого скрипта печатает трассировку
  Python («Traceback …»), а она тоже не начинается с `jira.py`. `main` ловит только
  `Failure` (`jira.py:963` `except Failure as failure:`). Падение может случиться после
  записи. Тогда этот абзац спорит со строкой 1 таблицы и со SKILL.md:147
  («after exit 1 or a 5xx exit 12 … `get` or `search` before running it again»). Агент
  может повторить `create` или `comment` без проверки и сделать дубль.
  Fix: «a Python traceback is the script crashing: exit 1, a write may have been applied
  (see row 1)»; «nothing reached Jira» оставить только для сообщений uv и «can't open
  file».
  Passes: full pass, confirmed. Проба на фейковой Jira: `POST issue` ответил 201 с телом
  `[]`, скрипт вышел с кодом 1 и трассировкой
  `AttributeError: 'list' object has no attribute 'get'`; запрос `POST /rest/api/2/issue`
  записан. Формулировку «nothing reached Jira» предложил мой Fix к F3.1 визита 1. Ошибка
  в моём совете, а не в исполнении.

Показ аккаунтов (SKILL.md:64-67) совпадает с кодом: «or the login alone when Jira has no
other name», «Reporters and comment authors show only their name».

### 6. Дублирование

Правило assign стоит в SKILL.md:68-71 и в строке 11. Его требует R8, копии совпадают.
Нарушения нет.

### 7. Когда звать человека

После сбоя комментария при кодах 4, 5, 6, 7, 10 и 429 совет — «report it; send the comment
with comment once you are told to» (`jira.py:755`). При коде 5 он согласован с остановкой
всех агентов. Нарушения нет.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

Новые ветки объяснены комментарием `jira.py:742-743`. Нарушения нет (о расхождении
комментария с сообщением см. F3.4).

### 10. Описания навыков

Без изменений с визита 1: описание называет `whoami` по смыслу; `uv` в `expects.commands`.

### 11. Нейтральность к провайдеру

Без изменений: `${SKILL_DIR}` с запасным путём, `uv` не привязан к CLI.

### 12. Безопасность и границы

Проверка держателя читает `name` или `key` (`jira.py:800`), так что задача, у исполнителя
которой есть только `key`, считается чужой и без `--reassign` не берётся. Крайний случай:
своя задача, известная только по `key`, тоже будет отвергнута. Это безопасная сторона, и
Jira Server всегда присылает `name`, поэтому не находка.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Не применимо: потоков нет. Сообщения uv отделены от ошибок скрипта; трассировку Python правило относит к окружению — F5.5. |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Чужую задачу можно забрать только с `--reassign` по слову человека или шага (SKILL.md:71). |
| 3. Path outside the run's worktree | `${SKILL_DIR}`; `.lado/tracker.yaml` ищется до первого `.git`. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: ни `dependencies.skills`, ни ролей. |
| 6. Commands out of step with `expects.commands` | (a) `uv` — единственная команда, которую кит запускает всегда: `expects commands: uv`, README:21 требует только его. (b) `uv` нужен на любом проекте. (c) `dependencies.lado: ">=0.30"`, у `lado kits check` нет предупреждения. |

## Not traced

- Журнал 1.2.0 (BLUEPRINT.md:239) и R8 (BLUEPRINT.md:113-116) не записывают правки
  8aeda44:
  > advice after a failed comment keeps the rules of 9 and 429 (F5.3)

  Не записаны: «сначала сообщить» после кодов 4, 5, 6, 7 и 10; 404 при снятии
  исполнителя; держатель по `name` или `key`; правило о сообщениях uv и Python.
  Совет: дописать их в строку 1.2.0 со ссылкой на отчёт d6590ef и расширить фразу R8.
- В остальном всё прослежено, как на визите 1: `uv` — «command (expects)», R3/R5/R8/R9
  описывают новое поведение. Строка решения триажа теперь называет исключение для assign
  (BLUEPRINT.md:166-167).

## Previous findings

Находки визита 1 (d6590ef). Находки полной оценки b3e0aec закрыты на визите 1 и с тех пор
не менялись.

| Находка | Статус | Доказательство |
|---|---|---|
| F5.1 [medium] совет «send the comment» при 5/6/7/10 | RESOLVED | `jira.py:753-755`: «send the comment with comment» только при `failure.code == REFUSED`, иначе «report it; send the comment with comment once you are told to». Проба полного прохода: 401, 403, 404, 429 → «report it first». Остаток при коде 11 — F3.4 |
| F5.2 [medium] «an account as Name (login)» | RESOLVED | SKILL.md:64 «**get** and **search** show the assignee, and **whoami** your account, as»; «Reporters and comment authors show only their name» |
| F3.1 [medium] строка не от `jira.py` | RESOLVED | SKILL.md:123-126: путь к `jira.py`, «its exit 2 is not wrong arguments», «report all of it». Новое противоречие с трассировкой — F5.5 |
| F3.2 [low] 404 при снятии → «check the key» | RESOLVED | `jira.py:819-822` → «Jira refused to unassign … 404», код 11. Потеря причины — F3.3 |
| F5.3 [low] логин без скобок | RESOLVED | SKILL.md:65 «or the login alone when Jira has no other name» |
| F5.4 [low] BLUEPRINT:167 «others' tasks» | RESOLVED | BLUEPRINT.md:167 «except taking another account's task in `assign` (R3,» |
| F12.1 [low] держатель только по `name` | RESOLVED | `jira.py:800` `current = (holder or {}).get("name") or (holder or {}).get("key")` |
| Попутно: `.pyc` в индексе | RESOLVED | `git ls-files \| grep -c pycache` → 0; `.gitignore` `__pycache__/`, `*.pyc` |

Список «fixed / not fixed» в build-report сверен с файлами и совпадает. Своя задача без
`--reassign` оставлена, как решил человек на гейте.

## Cut rules

Удалённые строки визита 2 (`git diff --word-diff d6590ef`):

| Удалённое правило (файл:строка в d6590ef) | Где теперь |
|---|---|
| SKILL.md:64 «**get**, **search**, **whoami** show an account as» | SKILL.md:64-66, сужено до исполнителя и `whoami` (F5.2) |
| SKILL.md:122-123 «comes from `uv` … treat it as exit 1» | SKILL.md:123-126: «treat it as exit 1 and report all of it» сохранено (с F5.5) |
| `jira.py` 429 → «report it; send the comment with comment once you are told to» | `jira.py:755`, ветка `else` (429 — SERVER_ERROR, не `unsure`) |
| `jira.py` `check if unsure else "send the comment with comment"` | `jira.py:750-753`, разделено |
| `jira.py` `login is None and … == REFUSED` | `jira.py:819`, расширено на NOT_FOUND |
| BLUEPRINT «others' tasks);» | BLUEPRINT.md:167, с исключением |

Правил не потеряно. Удалённые правила визита 1 — см. d6590ef, там тоже ничего не
потеряно.

## Missed earlier

Нет. Полный проход не нашёл находок в тексте, которого не касается дифф.

## Left by the plan

Нет: план ничего не оставляет («Leave: none»).

## Questions for the human

1. F5.5 (medium) не блокирует выпуск. Исправление — одно предложение в SKILL.md:
   трассировка Python — это код 1, запись могла пройти. Рекомендую исправить сейчас,
   вместе с F3.3 и F3.4 (по одной строке) и строкой журнала. Без этого агент после редкого
   падения скрипта может повторить запись и сделать дубль.
2. Проба на тестовой Jira 8.13 (`whoami`, `/rest/api/2/myself`, отказ `assign`, запуск
   через `uv` в сессии LADO) до выпуска — по-прежнему рекомендую.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
- На визите 1 один субагент-проход сделал одно чтение `whoami` к настоящей Jira. На этом
  визите пробы шли без `JIRA_*`, только против фейковой Jira.
