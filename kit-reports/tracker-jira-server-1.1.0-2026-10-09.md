# Отчёт о ките: tracker-jira-server 1.1.0

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-whoami`), путь задан
- Коммит: d13ca96 (текст кита тот же, что в 9308f1c; `kit.yaml` `version: 1.1.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: полная оценка, шаг `assess`. Прежний отчёт этого файла (d13ca96) — повторная
  оценка, а не полная: в его таблице «Known holes» нет дыры 6 (`expects.commands`).
  Поэтому он только фон, кит оценён заново.
- Проходы: три независимых субагента, каждому дали рубрику, `lado-kit-format` и папку кита,
  без `kit-reports/`. Начала проходов:
  - проход 1: kit.yaml, README, BLUEPRINT (из-за ошибки в задании субагент выбрал начало
    сам и начал с kit.yaml);
  - проход 2: `jira.py`, команда за командой, с пробами против фейковой Jira из тестов;
  - проход 3: SKILL.md глазами агента процессного кита.

  Однопроходных находок отброшено: 0. Оставлено как подтверждённые: 5 (F3.1, F5.3, F5.5,
  F9.1, F12.1), каждая с моей проверкой по файлам. Тесты: 80, OK. `lado` 0.31.0.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 9 находок (0 high, 5 medium, 4 low); 7 из 12 критериев без находок |
| Охват | полная оценка всего кита, 5 файлов: kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

Expects: нет: ни одной строки `expects …`, потому что в `kit.yaml` нет `expects` (см. F10.1).

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.1.0

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
не обрабатывает (см. «Found on the way»):

