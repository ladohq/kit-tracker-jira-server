# Отчёт о ките: tracker-jira-server 1.0.2

- Дата: 2026-10-09
- Кит: `.` (worktree запуска `improve/tracker-jira-server-1-1-0`), путь задан
- Коммит: 802c099 (`kit.yaml` `version: 1.0.2`; текст кита тот же, что в e9000a2)
- Оценил: критик kit-builder (слои a и b)
- Режим: полная оценка (шаг `assess` запуска `improve` к 1.1.0). Задача называет прежний
  отчёт этого файла (b5c7aa6/802c099), но это повторная оценка, а не полная: по шагу
  он только фон. Последняя полная оценка — `tracker-jira-server-0.1.1-2026-10-08.md`,
  с тех пор текст кита менялся. Этот файл переписан, прежняя его версия есть в git
  (802c099).
- Проходы: три независимых субагента, каждый с `kit-rubric`, `lado-kit-format` и папкой
  кита, без `kit-reports/`. Проход 1 начинал с kit.yaml и README, проход 2 — с `jira.py`
  по командам, проход 3 — с SKILL.md глазами агента чужого кита. Однопроходных находок
  отброшено: 1. Это `{…}` в обычном тексте, который Jira читает как макрос. Так задумано
  в R12 (BLUEPRINT.md:95, «Everything else, including wiki-special characters (`{`, `[`,»
  … «passes as it is»), а вред на живой Jira в этом проходе не показан. Оставлено как подтверждённые: 4
  (F3.2–F3.4, F5.2). Каждую я проверил запуском, вывод приведён в находке.
- Внешних и ожидаемых навыков нет (`dependencies.skills` и `expects` отсутствуют).

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); скелетов в BLUEPRINT.md нет |
| b. Рубрика | 6 находок (0 high, 2 medium, 4 low); 10 из 12 критериев без находок |
| Охват | полная оценка всего кита, 5 файлов: kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py; тесты: 64, OK |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.0.2

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

У кита нет потоков (R2) и нет скелетов, поэтому рисовать и сравнивать нечего. Скрипт
потоков такой кит не обрабатывает (см. «Found on the way»):

