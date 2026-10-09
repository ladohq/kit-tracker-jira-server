# Отчёт о ките: tracker-jira-server 1.1.0

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-1-0`), путь задан
- Коммит: 9308f1c (`kit.yaml` `version: 1.1.0`). Визит 2 оценивал 73144f1, визит 1 — d7cea03.
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.0.2-2026-10-09.md`
  (полная оценка, артефакт `assessment`). База — 802c099, её называет план.
  `git diff 802c099 -- kit.yaml README.md BLUEPRINT.md agents flows skills` затрагивает
  5 файлов: BLUEPRINT.md, README.md, kit.yaml, skills/tracker/SKILL.md, skills/tracker/jira.py.
  Визит 3 `evaluate`, после гейта выпуска. Решение человека: «Оставить F12.1/F5.3/F3.2,
  сделать F5.2, логин вместо me». С визита 2 (7bc2beb) изменились:
  - `jira.py` (0a1465e, 9308f1c);
  - SKILL.md +2 (0a1465e);
  - BLUEPRINT R5, R8 и строка журнала 1.1.0 (03abdd6);
  - тесты: 80.
- Проходы визита 3. Изменение — около 60 строк, три прохода я сделал сам:
  1. `cmd_assign` (разбор отказов, `_user`) против R5 и R8;
  2. ветка сбоя комментария после перехода против таблицы кодов SKILL.md;
  3. R5, R8 и журнал против кода и решения на гейте.
  Новых находок эти проходы не дали. Затем был полный проход (Re-evaluation 5) по всем
  пяти файлам целиком; его сделал отдельный субагент без `kit-reports/`. Он дал 3 находки
  в изменённом тексте (F5.4, F3.3, F3.4), каждую я подтвердил по коду (`jira.py:724-733`,
  `jira.py:782-792`) и запуском субагента. Однопроходных находок отброшено: 0.
- Проходы визитов 1–2: см. историю этого файла в git (aa62dcf, 7bc2beb).
- Оговорка: коды 401 и 404 на `PUT issue/{key}/assignee` взяты из документации Atlassian.
  Проба `trial-1.1.0` у человека; вывод assign с логином вместо `me` — его решение.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 3 открытые находки (0 high, 1 medium, 2 low); находки визита 2 RESOLVED (F5.3 из «Missed earlier» тоже); пункты плана RESOLVED; 10 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста и полный проход по 5 файлам, которых касается дифф (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 80, OK |
| Правило остановки | не выполнено: 0 high, 1 medium (F5.4). Это совет к гейту выпуска, а не блокировка |

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

1. Сбой комментария после перехода с ответом 429: вместо «send the comment with comment»
   писать «report it; send the comment with comment once you are told to» (F5.4).

## Находки

### 1. Границы ролей

Ролей нет. Правило записи: SKILL.md:26 и R11, обе формулировки называют assign и label.

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.3** [low] `skills/tracker/jira.py:785`
  > if login is None and failure.code == REFUSED:
  Сообщение об отказе снять исполнителя ловит только отказы с кодом 11. На `assign KEY
  none` ответ 404 уходит в следующую ветку и печатает «no such user» для
  «unassigned». Это бывает, только если задача исчезла между GET и PUT.
  Fix: проверять `login is None` раньше ветки 404. Passes: full pass, confirmed —
  `jira.py:788` `if failure.status == 404 or failure.code == REFUSED:` идёт после этой
  ветки. Запуск с `user="none"` и 404: `11 Jira refused to assign T-1 to unassigned:
  no such user, … (404)`.

- **F3.4** [low] `skills/tracker/jira.py:788`
  > if failure.status == 404 or failure.code == REFUSED:
  Проверка смотрит на HTTP-статус, а не на код скрипта. Поэтому 404 не от Jira (код 4,
  «JIRA_URL is not Jira's base address») на `assign` становится кодом 11 «no such user».
  Маловероятно: GET перед этим прошёл по тому же адресу.
  Fix: `failure.code in (NOT_FOUND, REFUSED)`. Passes: full pass, confirmed — запуск с
  кодом 4 и статусом 404: `11 Jira refused to assign T-1 to alice: no such user … (404)`.

### 4. Независимая проверка

Не применимо: потоков нет. 80 тестов, OK. Проба `trial-1.1.0` на тестовой Jira — у
человека.

### 5. Противоречия

- **F5.4** [medium] `skills/tracker/jira.py:733`
  > if unsure else "send the comment with comment", failure.message))
  Если комментарий после перехода получил 429, строка даёт два противоположных указания:
  «send the comment with comment» и, из сообщения 429, «report it, do not retry».
  Таблица SKILL.md для кода 12 говорит только «report it». Одни агенты сразу отправят
  комментарий снова, пока Jira ещё ограничивает запросы, другие сообщат.
  Fix: при 429 «the comment was not added (do not run the transition again; report it,
  then send the comment with comment once you are told to)».
  Passes: full pass, confirmed — запуск:
  ```
  12 T-1: Open -> Code Review done, but the comment was not added (do not run the transition again; send the comment with comment): Jira is rate limiting requests (429): report it, do not retry
  ```
  Ветку 429 эта правка вынесла отдельно (`jira.py:725` `# No answer or a 5xx may follow
  a comment Jira did add; a 429 runs nothing.`), поэтому находка в изменённом тексте.

R5 и вывод `assign` согласованы. Логин печатает только `assign`: `get`, `search` и
комментарии показывают `displayName`. Docstring `jira.py:5-6` говорит то же, что R5.
SKILL.md:21-22 «never ask for them, print them or put them in a file» обращено к агенту,
а не описывает вывод скрипта, поэтому противоречия нет.

