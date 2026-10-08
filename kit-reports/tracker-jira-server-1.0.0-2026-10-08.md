# Отчёт о ките: tracker-jira-server 1.0.0

- Дата: 2026-10-08
- Кит: `.` (worktree запуска `improve/tracker-jira-server`), путь задан
- Коммит: e81d06a (`kit.yaml` `version: 1.0.0`)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-0.1.1-2026-10-08.md`
  (артефакт `assessment`), база — 37181e0 (её называет план),
  `git diff 37181e0 -- kit.yaml README.md BLUEPRINT.md agents flows skills`: 5 файлов,
  +105 −57 (a025bf3 — BLUEPRINT после триажа; e81d06a — сборка).
- Проходы: три независимых субагента с диффом, скиллами `kit-rubric` и `lado-kit-format`,
  без `kit-reports/`. Проход 1: kit.yaml, README, SKILL.md, jira.py, BLUEPRINT. Проход 2:
  изменённые функции jira.py с запусками, затем SKILL.md, README, BLUEPRINT. Проход 3:
  SKILL.md глазами работника и ведущего, BLUEPRINT по требованиям, README, jira.py, и
  проверка вырезанных правил по `git diff --word-diff`. Однопроходных находок отброшено: 4
  (ссылка `link` на ещё не запушенную ветку; 429 не останавливает других агентов;
  двусмысленное «go on with it»; «once Jira answers» как приглашение проверять Jira).
  Оставлено как подтверждённые: 2. Полный проход (Re-evaluation 5) не делался: три прохода
  оставили блокирующую находку (F5.1).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 10 находок (1 high, 1 medium, 8 low); 8 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста, без полного прохода (есть блокирующая находка); тесты: 50, OK |
| Правило остановки | не выполнено: 1 high (F5.1), 1 medium (F3.1) |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.0.0

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

У кита нет потоков (R2), скелетов нет. Скрипт потоков этого случая не знает (см. «Found on
the way»):

```
$ flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. Сообщение скрипта о коде 9 должно само говорить «send Jira nothing more until you are
   told it answers again» — для чтения и записи, как обещают R8 и журнал (F5.1).
2. SKILL.md:48 — `--epic-name` только при заданном `fields.epic_name`, иначе `--field`,
   которое назовёт скрипт (F3.1).

## Находки

### 1. Границы ролей

Ролей нет. Разделение «работник → супервизор, ведущий → человек» сохранено: SKILL.md:115
«as a worker, send the supervisor that line and the command with `send_message`;». Формулировка
`STOP_ALL` — F5.2.

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

- **F3.1** [medium] `skills/tracker/SKILL.md:48`
  > settings ("bug"). An epic also needs `--epic-name`. When the project requires more
  После исправления F3.1 прошлого отчёта скрипт без `fields.epic_name` советует
  `--field <id>=<name>`, а эта строка (и строка 35 с новым `[--epic-name '<name>']`) велит
  всегда давать `--epic-name`. Без настройки это код 3 (`setting()`), строка 3 таблицы —
  «report it; the user fixes the file»: агент останавливается, хотя `--field` сработал бы.
  Строка не изменена, но ошибочной её сделало изменение рядом.
  Fix: «An epic also needs its Epic Name: `--epic-name` when the settings name
  `fields.epic_name`, otherwise the `--field` the script names (exit 8).» Passes: 3/3
  (проходы дали medium, medium, low — взят medium)

### 4. Независимая проверка

Не применимо к тексту кита: R10 ставит повтор пробы в песочнице до одобрения релиза
человеком (BLUEPRINT.md:89-90).

### 5. Противоречия

