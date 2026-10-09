# Отчёт о ките: tracker-jira-server 1.2.0

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-whoami`), путь задан
- Коммит: 65946fd (`kit.yaml` `version: 1.2.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.1.0-2026-10-09.md`
  (полная оценка, b3e0aec). База — b3e0aec, её называет план. Дифф
  `git diff b3e0aec -- kit.yaml README.md BLUEPRINT.md agents flows skills` затрагивает
  5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md,
  skills/tracker/jira.py. Визит 1 шага `evaluate`.
- Проходы: три независимых субагента по изменённому тексту и его окружению. Каждому дали
  рубрику, `lado-kit-format`, папку кита и дифф, без `kit-reports/`. Начала проходов:
  - проход 1: kit.yaml и README;
  - проход 2: `jira.py`, с пробами против фейковой Jira из тестов;
  - проход 3: SKILL.md глазами агента процессного кита (sdlc).

  Затем полный проход (Re-evaluation 5) по всем пяти файлам целиком, четвёртым субагентом.
  Проверку удалённых правил (`git diff --word-diff`) я сделал сам. Однопроходных находок
  отброшено: 2 — повтор правила assign в строке 11 (так требует R8, два прохода сочли это
  указателем) и длинная строка описания SKILL.md:6. Оставлено как подтверждённые: 4
  (F3.2, F5.3, F5.4, F12.1). Тесты: 86, OK.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений; `expects commands: uv` |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 7 открытых находок (0 high, 3 medium, 4 low); все 9 находок прежнего отчёта RESOLVED; 8 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py) |
| Правило остановки | не выполнено: 0 high, 3 medium (F3.1, F5.1, F5.2). Это совет к гейту выпуска, а не блокировка |

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

1. Сбой комментария после перехода с кодом 5, 6, 7 или 10: не советовать сразу «send the
   comment with comment», а «report it; send the comment with comment once you are told
   to» (F5.1).
2. SKILL.md:64: «show the assignee as `Display Name (login)`», а не «an account» (F5.2).
3. Правило о строке не от `jira.py`: назвать неверный путь к скрипту, многострочную ошибку
   uv и её код выхода 2 (F3.1).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Область записи SKILL.md:26-28 не менялась; `--reassign` — только
«when the human or your step says to take it from them» (SKILL.md:70).

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.1** [medium] `skills/tracker/SKILL.md:122`
  > not start with `jira.py` or `usage: jira.py` comes from `uv`, which runs the script (it
  Правило приписывает uv каждую строку не от скрипта, и при этом считает, что она одна.
  Три прохода нашли три способа ошибиться:
  - неверный путь к `jira.py` (CLI не подставил `${SKILL_DIR}`) печатает строку Python
    «can't open file». Агент сообщает её как код 1, вместо того чтобы взять путь из
    SKILL.md:20;
  - ошибка uv бывает многострочной (`error: Failed to initialize cache …` и
    `Caused by: … Permission denied`), а строка 1 таблицы велит «report its last line»;
  - uv выходит с кодом 2, тем же, что «wrong arguments» в таблице. Об этом правило
    молчит, так что агент, который смотрит в таблицу, «чинит» верную команду.

  Fix: «A line that does not start with `jira.py` comes from `uv` or Python, not the
  script: if it says it cannot open `jira.py`, fix the path (see above); otherwise (uv
  could not get Python or write its cache, exit 2) treat it as exit 1 and report all of
  it; nothing reached Jira.»
  Passes: 3/3. Проход 3 дал medium, проходы 1 и 2 — low, по разным частям; взят medium.
  Полный проход нашёл то же про путь. Проба:
  `uv run --quiet --script /nope/jira.py whoami` → `…/python3.12: can't open file '/nope/jira.py': [Errno 2] No such file or directory`, код 2.

- **F3.2** [low] `skills/tracker/jira.py:815`
  > if login is None:
  Снятие исполнителя (`assign KEY none`) с ответом 404 на PUT теперь пробрасывает
  исходный сбой: код 7, «task … not found (404): check the key». Но GET выше только что
  нашёл задачу. Ложного «no such user» больше нет (прежняя F3.1), однако агента теперь
  посылают проверять верный ключ.
  Fix: 404 здесь превращать в REFUSED «Jira refused to unassign %s».
  Passes: 1/3, confirmed. Сообщение берётся из `jira.py:529`
  `return "task %s not found (404): check the key, or you may not see it" % key`.
  Проба прохода 2: `('assign','TEST-1','none') exit 7 | jira.py: task TEST-1 not found (404): check the key`.