### 6. Дублирование

Пункт SKILL.md:63 об `assign` сужает строку 11 таблицы только для assign, а не повторяет
её. R8 говорит о том же как требование. Нарушения нет.

### 7. Когда звать человека

F12.1 визита 2 закрыт: SKILL.md:63 «use only a login you were given; on exit 11 report it
and do not try».

### 8. Циклы на повторном визите

Не применимо: потоков нет.

### 9. Краткость и «почему»

Новый пункт даёт причину: «since a guess may assign the task to someone else». Комментарий
в коде объясняет ветку 429 (`jira.py:725`).

### 10. Описания навыков

Без изменений с визита 2: описание называет все восемь действий.

### 11. Нейтральность к провайдеру

Без изменений: `python3 ${SKILL_DIR}/jira.py`.

### 12. Безопасность и границы

F12.1 закрыт (см. критерий 7). Логин `JIRA_USER` виден в выводе `assign` — это решение
человека, записанное в R5 (BLUEPRINT.md:51-53). Пароль и `JIRA_URL` по-прежнему не
печатаются: тесты проверяют пароль на каждом запуске.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Отказ в праве на assign — код 6, CAPTCHA — 5. Мелкая неточность: 404 не от Jira на assign — F3.4. |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Запись — SKILL.md:26 и R11; подбор логина запрещён (SKILL.md:63). |
| 3. Path outside the run's worktree | Без изменений: `${SKILL_DIR}`; `.lado/tracker.yaml` ищется от текущей папки вверх. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

Ничего:
- R5 описывает логин в выводе `assign`;
- R8 описывает 401 и 404 на assign и запрет подбирать логин;
- R11 и таблица трассировки называют assign и label;
- журнал 1.1.0 перечисляет правки визитов 2–3;
- меры бюджета green, раздел 4 совпадает с выводом скрипта;
- потоков и скелетов нет (R2).

## Previous findings

Находки визита 2 (7bc2beb) и пункты плана. Находки визита 1 и отчёта 1.0.2 закрыты
раньше и на этом визите не менялись.

| Находка / пункт | Статус | Доказательство |
|---|---|---|
| F12.1 [medium] подбор логина | RESOLVED | SKILL.md:63 «- **assign**: use only a login you were given; on exit 11 report it and do not try»; R8 «an unknown login is reported, never guessed» |
| F3.2 [low] отказ снять исполнителя | RESOLVED | `jira.py:786` «Jira refused to unassign %s: %s»; `test_unassign_refused_names_the_reason` (при 404 — F3.3) |
| F5.2 [low] R8 о 401/404 на assign | RESOLVED | BLUEPRINT.md:86 «For `assign` only, a 401 without» |
| F5.3 [medium, Missed earlier] комментарий после перехода при 9/5xx | RESOLVED | `jira.py:726` `unsure = failure.code == UNREACHABLE or (failure.code == SERVER_ERROR`; `test_transition_done_but_comment_unanswered_says_check_first` (при 429 — F5.4) |
| R5 логин вместо `me` (гейт) | RESOLVED | `jira.py` `_user` возвращает `name or "unassigned"`; тест ждёт `TEST-1: assignee ann -> agent.user` |
| Пункты плана T1–T5, находки 1.0.2 и визита 1 | RESOLVED | без изменений с визита 2 |

Build-report сверен с файлами и совпадает с ними; правил не сокращено.

## Cut rules

| Удалённое правило (файл:строка в базе 802c099) | Где теперь |
|---|---|
| BLUEPRINT R3 «six actions», «Nothing else (no delete, assign, user search,» | R3: «eight actions»; assign снят с запрета по плану, остальное на месте |
| BLUEPRINT R5 «never writes them to disk and never prints them» | R5: «never prints the password or `JIRA_URL`; the login of `JIRA_USER` appears only as an assignee in `assign`'s output» — сужено решением человека на гейте |
| BLUEPRINT R11 «comment or link only when» | R11: «comment, assign, label or link only when» |
| BLUEPRINT R12 «(added later if needed)» | Заменено решением человека «нет, ничего не меняем» |
| SKILL.md:70-72 обещание о wiki-разметке | SKILL.md:78-81, сужено; правило о `--wiki` сохранено |
| SKILL.md:122-123 правило после сбоя записи | SKILL.md:135-137, разделено по кодам |
| SKILL.md и README `# a word of the process -> the board's status` | `# words process kits use -> the board's status` (T4) |
| `jira.py` docstring «are never printed» | `jira.py:5-6`, как новый R5 |
| `jira.py` «the comment was not added … send the comment with comment» | `jira.py:724-733`, разделено: при 9/5xx «may not have been added … check with get», иначе прежний текст (при 429 — F5.4) |
| `jira.py` `_user` → `me` для `JIRA_USER` | Удалено решением человека (R5) |
| `jira.py` `APPLIED` для 5xx, «give them with --resolution or --field id=value», `moved += ", comment added"` | `APPLIED_ANSWERED`; строка с `--comment`; `_comment_id` |

Правил не потеряно. Два сужения (R5, `_user`) — решения человека на гейте выпуска.

## Missed earlier

Нет. Полный проход визита 3 не нашёл находок в тексте, который дифф не трогает. F5.3
визита 2 закрыт.

## Left by the plan

Нет: план ничего не оставляет.

## Questions for the human

1. F5.4 (medium) не блокирует выпуск. Исправление — одна строка для случая 429. Его можно
   сделать сейчас или отложить. Рекомендую отложить до следующей версии: при 429 Jira
   отказывает и повторной отправке, так что худший исход — лишняя попытка, а не дубль.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