- **F5.1** [high] `BLUEPRINT.md:73`
  > nothing more until told it answers again; the script's message says so. A refused login
  R8 (и строка журнала BLUEPRINT.md:166 «(script message and SKILL.md)») утверждает, что
  сообщение скрипта о коде 9 само велит больше не обращаться к Jira. Это не так: чтение даёт
  `jira.py: Jira is not reachable (ConnectionRefusedError): are you on the VPN or the company
  network?`, запись добавляет лишь `; the change may have been applied: once Jira answers
  again, check with get or search before running it again` (запуск против закрытого порта,
  код 9). Ведущий без навыка (README это допускает) получает от работника только эту
  строку, правила «nothing more» не знает и не знает, что должен сказать работнику, когда
  Jira ответит; работник по строке 9 SKILL.md ждёт «until you are told» — это и был сценарий
  пробы (2 × 30 с), который изменение должно закрыть.
  Fix: константа `"; send Jira nothing more until you are told it answers again"` в обоих
  сообщениях UNREACHABLE `_network_failure` (`jira.py:289-292`), для GET тоже, и тест;
  либо убрать «the script's message says so» из R8 и «script message and» из журнала.
  Первое ближе к решению триажа (наблюдение 2). Passes: 3/3 (проходы дали high, medium,
  medium — взят high по правилу рубрики; сам я оцениваю ближе к medium, человек может
  решить иначе)
- **F5.2** [low] `skills/tracker/jira.py:40`
  > STOP_ALL = "; tell every agent to stop using Jira until the human says it is fixed"
  Строку первым читает работник, а она велит ему самому «tell every agent»; README.md:12 и
  SKILL.md:125 («the lead tells them») отдают это ведущему.
  Fix: `"; the lead tells every agent to stop using Jira until the human says it is fixed"`.
  Passes: 2/3
- **F5.3** [low] `skills/tracker/SKILL.md:134`
  > After exit 1, 9 or 12 on a write, once Jira answers, `get` or `search` before running it
  Код 12 теперь включает 429, а скрипт говорит о нём «do not retry» и в комментарии —
  «nothing was applied» (`jira.py:329-331`); эта строка всё равно ведёт к проверке и
  повтору записи.
  Fix: «After exit 1, 9 or a 5xx exit 12 on a write, once you are told Jira answers again,
  …». Passes: 3/3