```
$ uv run --script flow_diagram.py . --out kit-reports/tracker-jira-server-1.1.0-2026-10-09
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. Добавить в `kit.yaml` `expects.commands: [python3]` и `dependencies.lado: ">=0.30"`,
   а в BLUEPRINT раздел 3 — python3 как «command (expects)» (F10.1).
2. Дать действие «кто я» (логин и отображаемое имя) и показывать в `get`/`search`
   исполнителя с логином (F5.2).
3. Не давать `assign … me` молча забирать задачу у другого человека: отказ или явное
   правило в SKILL.md (F12.1).
4. Строка 11 таблицы кодов: для `assign` «сообщить, другой логин не пробовать» (F5.1).
5. Сообщение о сбое комментария после перехода: учитывать правило ожидания кодов 9 и 429
   (F5.3, прежняя F5.4).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Права записи навыка заданы в одном месте, SKILL.md:26-28:
«Reading is always fine. Create, transition, comment, assign, label or link only when your role, your».

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.1** [low] `skills/tracker/jira.py:788`
  > if failure.status == 404 or failure.code == REFUSED:
  Проверка смотрит на HTTP-статус, а не на код скрипта. Поэтому сообщение о неизвестном
  пользователе получают два случая, где его быть не должно:
  - `assign KEY none` с ответом 404 (задача исчезла между GET и PUT) печатает «refused to
    assign … to unassigned: no such user»;
  - 404 не от Jira (код 4) становится кодом 11 «no such user».

  Агент и человек ищут не ту причину.
  Fix: проверять `login is None` раньше этой ветки, а «no such user» давать только при
  `failure.code in (NOT_FOUND, REFUSED)`. Passes: 1/3, confirmed. Ветка отказа снять
  исполнителя стоит выше и ловит только код 11:
  `jira.py:785` `if login is None and failure.code == REFUSED:`. Проба прохода 2:
  `11 … Jira refused to assign A-1 to unassigned: no such user, or the user cannot be assigned in this project (404)`.
  Это прежние F3.3 и F3.4.

### 4. Независимая проверка

Не применимо: потоков нет. `comment` печатает id комментария, `get` показывает те же id,
так что агент может проверить свою запись (SKILL.md:60-62).

### 5. Противоречия

- **F5.1** [medium] `skills/tracker/SKILL.md:132`
  > | 11 | Jira refused the request (bad JQL, a refused field value, unknown type, transition not open) | read the line, fix the request once; if it still fails, report it |
  Для `assign` код 11 означает неизвестный логин. Единственная «правка» запроса здесь —
  другой логин, а именно это запрещает SKILL.md:63. Агент, который действует по таблице,
  попробует другой логин; агент, который действует по пункту об assign, сообщит.
  Fix: в строке 11 дописать «(`assign`: report it, never try another login)».
  Passes: 2/3 (проходы 1 и 3). Проход 2 счёл это оговоркой, а не противоречием, и цитирует
  вторую сторону: `SKILL.md:63`
  `- **assign**: use only a login you were given; on exit 11 report it and do not try`.

- **F5.2** [medium] `skills/tracker/jira.py:529`
  > return value.get("displayName") or value.get(attr) or value.get("key") or "?"
  `get` и `search` показывают исполнителя по отображаемому имени, а `assign` берёт и
  печатает логины. Действия «кто я» нет, а SKILL.md:21-22 запрещает агенту печатать
  `JIRA_USER`. Агент не может отличить «задача моя» от «задача чужая». Он либо гадает
  (и может переназначить чужую задачу), либо зовёт человека без нужды. Задача без
  исполнителя показана как `Assignee: -`, а не словом.
  Это пункты 1–2 требований `tracker-requirements-690cd7a8.md` (F5.1 отчёта sdlc 0.3.0).
  Fix: действие `whoami` (GET `/rest/api/2/myself`: логин и отображаемое имя). В `get` и
  `search` печатать `Display Name (login)` и «unassigned». В SKILL.md одна строка:
  «чтобы узнать, твоя ли задача, сравни логин из `get` с `whoami`». В BLUEPRINT поправить
  R3 («Nothing else (no delete, user search, …)») и R5 («the login of `JIRA_USER` appears
  only as an assignee in `assign`'s output»).
  Passes: 2/3 (проход 1 — low, критерий 3; проход 3 — medium, критерий 5). Взяты medium
  и критерий 5: исправление снимает расхождение между `get` и `assign`.

- **F5.3** [medium] `skills/tracker/jira.py:732`
  > "check with get, then send the comment with comment if it is not there"
  Комментарий после перехода может не дойти. Тогда сообщение скрипта даёт указание,
  которое спорит с правилом ожидания из сообщения самой ошибки:
  - при коде 9 оно велит сразу «check with get», а вложенное сообщение и SKILL.md:130
    говорят «send Jira nothing more until you are told it answers again»;
  - при 429 оно велит «send the comment with comment» (`jira.py:733`), а вложенное
    сообщение говорит «report it, do not retry».

  Одни агенты сразу обращаются к недоступной или ограничивающей Jira, другие сообщают.
  Fix: для кода 9 — «once you are told Jira answers again, check with get…»; для 429 —
  «report it; send the comment with comment once you are told to».
  Passes: 1/3, confirmed. Вторая строка той же ветки: `jira.py:733`
  `if unsure else "send the comment with comment", failure.message))`.
  Проба прохода 2 для кода 9:
  `A-1: Open -> In Progress done, but the comment may not have been added (do not run the transition again; check with get, …): Jira is not reachable …; send Jira nothing more until you are told it answers again`.
  Часть про 429 — прежняя F5.4 (запуск в отчёте d13ca96).

- **F5.4** [low] `skills/tracker/SKILL.md:42`
  > | link a branch, commit or pull request | `link KEY-1 <url> [--title '<text>']` |
  SKILL.md и справка скрипта предлагают ссылки на pull request, а R3 говорит только «link
  a branch or commit URL» (BLUEPRINT.md:37). Описание в `kit.yaml` «label and link tasks»
  читается как связи между задачами, которых кит не делает. Это расхождение формулировок.
  Fix: назвать pull request в R3; в `kit.yaml` написать «link a branch or commit to tasks».
  Passes: 2/3 (проходы 1 и 2). Не путать с прежней F5.4: та теперь в F5.3.

- **F5.5** [low] `README.md:47`
  > refuses a `JIRA_URL` that is not `https://`, since the password goes with every request.
  Скрипт принимает и `http://` на loopback (для тестов), но README, R5 и R7 этого не
  говорят. Вреда почти нет: loopback не покидает машину.
  Fix: «(or `http://` to localhost, for tests)» в README и R7.
  Passes: 1/3, confirmed: `jira.py:253`
  `if not (url.scheme == "https" or (url.scheme == "http" and url.hostname in LOOPBACK)):`.