```
$ uv run --script flow_diagram.py . --out kit-reports/tracker-jira-server-1.0.2-2026-10-09
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
$ uv run --script flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. Разделить правило после сбоя записи. Для кода 9 — «когда скажут, что Jira отвечает».
   Для кодов 1 и 5xx — сразу `get`/`search` перед повтором (F3.1).
2. Засчитывать `--comment` как поле `comment` экрана перехода (F3.2).

## Находки

### 1. Границы ролей

Ролей нет (R2). Права агента на запись в Jira заданы в одном месте, SKILL.md:25
«Reading is always fine. Create, transition, comment or link only when your role, your…».
Файл настроек — пользователя: SKILL.md «the user changes it, not you».

### 2. Передачи между шагами

Не применимо: потоков нет. Результат действия — строка в stdout (ключ задачи, id
комментария). Сбой агент передаёт как «that line and the command» через `send_message`.

### 3. Готовность и исходы

- **F3.1** [medium] `skills/tracker/SKILL.md:122`
  > After exit 1, 9 or a 5xx exit 12 on a write, once you are told Jira answers again, `get`
  Условие «once you are told Jira answers again» подходит только к коду 9. После краха
  скрипта (1) и после 5xx (12) Jira ответила, и такого сообщения никто не пришлёт. Одни
  агенты будут ждать его без конца, другие сразу повторят запись без проверки. Крах тоже
  может случиться после применённой записи: `jira.py:627` читает ответ уже после POST.
  Та же формулировка есть в сообщении скрипта для 5xx (`jira.py:40` `APPLIED`).
  Fix: после 9 — `get`/`search`, когда скажут, что Jira отвечает; после 1 или 5xx на
  записи — `get`/`search` перед повтором. Так же разделить `APPLIED`.
  Passes: 2/3 (проход 1 дал medium, проход 3 — low; взят medium)

- **F3.2** [medium] `skills/tracker/jira.py:679`
  > and field_id not in fields]
  Проверка обязательных полей перехода смотрит только на `--field` и `--resolution`.
  Если экран требует поле `comment`, `--comment` его не закрывает. Агент делает то, что
  велит SKILL.md:56 «(exit 8): add `--resolution`, `--field` or `--comment`», и снова
  получает код 8. Если он попробует `--field comment=…`, комментарий уйдёт в `fields`,
  а такой формат Jira отвергает.
  Fix: считать `comment` заданным при `args.comment is not None` и отправлять его в
  `update.comment`; добавить тест. Passes: 1/3, confirmed — запуск с поддельной Jira,
  переход с `"fields": {"comment": {"required": true}}` и `comment="done"`:
  ```
  EXIT 8 transition 'Resolve' needs: Comment (comment); give them with --resolution or --field id=value
  ```

- **F3.3** [low] `skills/tracker/jira.py:660`
  > if not match and current.lower() == status.lower():
  Когда задача уже в целевом статусе, ветка обрабатывает только `--comment`, а
  `--resolution` и `--field` молча отбрасывает, с кодом 0. `transition KEY done
  --resolution Fixed` на задаче в Done без резолюции печатает «already in Done», и агент
  сообщит, что задача решена.
  Fix: в этой ветке при `--resolution` или `--field` выходить с кодом 11 или писать в
  строке, что они не применены. Passes: 1/3, confirmed — запуск:
  `resolution="Fixed", field=["x=1"]` → `T-1 is already in Done`, rc 0, POST не
  отправлен.

- **F3.4** [low] `skills/tracker/jira.py:253`
  > context = ssl.create_default_context(cafile=cafile)
  Если `SSL_CERT_FILE` указывает на несуществующий файл, скрипт падает с трассировкой и
  кодом 1. Это нарушает R8 (BLUEPRINT.md:65 «Each failure is one plain line saying what
  happened and what to do»). Последняя строка не называет переменную, хотя README:46
  сам велит её задать.
  Fix: ловить `OSError`/`ssl.SSLError` здесь и давать `Failure(TLS, "SSL_CERT_FILE (<path>)
  cannot be read: …")`. Passes: 1/3, confirmed — `SSL_CERT_FILE=/nonexistent/ca.pem
  jira.py get X-1`:
  ```
  FileNotFoundError: [Errno 2] No such file or directory
  exit 1
  ```

### 4. Независимая проверка

Не применимо: потоков и слияний нет. Каждая запись помечена `[LADO: <agent>]`
(`jira.py:490`), её видно в Jira.

### 5. Противоречия

- **F5.1** [low] `skills/tracker/SKILL.md:70`
  > `[text](url)`. Anything else is sent as it is, so wiki markup in plain text still works: `[~login]` mentions a user,
  Утверждение шире того, что делает скрипт и обещает R12 (там проходят только
  wiki-символы `{`, `[`, `|`). Wiki-разметка, которая похожа на Markdown, конвертируется:
  wiki-жирный становится курсивом, wiki-нумерованный список — заголовками. Агент, который
  берёт текст из `get` (тот в wiki markup) и шлёт его без `--wiki`, публикует искажённый
  текст от имени пользователя.
  Fix: «Mentions `[~login]` and a bare `KEY-1` pass as they are; wiki `*bold*` or `#`
  lists need `--wiki`.» Passes: 2/3, подтверждено запуском:
  ```
  to_wiki("this is *bold* in wiki\n# step one\n# step two")
  -> 'this is _bold_ in wiki\nh1. step one\nh1. step two'
  ```

- **F5.2** [low] `skills/tracker/jira.py:357`
  > LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^)\s]+)\)")
  SKILL.md:70 обещает, что ссылки `[text](url)` сохраняются. Ссылка со скобками в адресе
  ломается.
  Fix: разрешить один уровень парных скобок в адресе; добавить тест.
  Passes: 1/3, confirmed — `to_wiki("[a](http://x/y_(z))")` → `'[a|http://x/y_(z])'`.

Других противоречий нет. Сверены SKILL.md, README, R3/R8/R9/R12 и `jira.py`:
- метка экранирована (`jira.py:490`);
- комментарий перехода уходит отдельно, когда на экране нет поля `comment`
  (`jira.py:691`);
