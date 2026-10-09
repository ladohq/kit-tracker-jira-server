# Отчёт о ките: tracker-jira-server 1.1.0

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-1-0`), путь задан
- Коммит: d7cea03 (`kit.yaml` `version: 1.1.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.0.2-2026-10-09.md`
  (полная оценка, артефакт `assessment`). База — 802c099, её называет план.
  `git diff 802c099 -- kit.yaml README.md BLUEPRINT.md agents flows skills` затрагивает
  5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md (+22/−11),
  skills/tracker/jira.py (+96/−7).
- Проходы: три независимых субагента, каждый с дифф-файлом, `kit-rubric`,
  `lado-kit-format` и папкой кита, без `kit-reports/`. Проход 1 начинал с новых функций
  `jira.py`, проход 2 — с BLUEPRINT, проход 3 — с SKILL.md глазами агента процесс-кита.
  Удалённые правила сверил я сам, по `git diff --word-diff` и таблице build-report.
  Однопроходных находок отброшено: 0. Оставлено как подтверждённые: 2 (F6.2, F9.1),
  обе я подтвердил в файлах. Полный проход по затронутым файлам (Re-evaluation 5) не
  делался: открыта high-находка, так что вердикт и без него `changes`. Его нужно сделать на
  следующем визите, перед `approved`.
- Оговорка: F3.1 опирается на коды ответа, описанные в документации Atlassian REST v2
  для `PUT /issue/{key}/assignee`. На тестовой Jira 8.13.19 эти коды не проверялись.
  Как скрипт сопоставляет коды, подтверждено запуском.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 5 находок (1 high, 1 medium, 3 low); 6 находок отчёта 1.0.2 RESOLVED; пункты плана T2–T5 RESOLVED, T1 — кроме F3.1; 8 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста (5 файлов), без полного прохода: вердикт `changes`; тесты: 76, OK |
| Правило остановки | не выполнено: 1 high, 1 medium. Это совет к гейту выпуска, а не блокировка |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

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
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. В `cmd_assign` ответы 401 и 404 на PUT давать как 6 и 11, а не как 5 и 7. До PUT
   задачу уже прочитали с теми же учётными данными. Добавить тесты на 401 и 404 (F3.1).
2. SKILL.md:60: `transition --comment` печатает id не всегда — поправить фразу или печатать
   id (F5.1).

## Находки

### 1. Границы ролей

Ролей нет. Правило записи называет новые действия: SKILL.md:26 «Reading is always fine.
Create, transition, comment, assign, label or link only when your role, your».

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.1** [high] `skills/tracker/jira.py:753` (`cmd_assign`)
  > jira.call("PUT", path + "/assignee", body={"name": login},
  План обещает: нет права назначать — код 6, неизвестный пользователь — код 11. Скрипт даёт
  их, только если Jira ответит 403 и 400, а тесты подставляют именно эти ответы
  (`tests/test_jira.py:690` `status=403`, `:698` `status=400`). Документация Atlassian REST
  v2 для этого запроса называет другие коды: 401 — «does not have permission to assign», 404 —
  «the issue or the user does not exist». Общий разбор (`jira.py:326`
  `if code == 401:`) превращает 401 в код 5. Это значит «учётные данные отвергнуты, все
  агенты перестают работать с Jira», и вся сессия останавливается из-за одного
  отсутствующего права. Опечатка в логине (404) становится «task not found, check the
  key», хотя задачу только что прочитали.
  Fix: в `cmd_assign` ловить сбой PUT. 401 без `X-Authentication-Denied-Reason` →
  `NO_ACCESS` («no permission to assign KEY»). 404 → `REFUSED` с логином в строке:
  задачу только что прочитал GET. Тесты на 401 и 404. В пробу на тестовой Jira добавить
  назначение на несуществующий логин.
  Passes: 3/3 (проход 1 — high, проходы 2 и 3 — medium; взят high: при документированном
  401 сессия теряет Jira целиком). Запуск разбора ошибок:
  ```
  401 -> 5 Jira refused the credentials (401): check JIRA_USER and JIRA_PASSWORD; not retried, since
  404 -> 7 task T-1 not found (404): check the key, or you may not see it
  ```

Остальные новые исходы сверены с планом и тестами:
- метка с пробелом — код 2 до запроса;
- «already so» — код 0 и «nothing changed»;
- `--resolution`/`--field` на задаче в целевом статусе — код 11, ничего не отправлено;
- нечитаемый `SSL_CERT_FILE` — код 10;
- `--comment` закрывает обязательное поле `comment`.

### 4. Независимая проверка

Не применимо: потоков нет. Новые действия покрыты тестами (`test_assign`,
`test_unassign`, `test_assign_already_so_changes_nothing`, `test_label_*`,
`test_no_access_to_assign_or_label`, `test_assign_unknown_user`); 76 тестов, OK. Перед гейтом
выпуска супервизор делает пробу на тестовой Jira (план, «Answers»).

### 5. Противоречия

- **F5.1** [medium] `skills/tracker/SKILL.md:60`
  > - **comment**, **transition --comment**: print the new comment's id; `get` shows the
  Когда на экране перехода есть поле `comment`, комментарий уходит внутри перехода.
  Скрипт тогда печатает только `jira.py:713` `moved += ", comment added"`, без id. Теперь
  так бывает всегда, когда экран требует комментарий (F3.2). Агент процесс-кита сверяет
  запись по id (так задумано в T3), не находит его и может отправить комментарий ещё раз.
  Fix: либо после такого перехода прочитать id нового комментария и напечатать его, либо
  в SKILL.md: «`comment` prints the new comment's id; so does `transition --comment` when
  it posts the comment separately; otherwise find your `[LADO: …]` comment in `get`».
  Passes: 3/3. Подтверждено тестом: `tests/test_jira.py:466` ждёт
  `"TEST-1: In Progress -> Done, comment added"`.

### 6. Дублирование

- **F6.1** [low] `BLUEPRINT.md:162`
  > | `skills/tracker/jira.py` | skill script | R3, R4, R5, R6, R7, R8, R9, R12 | the only way to Jira without MCP; one file, standard library only; commands `get`, `search`, `create`, `transition`, `comment`, `link`; reads env credentials and `.lado/tracker.yaml`; converts Markdown to wiki markup; adds the mark |
  Таблица трассировки перечисляет шесть команд. R3 говорит о восьми, `jira.py` их имеет.
  Две копии уже расходятся. Fix: добавить `assign`, `label`. Passes: 2/3.

- **F6.2** [low] `BLUEPRINT.md:99`
  > - **R11** One default write scope in SKILL.md: reading is always fine; create, transition,
  R11 перечисляет записи «create, transition, comment or link» (BLUEPRINT.md:100), а
  правило в SKILL.md:26 теперь называет ещё assign и label. Требование и навык
  расходятся. Fix: в R11 «create, transition, comment, assign, label or link».
  Passes: 1/3, confirmed: `grep -n "create, transition, comment or link"` находит строку
  только в BLUEPRINT. На это же указывает build-report («For the human»).

### 7. Когда звать человека

Новые отказы ложатся на прежние строки таблицы: 6 «report what you tried», 11 «fix the
request once; if it still fails, report it». Правило «report it» не менялось.
Исключение — F3.1: из-за него отказ assign может пойти по строке 5.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

- **F9.1** [low] `skills/tracker/SKILL.md:134`
  > on a write, Jira did answer, so `get` or `search` before running it again. Whatever the code, never guess the task's state from a failed run: say what failed.
  Причина «Jira did answer» верна для 5xx (код 12), но не для кода 1: крах скрипта бывает
  и до запроса, и во время него (`main()` ловит только `Failure`). Само действие
  правильное, неверно только объяснение. Fix: «after exit 1 or a 5xx exit 12 on a write,
  there is nothing to wait for: `get` or `search` before running it again».
  Passes: 1/3, confirmed: в `jira.py` `main()` ловит только `except Failure`, остальные
  исключения дают код 1 независимо от ответа Jira.

### 10. Описания навыков

Описание называет новые действия и даёт триггеры: «assign it, add or remove labels» и
«"assign it to me"», «"mark it waiting for release"». Таблица Actions перечисляет все
восемь действий, как требует R3.

### 11. Нейтральность к провайдеру

Новых путей и инструментов нет: `python3 ${SKILL_DIR}/jira.py`.

### 12. Безопасность и границы

- `assign` и `label` трогают только названную задачу и подчиняются правилу записи
  SKILL.md:26.
- `label` отправляет только реальные изменения и не трогает остальные метки.
- Если после изменения метки не удалось прочитать заново, строка говорит «do not run it
  again».
- Логин `JIRA_USER` печатается как `me`: так выполняется R5 «never prints them».

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Коды по-прежнему разделяют окружение и ошибку запроса. Но F3.1: отказ в праве на assign может выглядеть как ошибка окружения (5). |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Запись — SKILL.md:26 «Create, transition, comment, assign, label or link only when your role, your». |
| 3. Path outside the run's worktree | Без изменений: `${SKILL_DIR}`, `.lado/tracker.yaml` ищется от текущей папки вверх. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

- Новые действия названы в R3, слова статусов — в R6.
- Таблица трассировки отстала (F6.1), R11 тоже (F6.2).
- Меры бюджета green; раздел 4 BLUEPRINT («(1.1.0)») совпадает с выводом скрипта.
- Потоков и скелетов нет (R2).

## Previous findings

Отчёт 1.0.2 (полный, 802c099, `assessment`) и пункты плана:

| Находка / пункт | Статус | Доказательство |
|---|---|---|
| F3.1 [medium] правило после сбоя записи | RESOLVED | SKILL.md:132 «A failed write may have been applied. After exit 9 on a write, once you are told Jira»; `jira.py:348` `APPLIED_ANSWERED if method != "GET"` (формулировка — F9.1) |
| F3.2 [medium] обязательный комментарий перехода | RESOLVED | `jira.py:693` `and not (field_id == "comment" and args.comment is not None)]`; `test_transition_required_comment_is_given_by_comment` |
| F3.3 [low] «already in» отбрасывает флаги | RESOLVED | `jira.py:672` `raise Failure(REFUSED, "%s is already in %s: --resolution and --field were not "` |
| F3.4 [low] нечитаемый `SSL_CERT_FILE` | RESOLVED | `jira.py:259` `raise Failure(TLS, "SSL_CERT_FILE (%s) cannot be read: %s; the user points it "` |
| F5.1 [low] обещание про wiki-разметку | RESOLVED | SKILL.md:78 «Mentions `[~login]` and a bare `KEY-1` pass as they are. Wiki markup that» |
| F5.2 [low] скобки в URL | RESOLVED | `jira.py:365` `LINK` с одним уровнем скобок; тест в `test_links` |
| T1 `assign` | STILL OPEN (частично) | действие, «already so», вывод «before -> after» есть; коды 6/11 — только при 403/400 (F3.1) |
| T2 `label` | RESOLVED | `cmd_label`; `test_label_*`; метка с пробелом — код 2 до запроса |
| T3 id комментариев в `get` | RESOLVED | `jira.py:557` `print("\n--- comment %s, %s, %s\n%s" % (` (о `transition --comment` — F5.1) |
| T4 слова статусов | RESOLVED | SKILL.md:99 и README.md:57 `in progress: In Progress` |
| T5 описание и Actions | RESOLVED | см. критерий 10 |
| `kit.yaml` 1.1.0, README | RESOLVED | `kit.yaml:2` `version: 1.1.0`; README называет assign и label |

Build-report сверен с файлами и совпадает с ними. «Cut text: None» верно: ни одно
правило не сокращено.

## Cut rules

| Удалённое правило (файл:строка в базе 802c099) | Где теперь |
|---|---|
| BLUEPRINT R3 «six actions», «Nothing else (no delete, assign, user search,» | R3: «eight actions»; assign снят с запрета по плану, остальное («no delete, user search, attachments, boards or sprints») на месте |
| BLUEPRINT R12 «(added later if needed)» | Заменено решением человека «нет, ничего не меняем» (план) |
| SKILL.md:70-72 «Anything else is sent as it is, so wiki markup in plain text still works…»; «For wiki markup Markdown lacks (panels, `{noformat}`)… add `--wiki`» | SKILL.md:78-81, сужено по F5.1; правило о панелях и `{noformat}` с `--wiki` сохранено |
| SKILL.md:122-123 правило после сбоя записи | SKILL.md:132-134, разделено по кодам (F3.1) |
| SKILL.md и README `# a word of the process -> the board's status` | `# words process kits use -> the board's status` (T4) |
| `jira.py` строка сбоя «give them with --resolution or --field id=value» | Та же строка, добавлен `--comment` |
| `jira.py` `APPLIED` для 5xx | `APPLIED_ANSWERED`; `APPLIED` остался для кода 9 |
| `jira.py` `ssl.create_default_context` без обработки, прежний `LINK`, заголовок комментария в `get` | Те же места, расширены по плану |

Правил не потеряно.

## Missed earlier

Нет. Полный проход не делался (см. «Проходы»).

## Left by the plan

Нет: план ничего не оставляет («Leave: none»).

## Questions for the human

1. Проверить коды ответа Jira на назначение. Рекомендую добавить в пробу на тестовой Jira
   8.13.19 `assign KEY no.such.login` и, если есть пользователь без права Assign
   Issues, его попытку назначить. Тогда будет видно, какие коды Jira 8.13 отдаёт на самом
   деле. Исправление F3.1 нужно в любом случае: оно дёшево и не даст одному отказу
   остановить сессию.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