### 6. Дублирование

Проверены README:76-79 и SKILL.md:26-28 (область записи): README только указывает на
SKILL.md. Правило остановки по коду 5 нарочно повторено в сообщении скрипта и в SKILL.md
(R8: его должен узнать и лидер без навыка). Нарушения нет.

### 7. Когда звать человека

SKILL.md:115-118: «as a worker, send the supervisor that line and the command with `send_message`;
as the lead, tell the human». Там же правило «ждать или продолжать». У кодов 5 и 9 есть
правила остановки. Нарушения нет. О решении «забрать чужую задачу» см. F12.1.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

- **F9.1** [low] `skills/tracker/SKILL.md:62`
  > `transition --comment` prints no id, find your `[LADO: …]` comment in `get`.
  Скрипт отправляет метку экранированной, `\[LADO: …\]`, а `get` печатает тело как есть.
  Агент, который ищет буквально `[LADO:`, свой комментарий не найдёт.
  Fix: «find your `\[LADO: …\]` comment in `get`, as Jira keeps it».
  Passes: 1/3, confirmed: `jira.py:504` `label = "\\[LADO: %s\\]" % agent`; `get` печатает
  `comment.get("body")` без изменений (`jira.py:565`).

### 10. Описания навыков

- **F10.1** [medium] `kit.yaml:8` (known hole 6a)
  > lado: ">=0.27"
  Навык всегда запускает `python3` (SKILL.md:17
  `python3 ${SKILL_DIR}/jira.py <command> ...      # --help on any command`), README:21
  требует его для каждого проекта, а в `kit.yaml` нет `expects.commands`. Поэтому сессия
  без `python3` в PATH агентов стартует. Первое же действие трекера падает с
  «command not found» (127), а такого кода в таблице SKILL.md нет. BLUEPRINT раздел 3
  не называет python3 «command (expects)».
  Fix: в `kit.yaml` добавить `expects: {commands: [python3]}` и поднять
  `dependencies.lado` до `">=0.30"`; README:21 уже требует python3. В BLUEPRINT раздел 3
  добавить строку `python3` как «command (expects)», а в строку `kit.yaml` — `expects`.
  Passes: 3/3.

Описание навыка говорит, что он умеет и когда его звать («Use whenever your work touches a
task in the tracker»). Соседних и зависимых навыков нет.

### 11. Нейтральность к провайдеру

Скрипт вызывается через `${SKILL_DIR}`, и для CLI без этой подстановки есть запасной путь
(SKILL.md:20 «If your CLI does not expand `${SKILL_DIR}`, use the folder this SKILL.md is in»).
Инструментов одного CLI нет; абсолютных и домашних путей в навыке и скрипте нет.
Нарушения нет.

### 12. Безопасность и границы