- **F5.4** [low] `BLUEPRINT.md:140`
  > - R10: `tests/test_jira.py`; the release itself is the `create` run's step, not a kit file.
  Новая R10 — релиз 1.0.0 в `improve`, пробы на тестовой Jira вместо настоящей,
  переименование. Обратная проверка и строка трассировки BLUEPRINT.md:126 («the trial
  touches the real Jira only with the human's yes») остались от прежней R10.
  Fix: «the release and the rename are the run's release step, not a kit file»; в строке
  126 — «the trials run on a test Jira, so …». Passes: 3/3
- **F5.5** [low] `BLUEPRINT.md:52`
  > design round Q3 (strict subset), Q2 (the first project's facts deferred to the trial).
  Пункт «facts … gathered by the human before the trial» удалён, а R10 больше не знает
  пробы на настоящем проекте; источник R6 указывает на пробу, которой не будет.
  Fix: «Q2 (the first project's facts are gathered at its first use)». Passes: 1/3,
  confirmed (`git diff 37181e0 -- BLUEPRINT.md`: удалена строка «- CRM3's facts (issue
  types, statuses, Epic Link id, required fields, Jira Software) and»; новая R10 «the first
  real project is the first use after the release, not a condition of it»)

### 6. Дублирование

Правило кода 5 стоит в сообщении скрипта, в строке 5 SKILL.md и в README.md:11-12 —
намеренно, R8: «so a lead without the skill learns it too»; строка SKILL.md указывает на
сообщение («As the line says»). Правило «ждать или идти дальше» теперь в одном месте
(SKILL.md:116-117). Не находка.

### 7. Когда звать человека

Путь сохранён: работник → супервизор, ведущий → человек, и «Then wait for the answer if
your step cannot go on without the tracker; otherwise go on with it.» Пробел для ведущего
без навыка при коде 9 — F5.1.

### 8. Циклы на повторном визите

Не применимо: потоков нет. Код 11 по-прежнему «fix the request once».

### 9. Краткость и «почему»

- **F9.1** [low] `skills/tracker/jira.py:166`
  > raise ValueError(where(key) + "'%s.%s' must be one plain value" % (key, name))
  Для плохого вложенного значения называется строка раздела, а не значения: для
  `statuses:` (строка 2) и `done: [x]` (строка 4) вывод
  `… tracker.yaml line 2: 'statuses.done' must be one plain value`.
  Fix: запоминать строку каждого вложенного ключа и называть её здесь. Passes: 2/3
- **F9.2** [low] `BLUEPRINT.md:14`
  > or newer (8.x before 8.4 lacks the create metadata R7 uses), not for one project. Nothing project- or company-specific (Jira address, project key,
  Строки R1 и R6 (BLUEPRINT.md:46, «…its line too, F5.5). Only the project key…») не
  перенесены, а id находки стоит в тексте требования, а не в его *Source*.
  Fix: перенести обе строки; «F5.5» — в *Source* R6. Passes: 1/3, confirmed (длина
  строки 14 — 148 знаков; строка 46 в diff a025bf3)

### 10. Описания навыков

`description` навыка не менялся; `kit.yaml` теперь «8.4 or newer», в согласии с README,
R1, R7 и `--help` скрипта.

### 11. Нейтральность к провайдеру

Изменённый текст не называет инструментов CLI; путь к скрипту — `${SKILL_DIR}`; `<kit>` в
README — для человека.

### 12. Безопасность и границы

- **F12.1** [low] `README.md:44`
  > `curl -u "$JIRA_USER:$JIRA_PASSWORD" "$JIRA_URL/rest/api/2/myself"`.
  Новый вариант кладёт пароль в аргументы curl, видимые в списке процессов (`ps`), — против
  совета самого README держать пароль в связке ключей. Не сказано и как найти `<kit>`.
  Fix: оставить только проверку через `jira.py` и добавить «(`lado kits show
  tracker-jira-server` prints it)»; или прежний `curl -u "$JIRA_USER"` с оговоркой про
  опечатку. Passes: 3/3
- **F12.2** [low] `README.md:17`
  > lado kits add https://github.com/ladohq/lado-kit-tracker-jira-server
  `git remote -v` всё ещё `ladohq/kit-tracker-jira-server`; R10 переименовывает репозиторий
  только «at the release step with the human's yes». До этого — или при «нет» — команда
  установки не работает; заголовок README.md:1 `# kit-tracker-jira-server` не переименован.
  Fix: заголовок — вместе с URL; на шаге релиза сверить URL README с remote после
  переименования (или вернуть URL, если человек скажет «нет»). Passes: 2/3

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Коды по-прежнему разделяют окружение (4, 5, 9, 10, 12) и ошибку запроса (2, 11); 429 перенесён из 11 в 12 («report it»). |
| 2. Work outside a flow, merge without a gate | Нет git-работы; запись в Jira — SKILL.md:25 «only when your role, your step or the human asks for it»; переименование репозитория — «at the release step with the human's yes» (R10). |
| 3. Path outside the run's worktree | Без изменений: `.lado/tracker.yaml` «from the current directory up to the repository root»; `<kit>` в README — для человека. |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. |

## Not traced

- R8 обещает то, чего нет в скрипте (F5.1).
- Обратная проверка и строка трассировки для R10 устарели (F5.4).
- Других расхождений нет: все элементы названы требованиями, меры бюджета green, потоков
  и скелетов нет.

## Previous findings

| Находка (отчёт 37181e0) | Статус | Доказательство |
|---|---|---|
| F3.1 подсказка Epic Name | RESOLVED в скрипте; новая F3.1 — SKILL.md:48 | `jira.py:484` `if epic_name and f.get("fieldId") == epic_name:`; тест `test_create_epic_name_of_another_field_points_to_field` |
| F3.2 429 | RESOLVED (см. F5.3) | `jira.py:328` `if code == 429:` → `SERVER_ERROR`; строка 12 SKILL.md «or it is rate limiting requests (429)» |
| F3.3 `link` без URL | RESOLVED | SKILL.md:41-42 «a repository with no remote has no such page, so give the branch and the commit hash in a `comment`» |
| F5.1 одно правило после «report it» | RESOLVED | SKILL.md:116-117 «Then wait for the answer if your step cannot go on without the tracker; otherwise go on with it.»; строка 12 — «report it» |
| F5.2 версии | RESOLVED | kit.yaml:4, README.md:3, `jira.py:2` «8.4 or newer»; `grep -rn '8\.x'` в тексте кита — только BLUEPRINT.md:14 «8.x before 8.4» |
| F5.3 после кода 9 | RESOLVED в SKILL.md (строка 9) и `APPLIED`; STILL OPEN в обещании R8 — см. F5.1 | `jira.py:38` «once Jira answers again»; вывод чтения при коде 9 без «nothing more» |
| F5.4 токены | RESOLVED | README.md:26 «Personal access tokens (Jira 8.14 and newer) are not supported:» |
| F5.5 строка в ошибках настроек | RESOLVED для ключей верхнего уровня (см. F9.1) | `jira.py:153` `"%s line %d: " % (path, lines[key])` |
| F7.1 код 5 до ведущего | RESOLVED (см. F5.2) | `jira.py:40` `STOP_ALL`; README.md:10-12 |
| F7.2 открытые решения | RESOLVED | BLUEPRINT.md:97 «Decided at the improve triage (2026-10-08): no limits for agents beyond R11» |
| F9.1 `--epic-name` в строке `create` | RESOLVED | SKILL.md:35 `[--epic-name '<name>']` |
| F12.1 R10 | RESOLVED (см. F5.4) | BLUEPRINT.md:88 «these trials stand for the trial on the human's real Jira» |
| F12.2 имена проекта | RESOLVED | `grep -rin 'clens\|crm3'` вне `kit-reports/` и `.git` — пусто |
| F12.3 проверка входа | RESOLVED (см. F12.1) | README.md:41-42 `python3 <kit>/skills/tracker/jira.py search 'project = ABC' --max 1` |
| F12.4 имя репозитория | RESOLVED в README (см. F12.2) | README.md:17 |

Сверка с build-report: все 15 пунктов «fixed/done/checked» подтверждены файлами; оговорки —
в столбце «Статус».

## Cut rules

| Удалённое правило (файл:строка в базе) | Где теперь |
|---|---|
| SKILL.md:113 «and wait for its answer» | SKILL.md:116-117, теперь условно — так велит план (F5.1) |
| SKILL.md:121 «The lead tells every agent to stop using Jira until the human says it is fixed» | SKILL.md:125 «the lead tells them» и `jira.py:40` `STOP_ALL` (формулировка — F5.2) |
| SKILL.md:128 «whether your step can go on without the tracker is your step's decision» | SKILL.md:116-117 |
| README.md:24-25 «Jira Server before 8.14 has no personal access tokens, so the password is the user's own» | README.md:26-28 |
| README.md:38 проверка входа `curl -u "$JIRA_USER"` | README.md:41-44 (F12.1) |
| BLUEPRINT.md:75-78 R10 «trial … in the real Jira …, only with the human's yes» | R10 BLUEPRINT.md:86-96 — заменено решением триажа |
| BLUEPRINT.md:80-83 «Open … Further limits for agents» | BLUEPRINT.md:97-99 |
| BLUEPRINT.md:84-85 «CRM3's facts … gathered by the human before the trial» | снято вместе с пробой на CRM3; висящая ссылка — F5.5 |

Правил не потеряно.

## Missed earlier

Нет (полный проход не делался: есть блокирующая находка).

## Left by the plan

Нет: план «Leave: none».

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не знает кита без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Всё ещё открыто.
