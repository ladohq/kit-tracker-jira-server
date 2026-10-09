# Отчёт о ките: tracker-jira-server 1.1.0

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-1-0`), путь задан
- Коммит: 73144f1 (`kit.yaml` `version: 1.1.0`); визит 1 оценивал d7cea03
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.0.2-2026-10-09.md`
  (полная оценка, артефакт `assessment`). База — 802c099, её называет план.
  `git diff 802c099 -- kit.yaml README.md BLUEPRINT.md agents flows skills` затрагивает
  5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md, skills/tracker/jira.py.
  Визит 2 `evaluate`. С визита 1 (aa62dcf) изменились:
  - `jira.py` +34/−6 (c547fbe): 401 и 404 на assign, `_comment_id`;
  - SKILL.md +3/−2 (c547fbe);
  - BLUEPRINT.md: R11 и строка `jira.py` в таблице трассировки (73144f1);
  - тесты: 78.
- Проходы визита 2. Изменение — около 45 строк, три прохода я сделал сам:
  1. `cmd_assign` и `Failure.status/denied` против плана (T1) и R8;
  2. `_comment_id` и SKILL.md:60-62 против T3;
  3. BLUEPRINT R11 и строка трассировки, формулировка F9.1.
  Новых находок эти проходы не дали. Затем был полный проход (Re-evaluation 5) по всем пяти
  файлам целиком; его сделал отдельный субагент без `kit-reports/`. Он дал 4 находки, каждую
  я подтвердил запуском или цитатой: F3.2, F12.1, F5.2 в изменённом тексте и F5.3 в «Missed
  earlier». Однопроходных находок отброшено: 0.
- Проходы визита 1: три независимых субагента с дифф-файлом. Однопроходных находок
  отброшено 0, оставлено как подтверждённые 2 (F6.2, F9.1).
- Оговорка: коды 401 и 404 на `PUT issue/{key}/assignee` взяты из документации Atlassian
  REST v2. Теперь скрипт верно обрабатывает и их, и 403/400 (тесты). Какие коды отдаёт
  Jira 8.13 на самом деле, покажет проба (см. «Questions for the human»).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 3 открытые находки (0 high, 1 medium, 2 low) и 1 в «Missed earlier» (medium); находки визита 1 RESOLVED; пункты плана RESOLVED; 9 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 78, OK |
| Правило остановки | не выполнено: 0 high, 1 medium (F12.1). Это совет к гейту выпуска, а не блокировка |

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

1. SKILL.md, пункт об `assign`: брать только логин, который дали, а на код 11 сообщать,
   а не пробовать другой (F12.1).
2. Строка сбоя комментария после перехода при 9 или 5xx: «может быть добавлен,
   проверь `get`» (F5.3, «Missed earlier»).

## Находки

### 1. Границы ролей