- **F12.1** [medium] `skills/tracker/SKILL.md:40`
  > | assign a task | `assign KEY-1 <me \| login \| none>` (`none` unassigns) |
  В описании навыка есть триггеры «take the task», «assign it to me» (SKILL.md:7). Они
  ведут к `assign KEY me`, и эта команда молча забирает задачу у того, кто её держит.
  Скрипт сравнивает текущего исполнителя только с целевым логином
  (`jira.py:774` `if (current or "").lower() == (login or "").lower():`). Ни одно правило
  не говорит, что забрать чужую задачу — решение человека. Запись идёт от имени
  пользователя.
  Это пункт 3 требований `tracker-requirements-690cd7a8.md`.
  Fix: при чужом исполнителе `assign … me` отказывается и называет его (или делает это
  только по флагу вроде `--only-if-free`). В SKILL.md: «on a task held by another
  account, report it; reassign only when you are told to».
  Passes: 1/3, confirmed. Тест ждёт тихого переназначения:
  `tests/test_jira.py:591` `self.assertEqual(out, "TEST-1: assignee ann -> agent.user\n")`.
  Проход 3 дал high. Я снизил до medium: переназначение легко отменить, а R11 уже
  ограничивает запись тем, о чём попросили.

Остальное: удаления нет, неверный пароль не повторяется, пароль идёт только по https (и
на loopback, F5.5), проверку TLS не отключить.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Не применимо: потоков нет. Таблица кодов отделяет сбои окружения (3, 4, 5, 9, 10, 12) от ошибок запроса (2, 8, 11). Неточность: 404 не от Jira на assign — F3.1. |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Запись в Jira — по SKILL.md:26-28 «only when your role, your step or the human asks for it»; пробел с чужой задачей — F12.1. |
| 3. Path outside the run's worktree | `${SKILL_DIR}`; `.lado/tracker.yaml` ищется от текущей папки вверх до первого `.git` (в worktree это файл, `jira.py:196`). |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: ни `dependencies.skills`, ни ролей. |
| 6. Commands out of step with `expects.commands` | (a) F10.1: `python3` всегда запускается и требуется в README, но его нет в `expects.commands`. (b) нет: `expects.commands` пуст. (c) пока не применимо; при исправлении F10.1 нужно `dependencies.lado: ">=0.30"`. |

## Not traced

- Каждый файл кита назван требованием (BLUEPRINT раздел 3). Бюджет green, скелетов нет —
  потоков нет (R2), BLUEPRINT.md:162 это говорит.
- `python3` как обязательная команда не назван ни в R4, ни в разделе 3 как «command
  (expects)» (F10.1).
- Pull request в `link` и `--title` не названы в R3 (F5.4).
- Подстановка `{project}` в JQL `search` (SKILL.md:47) не названа в R3.
- `http://` на loopback расходится с R5/R7 (F5.5).
- R5 против кода: `_name` показывает логин в `get`/`search`, когда у пользователя нет
  `displayName`. Это крайний случай, не находка; при исправлении F5.2 R5 меняется всё
  равно.
- Порядок требований: R11 и R12 стоят перед R10. Это косметика.

## Questions for the human

1. F5.2 и F12.1 — это требования из `tracker-requirements-690cd7a8.md`, пункты 1–2 и 3.
   Делать ли и пункт 3 (необязательный): `assign … me` отказывается при чужом исполнителе?
   Рекомендую да. Это одна проверка в уже имеющемся GET, и тогда sdlc может просто
   просить «назначь на себя, если свободна».
2. F5.3 (бывшая F5.4) сейчас шире: кроме 429 она касается и кода 9. Исправлять в этой
   версии? Рекомендую да: правка — одна строка формирования сообщения, и она закрывает
   открытую medium.
3. Low-находки F3.1, F5.4, F5.5, F9.1: исправлять заодно? Рекомендую F3.1 и F9.1 да (они
   сбивают агента); F5.4 и F5.5 — только текст BLUEPRINT/README, по желанию.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2) и для `--out`, и
  для `--compare`. Всё ещё открыто.
- `[kit-builder]` Шаг `assess` говорит взять готовый «full report … with a "Known holes"
  table». Отчёт 1.1.0 был повторной оценкой, и в его таблице нет дыры 6, добавленной в
  рубрику позже. Условие шага не говорит, что таблица должна покрывать все текущие дыры.