- задача уже в целевом статусе: только комментарий;
- `--field description` не конвертируется;
- языки блоков кода — по R12;
- коды выхода 2–12 совпадают с таблицей.

### 6. Дублирование

README повторяет для человека правило записи и правило кода 5 и ссылается на
`skills/tracker/SKILL.md`. Копии не расходятся. BLUEPRINT хранит причины, а не указания
агентам.

### 7. Когда звать человека

SKILL.md:103-105: «as a worker, send the supervisor that line and the command with
`send_message`; as the lead, tell the human. Then wait for the answer if your step cannot
go on». Код 5 останавливает всех через ведущего (`STOP_ALL`, `jira.py:42`). Код 11 даёт
одну попытку исправить запрос, потом агент сообщает. Нарушения нет; F3.1 касается
только условия проверки после сбоя.

### 8. Циклы на повторном визите

Не применимо: потоков нет. Скрипт сам не повторяет («it never retries»).

### 9. Краткость и «почему»

У неочевидных правил есть причины: «one more try can lock the login», «Jira shows every
line break», `# Jira drops update.comment of a transition with no comment field on its
screen.` Пустых фраз проходы не нашли.

### 10. Описания навыков

Навык один, `tracker`. В его описании сказано, когда его брать: «Use whenever your work
touches a task in the tracker». Внешних навыков и `expects` нет.

### 11. Нейтральность к провайдеру

Запуск — `python3 ${SKILL_DIR}/jira.py`, с запасным вариантом для CLI, который не
раскрывает `${SKILL_DIR}` (SKILL.md:19). Имён инструментов CLI нет. `~/.zprofile` и
`security` есть только в README, для человека.

### 12. Безопасность и границы

- Учётные данные не печатаются и уходят только по https или на loopback (`jira.py:247`).
- Редиректы не выполняются, TLS не отключается.
- После 401 или CAPTCHA повтора нет.
- `create` проверяет обязательные поля до POST.
- `link` идемпотентен по `globalId`.
- При сбое комментария после перехода строка говорит «do not run the transition again».
- Удаления нет; запись — по R11.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Коды разделяют окружение (4, 5, 9, 10, 12 — «report it») и ошибку запроса (2, 8, 11 — «fix»). Исключение — F3.4: ошибка окружения (`SSL_CERT_FILE`) выходит как крах, код 1. |
| 2. Work outside a flow, merge without a gate | Git-работы нет. Запись в Jira только так: SKILL.md:25 «Create, transition, comment or link only when your role, your…». |
| 3. Path outside the run's worktree | `${SKILL_DIR}`; `find_config` ищет вверх до первого `.git`, то есть до файла `.git` самого worktree (`jira.py:190`). |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: `dependencies.skills` нет. Собственные записи навыка ограничены правилом SKILL.md:25. |

## Not traced

Ничего. Каждый элемент есть в таблице трассировки BLUEPRINT, R1–R12 прослежены в обе
стороны. Меры бюджета green, раздел 4 BLUEPRINT совпадает с выводом скрипта. Потоков и
скелетов нет (R2, BLUEPRINT.md «Flow skeletons: none»). Мелочь: R10 стоит в списке
после R12.

Для плана 1.1.0, не находки: R3 запрещает assign (BLUEPRINT.md «Nothing else (no
delete, assign, user search,»), а пример `.lado/tracker.yaml` в SKILL.md и README не
содержит `in progress`. Требования T1 и T4 меняют и то и другое.

## Questions for the human

Нет.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не обрабатывает кит без
  `flows/`: `error: kit.yaml: states must be a non-empty mapping` (код 2). Открыто с
  отчёта 1.0.2.
- `[kit-builder]` Шаг `assess` называет отчёт по версии из `kit.yaml`. Если релиз этой
  версии уже прошёл в тот же день, имя совпадает с отчётом релиза, и полная оценка
  переписывает его: здесь `tracker-jira-server-1.0.2-2026-10-09.md`. Прежняя версия файла
  есть в 802c099.