Ролей нет. Правило записи: SKILL.md:26 «Reading is always fine. Create, transition,
comment, assign, label or link only when your role, your», и так же в R11.

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.2** [low] `skills/tracker/jira.py:782`
  > raise Failure(REFUSED, "Jira refused to assign %s to %s: no such user, or the "
  Любой отказ PUT получает текст «no such user». Это верно и для `assign KEY none` в
  проекте, где задача обязана иметь исполнителя. Настоящая причина видна только в скобках.
  Fix: при `login is None` писать «Jira refused to unassign %s» с причиной Jira.
  Passes: full pass, confirmed — запуск с ответом 400 «Issues must be assigned.»:
  ```
  11 Jira refused to assign A-1 to unassigned: no such user, or the user cannot be assigned in this project (Jira refused the values: assignee (Issues must be assigned.))
  ```

Остальные исходы `assign` соответствуют плану:
- 401 без `X-Authentication-Denied-Reason` → код 6;
- 401 с CAPTCHA → код 5;
- 404 и 400 → код 11 с логином;
- «already so» → код 0.

Тесты: `test_assign_without_permission_is_not_a_credentials_failure`,
`test_assign_unknown_user_answered_404`.

### 4. Независимая проверка

Не применимо: потоков нет. 78 тестов, OK. Перед гейтом выпуска супервизор делает пробу на
тестовой Jira (план, «Answers»).

### 5. Противоречия

- **F5.2** [low] `BLUEPRINT.md:78`
  > (403), a credential variable unset (named), credentials refused (401, or 403 with
  По R8 ответ 401 значит «учётные данные отвергнуты». В 1.1.0 `assign` трактует 401 без
  `X-Authentication-Denied-Reason` как нет прав (6), а 404 — как неизвестного пользователя
  (11), `jira.py:777-786`. Ни R8, ни R3 этого не говорят: blueprint отстал от скрипта.
  Fix: в R8 «except `assign`: a 401 without X-Authentication-Denied-Reason is no permission
  (exit 6), a 404 an unknown user (exit 11)». Passes: full pass, confirmed —
  `jira.py:777` `# Jira answers this request with 401 for a missing permission and 404 for an`.

Исправление F5.1 визита 1 согласовано. `_comment_id` ищет id, а если не находит, печатает
«comment added». SKILL.md:61-62 говорит: «If `transition --comment` prints no id, find
your `[LADO: …]` comment in `get`».

### 6. Дублирование

F6.1 и F6.2 визита 1 закрыты (см. «Previous findings»). README:77-79 повторяет правило
записи для человека и ссылается на SKILL.md; копии совпадают.

### 7. Когда звать человека

Правило «report it» не менялось. Пробел в нём — F12.1: после кода 11 на `assign` агенту
не сказано, что логин не подбирают.

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

F9.1 визита 1 закрыт. В новом коде есть причины, например
`# Jira answers this request with 401 for a missing permission and 404 for an`. Пустых
фраз нет.

### 10. Описания навыков

Описание называет все восемь действий и даёт триггеры («"assign it to me"», «"mark it
waiting for release"»). Внешних навыков нет.

### 11. Нейтральность к провайдеру

Без изменений: `python3 ${SKILL_DIR}/jira.py`, запасной путь для CLI без `${SKILL_DIR}`.

### 12. Безопасность и границы

- **F12.1** [medium] `skills/tracker/SKILL.md:130`
  > | 11 | Jira refused the request (bad JQL, a refused field value, unknown type, transition not open) | read the line, fix the request once; if it still fails, report it |
  На неизвестный логин `assign` даёт код 11 («no such user»), а эта строка велит «fix the
  request once». Поиска пользователей у скилла нет (R3), поэтому «исправить» можно только
  догадкой (`ivanov` → `i.ivanov`). Догадка может назначить задачу другому живому человеку
  от имени пользователя. Пункт об `assign` (SKILL.md:63) этого не запрещает.
  Fix: в пункте об `assign` «use only a login you were given; on exit 11 report it, do not
  try another login». Passes: full pass, confirmed — `test_assign_unknown_user_answered_404`
  ждёт код 11 и «Jira refused to assign TEST-1 to nobody: no such user».

Прочее без изменений:
- `assign` и `label` трогают только названную задачу;
- `label` шлёт только реальные изменения;
- логин `JIRA_USER` печатается как `me` (R5).

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Отказ в праве на assign больше не выглядит как сбой учётных данных: 401 без заголовка — код 6. Остальные коды разделены, как раньше. |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Запись — SKILL.md:26 и R11; подбор логина — F12.1. |
| 3. Path outside the run's worktree | Без изменений: `${SKILL_DIR}`; `.lado/tracker.yaml` ищется от текущей папки вверх. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

- Новые действия названы в R3, слова статусов — в R6.
- Правило записи с assign и label — в R11 (BLUEPRINT.md:99-100).
- Строка `jira.py` в таблице трассировки перечисляет восемь команд.
- R8 не говорит о 401 и 404 на assign (F5.2).
- Меры бюджета green; раздел 4 BLUEPRINT («(1.1.0)») совпадает с выводом скрипта.
- Потоков и скелетов нет (R2).

## Previous findings

Находки отчёта 1.0.2 (полного, 802c099) закрыты на визите 1. Ниже — находки визита 1
(aa62dcf) и пункты плана.

| Находка / пункт | Статус | Доказательство |
|---|---|---|
| F3.1 [high] коды assign 401/404 | RESOLVED | `jira.py:779` `if failure.status == 401 and not failure.denied:` → `NO_ACCESS`; 404 → `REFUSED`; два новых теста |
| F5.1 [medium] id при `transition --comment` | RESOLVED | `jira.py:718` `found = _comment_id(jira, args.key, comment)`; тест ждёт «comment 200 added»; SKILL.md:61-62 — запасной путь |
| F6.1 [low] строка трассировки | RESOLVED | BLUEPRINT.md:163 «commands `get`, `search`, `create`, `transition`, `comment`, `assign`, `label`, `link`» |
| F6.2 [low] R11 | RESOLVED | BLUEPRINT.md:100 «comment, assign, label or link only when the agent's role» |
| F9.1 [low] «Jira did answer» для кода 1 | RESOLVED | SKILL.md:135 «on a write, there is nothing to wait for: `get` or `search` before running it again.» |
| F3.1–F3.4, F5.1, F5.2 отчёта 1.0.2 | RESOLVED | закрыты на визите 1, на визите 2 без изменений |
| T1 `assign` | RESOLVED | коды 6 и 11 при 401/403 и 404/400 |
| T2–T5, версия 1.1.0, README | RESOLVED | закрыты на визите 1, на визите 2 без изменений |

Build-report сверен с файлами и совпадает с ними. Таблицы сокращённого текста нет;
правил не сокращено.

## Cut rules

| Удалённое правило (файл:строка в базе 802c099) | Где теперь |
|---|---|
| BLUEPRINT R3 «six actions», «Nothing else (no delete, assign, user search,» | R3: «eight actions»; assign снят с запрета по плану, остальное на месте |
| BLUEPRINT R11 «comment or link only when» | R11: «comment, assign, label or link only when» (расширено) |
| BLUEPRINT R12 «(added later if needed)» | Заменено решением человека «нет, ничего не меняем» (план) |
| SKILL.md:70-72 обещание о wiki-разметке; правило о панелях и `{noformat}` | SKILL.md:78-81, сужено по F5.1 отчёта 1.0.2; правило о `--wiki` сохранено |
| SKILL.md:122-123 правило после сбоя записи | SKILL.md:133-135, разделено по кодам |
| SKILL.md и README `# a word of the process -> the board's status` | `# words process kits use -> the board's status` (T4) |
| `jira.py` «give them with --resolution or --field id=value» | Та же строка, добавлен `--comment` |
| `jira.py` `APPLIED` для 5xx | `APPLIED_ANSWERED`; `APPLIED` остался для кода 9 |
| `jira.py` `moved += ", comment added"` (визит 1) | `jira.py:718-719`, с id, если он нашёлся |
| `jira.py` ветка отказа `cmd_assign` (визит 1) | `jira.py:777-786`, расширена 401/404 |

Правил не потеряно.

## Missed earlier

- **F5.3** [medium] `skills/tracker/jira.py:724`
  > raise Failure(failure.code, "%s done, but the comment was not added (do not "
  Если отдельный комментарий после перехода не дождался ответа (9) или получил 5xx,
  строка утверждает сразу две вещи. С одной стороны, комментарий «was not added … send
  the comment with comment». С другой, «the change may have been applied». Агент,
  выполнивший первую половину, может отправить комментарий второй раз. Строка появилась
  в 1.0.2 (f20af91), в тексте, который этот дифф не трогает.
  Fix: при коде 9 или 5xx писать «the comment may have been added: check with get before
  sending it with comment». Passes: full pass, confirmed — запуск:
  ```
  9 A-1: Open -> In Progress done, but the comment was not added (do not run the transition again; send the comment with comment): Jira did not answer in 30 seconds; send Jira nothing more until you are told it answers again; the change may have been applied: once Jira answers again, check with get or search before running it again
  ```

## Left by the plan

Нет: план ничего не оставляет («Leave: none»).

## Questions for the human

1. Проба на тестовой Jira 8.13.19 перед выпуском. Рекомендую кроме пунктов плана
   добавить `assign KEY no.such.login` (ждём код 11). Если есть пользователь без права
   Assign Issues, добавить и его попытку назначить (ждём код 6). Так станет видно,
   какие коды Jira 8.13 отдаёт на самом деле.
2. F12.1 (medium) и F5.3 (medium, «Missed earlier») не блокируют выпуск. Рекомендую
   исправить F12.1 до выпуска: это одна фраза в SKILL.md, и без неё агент может назначить
   задачу не тому человеку. F5.3 тоже одна строка, его можно взять туда же.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