### 4. Независимая проверка

Не применимо: потоков нет. 86 тестов, OK. Пробы на тестовой Jira для 1.2.0 ещё не было
(см. вопрос 3).

### 5. Противоречия

- **F5.1** [medium] `skills/tracker/jira.py:752`
  > advice = check if unsure else "send the comment with comment"
  Правка прежней F5.3 учла правило ожидания только для кодов 9 и 429. Если комментарий
  после перехода упал с кодом 5 (пароль отвергнут или CAPTCHA), 6, 7 или 10, совет всё
  ещё «send the comment with comment». При коде 5 та же строка дальше говорит, что все
  агенты прекращают работу с Jira, а SKILL.md:134 предупреждает «one more try can lock
  the login». Агент, который послушает первую половину строки, сделает ещё одну попытку
  входа. Комментарий в коде (`jira.py:742`, «The advice keeps the failure's own rule»)
  обещает больше, чем делает код.
  Fix: «send the comment with comment» только при `failure.code == REFUSED`; при любом
  другом коде — «report it; send the comment with comment once you are told to».
  Passes: 2/3 (проходы 1 и 2), и полный проход. Проба:
  `CODE 5 … done, but the comment was not added (do not run the transition again; send the comment with comment): Jira refused the login and wants a CAPTCHA … the lead tells every agent to stop using Jira`.

- **F5.2** [medium] `skills/tracker/SKILL.md:64`
  > - **get**, **search**, **whoami** show an account as `Display Name (login)`, a task with
  В виде `Display Name (login)` печатается только исполнитель. Автор задачи и авторы
  комментариев идут через `_name` и печатаются только отображаемым именем
  (`jira.py:563` `_person(fields.get("assignee")), _name(fields.get("reporter"))))`).
  Агент, которому велено «верни задачу автору», передаст в `assign` отображаемое имя,
  получит код 11 и потеряет шаг. Сравнить автора комментария с `whoami` он тоже не может.
  Fix: «show the assignee as `Display Name (login)`», как в R3 (BLUEPRINT.md:44).
  Печатать логин автора задачи нельзя: R5 разрешает логин `JIRA_USER` только как
  исполнителя.
  Passes: 2/3 (проход 1 — low, проход 2 — medium; взят medium), и полный проход.
  Проба: `Assignee: Ann Lee (ann)   Reporter: Bob Ray`.

- **F5.3** [low] `skills/tracker/jira.py:546`
  > return login or name or "?"
  Если у пользователя нет отображаемого имени или оно равно логину, печатается один логин,
  без скобок. Агент, которому SKILL.md:64 велит брать «логин в скобках», скобок не найдёт.
  В `search` исполнитель вдобавок оказывается во вложенных скобках:
  `summary  (John Doe (jdoe))` (`jira.py:603`).
  Сравнение всё равно работает: обе стороны идут через `_person`.
  Fix: в SKILL.md:64 добавить «or the login alone when Jira has no other name».
  Passes: 1/3, confirmed: `jira.py:603`
  `fields.get("summary"), _person(fields.get("assignee"))))` внутри формата `"(%s)"`.

- **F5.4** [low] `BLUEPRINT.md:167`
  > closing tasks, others' tasks); the kit has no delete, and a process kit may set its own
  Решение триажа 2026-10-08 «no limits for agents beyond R11 (deletes, closing tasks,
  others' tasks)» теперь спорит с R3 1.2.0: `assign` отказывается брать задачу другого
  аккаунта без `--reassign`. Следующий автор может прочесть это как разрешение убрать
  отказ.
  Fix: дописать «except taking another account's task in `assign` (R3, 1.2.0)».
  Passes: 1/3, confirmed: `BLUEPRINT.md:36` «a task held by another account is refused
  with that account named, unless». Строка не изменена диффом, но противоречие создаёт
  изменение, поэтому находка здесь, а не в «Missed earlier».

### 6. Дублирование

Правило «не пробуй другой логин и `--reassign`» стоит в SKILL.md:67-70 и в строке 11
(SKILL.md:140). Второе место требует R8, а копии совпадают. Это указатель, нарушения нет.

### 7. Когда звать человека

Отказ при чужой задаче называет держателя и говорит «report it, and add --reassign only
when the human or your step says to take it from them» (`jira.py:804-806`); путь
сообщения — SKILL.md:124-126. Нарушения нет.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

Новые правила несут причину: `jira.py:800` «Taking a task from another account is the
human's decision, never a side effect.»; SKILL.md:68 «since a guess may assign the task
to someone else». Нарушения нет.

### 10. Описания навыков

Описание называет новое действие по смыслу: «say which account you work as» (SKILL.md:6);
в таблице действий — «see which account you work as | `whoami`». `uv` есть в
`expects.commands`, а `dependencies.lado` — `">=0.30"`. Нарушения нет.

### 11. Нейтральность к провайдеру

`uv run --quiet --script ${SKILL_DIR}/jira.py`, запасной путь для CLI без `${SKILL_DIR}`
на месте (SKILL.md:20). `uv` не привязан к одному CLI. Нарушения нет.

### 12. Безопасность и границы

- **F12.1** [low] `skills/tracker/jira.py:797`
  > current = (holder or {}).get("name")
  `_person` берёт логин из `name`, а при его отсутствии из `key`. Проверка «чужая задача»
  смотрит только на `name`. Исполнитель без `name` поэтому считается «unassigned», и
  `assign … me` забирает задачу без `--reassign`. Jira Server обычно присылает `name`,
  отсюда low.
  Fix: `current = (holder or {}).get("name") or (holder or {}).get("key")`.
  Passes: 1/3, confirmed: `jira.py:542` `login = user.get("name") or user.get("key")`.
  Проба прохода 2 с `{"key":"JIRAUSER10100","displayName":"Ann"}`:
  `TEST-1: assignee unassigned -> agent.user`, код 0.

`whoami` печатает только `name` и `displayName`; пароль и `JIRA_URL` не печатаются.
Чужую задачу `assign` без `--reassign` не трогает при любой цели, в том числе `none`.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Не применимо: потоков нет. Сбой uv отделён от ошибки запроса правилом SKILL.md:121-123; его пробелы — F3.1. |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Забрать чужую задачу можно только с `--reassign`, «only when the human or your step says to take it from them» (SKILL.md:70). |
| 3. Path outside the run's worktree | `${SKILL_DIR}`; `.lado/tracker.yaml` ищется до первого `.git` (в worktree это файл). Кеш uv лежит вне worktree, но это кеш инструмента, а не файл кита. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: ни `dependencies.skills`, ни ролей. |
| 6. Commands out of step with `expects.commands` | (a) `uv` — единственная команда, которую кит запускает всегда: `expects commands: uv`, README:21 «The agents need `uv` on their PATH». В kit.yaml, README, SKILL.md и `jira.py` `python3` не осталось. (b) `uv` нужен на любом проекте. (c) `dependencies.lado: ">=0.30"`, у `lado kits check` нет предупреждения. |

## Not traced

Ничего:
- `uv` — «command (expects)» в разделе 3, покрывает R4;
- `whoami`, исполнитель с логином и `--reassign` есть в R3;
- логин в `whoami` и у исполнителя, http на localhost — в R5;
- строка 11, «no such user» только для логина, совет после сбоя комментария — в R8;
- `\[LADO: …\]` — в R9;
- журнал 1.2.0 перечисляет все правки;
- раздел 4 совпадает с выводом скрипта (green);
- потоков и скелетов нет (R2).

Расхождение с R8 — в F5.1: R8 описывает совет после сбоя комментария только для 9 и 429.

## Previous findings

| Находка / пункт | Статус | Доказательство |
|---|---|---|
| F10.1 [medium] нет `expects.commands` | RESOLVED | `kit.yaml` `expects:` / `commands: [uv]`, `lado: ">=0.30"`; `lado kits check`: `expects commands: uv` |
| F5.2 [medium] нет «кто я», исполнитель только именем | RESOLVED | `jira.py` `cmd_whoami` «You work as %s»; `get` `_person(fields.get("assignee"))`; `_person` → «unassigned». Остаток — F5.2 (новая) о тексте SKILL.md |
| F12.1 [medium] `assign … me` молча забирает чужую задачу | RESOLVED | `jira.py:803` `if current and current.lower() != mine and not args.reassign:`; тест `test_assign_refuses_a_task_held_by_another_account`. Крайний случай без `name` — F12.1 (новая) |
| F5.1 [medium] строка 11 против правила assign | RESOLVED | SKILL.md:140 «(`assign`: report it, never try another login or `--reassign` on your own)» |
| F5.3 [medium] совет после сбоя комментария (9, 429) | RESOLVED | `jira.py` «once you are told Jira answers again, » и «report it; send the comment with comment once you are told to». Коды 5/6/7/10 — F5.1 (новая) |
| F3.1 [low] ложное «no such user» | RESOLVED | `jira.py` `if failure.code in (NOT_FOUND, REFUSED):` только для логина; `if login is None:` раньше. Остаток при 404 на снятие — F3.2 |
| F5.4 [low] pull request, описание kit.yaml | RESOLVED | R3 «link a branch, commit or pull request URL»; `kit.yaml` «link a branch or commit to tasks» |
| F5.5 [low] http на localhost | RESOLVED | README «(or `http://` to localhost, for tests)»; R5 |
| F9.1 [low] экранированная метка | RESOLVED | SKILL.md:62 «find your `\[LADO: …\]` comment in `get`, as Jira keeps it escaped» |
| Изменение плана: проверить `expects.commands` | RESOLVED | см. дыру 6: `uv` объявлен, README требует только его |

Список «fixed / not fixed» в build-report сверен с файлами и совпадает. Таблица
сокращённого текста там: «None cut».

Есть одно отклонение от плана. План: отказывать, «when the task has an assignee other than
the target (for any target …)». Сборка отказывает только когда держатель — не `JIRA_USER`
(`jira.py:803`): свою задачу агент может передать или снять без `--reassign`. Так же
говорят R3 («a task held by another account») и требование 3 sdlc. Автор назвал это
отклонение сам. Это не находка, а вопрос 1.

## Cut rules

| Удалённое правило (файл:строка в базе b3e0aec) | Где теперь |
|---|---|
| R5 «the login of `JIRA_USER` appears only as an assignee in `assign`'s output» | R5: «only as an account Jira shows anyway: as an assignee (`assign`, `get`, `search`) and in `whoami`» — расширено по плану (F5.2) |
| README:21 «The agents need `python3` (3.9 or newer)» | README:21 «`uv` … finds or installs the Python 3.9 or newer it names»; `jira.py` `requires-python = ">=3.9"` |
| README:42 проверка входа `search 'project = ABC' --max 1` | README:44 `… jira.py whoami` — проверка входа сохранена; доступ к проекту она больше не проверяет, но правило было о входе |
| README:47 «refuses a `JIRA_URL` that is not `https://`» | README:49-50, то же, плюс localhost (F5.5) |
| `jira.py` docstring «the login only as an assignee by assign» | `jira.py:9-11`, как новый R5 |
| `jira.py` ветки assign: `login is None and … REFUSED`, `status == 404 or … REFUSED` | `jira.py:815-825`: снятие отдельно, «no such user» при `NOT_FOUND`/`REFUSED` (F3.1; остаток — F3.2) |
| `jira.py` совет «check with get…» / «send the comment with comment» | `jira.py:745-752`, разделено по кодам (F5.3; остаток — F5.1) |
| R4 «on Python's standard library only» | R4: то же, плюс «run by `uv`» |

Правил не потеряно.

## Missed earlier

Нет. Полный проход не нашёл находок в тексте, которого не касается дифф.

## Left by the plan

Нет: план ничего не оставляет («Leave: none»).

## Questions for the human

1. Своя задача: сборка разрешает агенту передать или снять **свою** задачу без
   `--reassign`, а план говорил «при любом исполнителе, кроме цели». Рекомендую оставить
   как в сборке: так говорят R3 и требование 3 sdlc, а вред от передачи своей задачи
   невелик.
2. Три medium (F5.1, F5.2, F3.1) не блокируют выпуск. Рекомендую исправить их в 1.2.0 до
   выпуска: это три короткие правки текста или сообщения, а F5.1 защищает от лишней
   попытки входа после CAPTCHA. Low (F3.2, F5.3, F5.4, F12.1) — заодно, они по одной
   строке.
3. Новые `whoami` и отказ `assign` — это поведение против живой Jira. Повторить пробу на
   тестовой Jira 8.13 (как `trial-1.1.0`) до выпуска? Рекомендую да, особенно
   `/rest/api/2/myself` и запуск через `uv` в сессии LADO.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
- Вне текста кита: коммит 65946fd добавил в репозиторий
  `tests/__pycache__/test_jira.cpython-312.pyc`, а `.gitignore` нет. Следующий запуск
  тестов изменит отслеживаемый файл, и worktree станет грязным перед выпуском. Совет:
  `git rm --cached` этого файла и `__pycache__/` в `.gitignore`.
- Один субагент-проход запустил `whoami` с переменными `JIRA_*` окружения, и запрос
  ушёл на настоящую Jira. Это одно чтение (`GET /rest/api/2/myself`), ничего не
  записано. В следующих оценках пробы стоит запускать без `JIRA_*`.
