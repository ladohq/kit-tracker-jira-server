# Отчёт о ките: tracker-jira-server 0.1.1

- Дата: 2026-10-08
- Кит: `.` (worktree запуска `improve/tracker-jira-server`), путь задан
- Коммит: 27b7350 (`kit.yaml` `version: 0.1.1`)
- Оценил: критик kit-builder (слои a и b)
- Режим: полная оценка (шаг `assess` запуска `improve` к v1.0.0). Прежний отчёт этого
  файла (706ef18) — повторная оценка, а не полная, поэтому он только фон; git хранит его.
- Проходы: три независимых субагента, каждый со скиллами `kit-rubric` и `lado-kit-format`
  и папкой кита, без `kit-reports/`. Проход 1: kit.yaml и README, затем SKILL.md, jira.py,
  BLUEPRINT. Проход 2: скрипт команда за командой против таблиц SKILL.md, затем README,
  BLUEPRINT. Проход 3: SKILL.md как его читает агент, затем BLUEPRINT по требованиям R1–R11,
  README, jira.py; ему были даны два наблюдения пробы в сессии LADO. Однопроходных находок
  отброшено: 4 (текст задач и комментариев как данные, а не указания; повтор после кода 8
  без предела; «fix the request once» для недоступного перехода; правило кода 8 трижды
  в SKILL.md) — вред в файлах не показан. Оставлено как подтверждённые: 8.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков, R2); в BLUEPRINT.md нет скелетов («Flow skeletons: none») |
| b. Рубрика | 15 находок (0 high, 7 medium, 8 low); 7 из 12 критериев без находок |
| Охват | полная оценка всего кита, 5 файлов текста (kit.yaml, README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 48, OK |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 0.1.1

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

У кита нет потоков (R2), скелетов в BLUEPRINT.md нет. Скрипт потоков не знает такого
случая (см. «Found on the way»), диаграмм нет:

```
$ flow_diagram.py . --out kit-reports/tracker-jira-server-0.1.1-2026-10-08
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
$ flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. Решить с человеком R10: засчитывается ли проба на тестовой Jira вместо пробы на CRM3, и
   записать решение в BLUEPRINT (F12.1).
2. Одно правило для «report it»: когда работник ждёт ответа супервизора, а когда идёт дальше
   без трекера; убрать противоречие строки кода 12 (F5.1).
3. После кода 9 — больше не обращаться к Jira, пока не скажут, что она отвечает; сообщение
   скрипта не должно звать к немедленному `get`/`search` (F5.3).
4. Сообщение о коде 5 должно само просить ведущего остановить всех агентов: ведущий может не
   иметь навыка (F7.1).
5. Назвать поддерживаемые версии честно — `create` работает с 8.4 (F5.2) — и сказать, что
   токены 8.14+ не поддерживаются (F5.4).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Право навыка на запись сказано: SKILL.md:25 «Reading is always fine.
Create, transition, comment or link only when your role, your».

### 2. Передачи между шагами

Не применимо: потоков и артефактов нет; результат скрипта — stdout и Jira.

### 3. Готовность и исходы

- **F3.1** [medium] `skills/tracker/jira.py:474`
  > if f.get("fieldId") == epic_name or f.get("name", "").lower() == "epic name":
  Подсказка `--epic-name` выбирается и по имени поля, когда `fields.epic_name` не задан или
  задан неверно. Не задан: следующая команда с `--epic-name` падает с кодом 3
  (`jira.py:459` `setting(config, "fields", "epic_name", "--epic-name")`), и по строке кода 3
  агент останавливается и ждёт, что человек поправит файл, хотя первое сообщение уже назвало
  id поля, которое приняло бы `--field <id>=<name>`. Задан неверно: подсказка повторяет то,
  что агент уже дал (прежняя F5.1 отчёта 706ef18, всё ещё открыта).
  Fix: `--epic-name` подсказывать только при `epic_name and f.get("fieldId") == epic_name`;
  во всех других случаях — `give it with --field <fieldId>=<name>` с настоящим id. Тест на
  оба случая. Passes: 1/3, confirmed (проход 2 запуском против тестовой Jira тестов:
  `8 … give it with --epic-name '<name>'`, затем `3 jira.py: --epic-name needs
  'fields.epic_name' in .lado/tracker.yaml`; прежний отчёт — запуском с неверным id)
- **F3.2** [low] `skills/tracker/jira.py:332`
  > return Failure(REFUSED, "Jira refused the request (%d)%s" % (code, detail))
  Всякий другой 4xx, в том числе 429 ограничения частоты Data Center, становится кодом 11,
  а строка 11 SKILL.md велит «fix the request once»: агент правит верный запрос.
  Fix: 429 — в код 12 (или своим сообщением «rate limited: report it, do not retry»).
  Passes: 1/3, confirmed (проход 2 запуском: `11 jira.py: Jira refused the request (429)`;
  в `_http_failure` нет ветки для 429)
- **F3.3** [low] `skills/tracker/SKILL.md:39`
  > | link a branch, commit or pull request | `link KEY-1 <url> [--title '<text>']` |
  Не сказано, откуда берётся URL и что делать, когда его нет (репозиторий без remote). В
  пробе агент сам догадался дать хеш в комментарии; другой может выдумать URL, а
  `cmd_link` (`jira.py:555`) шлёт любой.
  Fix: строка под таблицей: «the URL is the branch's or commit's page on the repository's
  host; with no remote there is nothing to link: give the branch and hash in a `comment`».
  Passes: 1/3, confirmed (артефакт `/trial-lado-session`, наблюдение 1)

### 4. Независимая проверка

Не применимо: потоков нет; удалений и других необратимых действий навык не делает
(R3 «no delete»). Расхождение BLUEPRINT с релизом — F12.1.

### 5. Противоречия

- **F5.1** [medium] `skills/tracker/SKILL.md:128`
  > | 12 | Jira itself failed (5xx) | report it; whether your step can go on without the tracker is your step's decision |
  Строки 112–113 велят работнику послать строку супервизору «and wait for its answer» для
  всякого «report it»; строка 12 разрешает шагу идти дальше. Агенты будут то ждать, то
  продолжать (то же для кодов 7 и 9).
  Fix: в фразе «To report» одно правило: после отчёта ждать ответа, если шаг не может идти
  без трекера, иначе продолжать; из строки 12 убрать вторую половину. Passes: 3/3
- **F5.2** [medium] `skills/tracker/jira.py:440`
  > base = "issue/createmeta/%s/issuetypes" % urllib.parse.quote(project)
  Кит обещает «8.x» (kit.yaml:4, README.md:3, BLUEPRINT R1, R7), а `create` использует только
  постраничный createmeta, который, по памяти всех трёх проходов, появился в Jira 8.4. На
  8.0–8.3 `create` получит 404 и сообщит «project … not found: check 'project'» (код 7) или
  «not Jira's base address» (код 4) — человек пойдёт чинить верную настройку. Факт о версии
  в файлах не проверяется; проба на 8.13 его не опровергает.
  Fix: «8.4 or newer» в kit.yaml, README, BLUEPRINT R1/R7; или запасной путь
  `issue/createmeta?projectKeys=…&expand=projects.issuetypes.fields` при 404.
  Passes: 3/3
- **F5.3** [medium] `skills/tracker/jira.py:38`
  > APPLIED = ("; the change may have been applied: check with get or search before running "
  После таймаута записи сообщение скрипта (и SKILL.md:130) зовёт сразу проверить `get` или
  `search` — новый запрос к Jira, которая не ответила, ещё 30 с ожидания. Это расходится
  со строкой кода 9 («report it») и с «wait for its answer» (SKILL.md:113). В пробе так и
  вышло: два запроса подряд, минута до ответа.
  Fix: «…: once Jira answers again, check with get or search before running it again»; в
  SKILL.md:130 — после кода 9 ничего не слать в Jira, пока не скажут, что она отвечает.
  Passes: 1/3, confirmed (артефакт `/trial-lado-session`, наблюдение 2; `jira.py:284-285`
  добавляет `APPLIED` к сообщению таймаута)
- **F5.4** [medium] `README.md:24`
  > LADO's agents inherit. Jira Server before 8.14 has no personal access tokens, so the
  Фраза подсказывает, что на 8.14+ можно взять токен, а скрипт шлёт только
  `Basic user:password` (`jira.py:239-240`); Data Center принимает токен как `Bearer`.
  Токен в `JIRA_PASSWORD` даст 401 — код 5, неудачный вход, который может включить CAPTCHA.
  Fix: одно предложение: «Personal access tokens (8.14+) are not supported: the script
  uses Basic auth with the password.» Passes: 1/3, confirmed (`jira.py:240`
  `self.auth = "Basic " + …`; Bearer нигде)
- **F5.5** [low] `BLUEPRINT.md:41`
  > `[a, b]` lists, `#` comments; anything else stops it with the path, the line and what is
  Проверки `_validate` (`jira.py:148-169`) — неизвестный ключ, не список, не карта — не
  называют строку: `p.yaml: unknown key 'status'; known keys: …`.
  Fix: передать номер строки в `_validate` для ключей верхнего уровня, или ослабить R6.
  Passes: 1/3, confirmed (`where = path + ": "` в `_validate`, без номера строки)

### 6. Дублирование

README повторяет для человека правила SKILL.md (CAPTCHA, метка, область записи) со
ссылкой на SKILL.md; формулировки совпадают. В SKILL.md правило живёт в одном месте.
Не находка.

### 7. Когда звать человека

- **F7.1** [medium] `skills/tracker/SKILL.md:121`
  > | 5 | credentials refused, or Jira wants a CAPTCHA | stop using Jira and report it: Jira asks for a CAPTCHA after failed logins (on some servers after the first), so one more try can lock the login. The lead tells every agent to stop using Jira until the human says it is fixed |
  Указание ведущему стоит в навыке, а ведущий процессного кита со своим списком `skills:`
  навыка не получает (README.md:9-10 советует список только ролям, которым трекер нужен).
  Работник шлёт лишь строку и команду (SKILL.md:112), сообщение кода 5 об остановке других
  агентов молчит — следующий агент может заблокировать вход.
  Fix: в сообщение скрипта о коде 5 (или в отчёт работника) добавить «tell every agent to
  stop using Jira until the human says it is fixed»; в README — ведущему со списком
  `skills:` добавить `tracker`. Passes: 2/3
- **F7.2** [low] `BLUEPRINT.md:80`
  > Open, decided at the trial (not in v0.1.0):
  Пробы прошли, а открытые вопросы (ограничения сверх R11; факты CRM3) не закрыты и не
  перенесены; R3 и R6 всё ещё говорят «in v0.1.0» (строки 28, 45). Решение человека об
  ограничениях агентов нигде не записано.
  Fix: записать решение триажа (или версию, в которой решат) и заменить «v0.1.0» на
  описание без версии. Passes: 3/3

### 8. Циклы на повторном визите

Не применимо: потоков нет. Повторы агента ограничены: скрипт «never retries», код 11
«fix the request once».

### 9. Краткость и «почему»

- **F9.1** [low] `skills/tracker/SKILL.md:35`
  > | create a task | `create --type <type> --summary '<text>' [--description -] [--epic KEY-9] [--field id=value]` |
  В строке нет `--epic-name`, хотя строка 45 говорит «An epic also needs `--epic-name`»;
  агент, копирующий строку таблицы, получит код 8 (прежняя F9.2, всё ещё открыта).
  Fix: добавить `[--epic-name '<name>']`. Passes: 1/3, confirmed (`grep -nF` строки 35:
  `--epic-name` в ней нет)

### 10. Описания навыков

`description` (SKILL.md:3-7) говорит, что умеет навык и когда («Use whenever your work
touches a task in the tracker»); навык один, имя `tracker` задано соглашением (R2);
`dependencies.skills` нет.

### 11. Нейтральность к провайдеру

Скрипт вызывается через `${SKILL_DIR}` с запасным правилом («If your CLI does not expand
`${SKILL_DIR}`, use the folder this SKILL.md is in»); инструменты CLI не названы, только
`send_message` LADO; в jira.py нет абсолютных и домашних путей.

### 12. Безопасность и границы

- **F12.1** [medium] `BLUEPRINT.md:76`
  > real Jira (project CRM3), only with the human's yes; v1.0.0 and the official marketplace
  R10 ставит v1.0.0 и маркетплейс после пробы на настоящей Jira (CRM3); журнал изменений
  (строки 150–152) и артефакты записывают пробы на тестовой Jira 8.13.19. Релиз 1.0.0 сейчас
  либо пропускает проверку, одобренную человеком, либо молча меняет R10.
  Fix: человек решает; решение записать в R10 (с источником) и в журнал. Passes: 3/3
- **F12.2** [low] `BLUEPRINT.md:9`
  > Clens (Jira project CRM3), but the kit is for any project.
  Публичный репозиторий официального маркетплейса будет называть внутренний проект клиента
  и его ключ (также строки 8, 76, 84). R1 убирает такие имена из навыка и скрипта, но не из
  BLUEPRINT.
  Fix: по решению человека заменить на «a corporate Jira Server 8.13 project». Passes: 3/3
- **F12.3** [low] `README.md:38`
  > Check the login once by hand before a session: `curl -u "$JIRA_USER" "$JIRA_URL/rest/api/2/myself"`.
  `curl -u` без пароля просит ввести его руками; одна опечатка — неудачный вход, а строки
  39–40 говорят, что это может включить CAPTCHA, от которой проверка и должна защитить.
  Fix: проверять тем же, чем агенты, например `python3 skills/tracker/jira.py search
  'project = ABC' --max 1`, или `curl -u "$JIRA_USER:$JIRA_PASSWORD"`.
  Passes: 1/3, confirmed (README.md:39 «A wrong password is never retried, since after
  failed logins (on some servers after the first) Jira»)
- **F12.4** [low] `README.md:15`
  > lado kits add https://github.com/ladohq/kit-tracker-jira-server
  `lado-kit-format` («Publishing») велит назвать репозиторий `lado-kit-<name>` с темой
  `lado-kit`; здесь (и в `git remote`) — `kit-tracker-jira-server`.
  Fix: переименовать в `lado-kit-tracker-jira-server` до pull request в маркетплейс, или
  записать в BLUEPRINT, почему нет. Passes: 2/3

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Решено: коды разделяют окружение (3, 4, 5, 9, 10, 12 — «report it») и ошибку запроса (2, 8, 11 — «fix»), SKILL.md:115-128. F5.1, F5.3 — о том, что делать после отчёта; F3.2 — 429 попадает в «ошибку запроса». |
| 2. Work outside a flow, merge without a gate | Нет git-работы и merge; запись в Jira ограничена SKILL.md:25-27 («only when your role, your step or the human asks for it»). |
| 3. Path outside the run's worktree | Решено: `find_config` останавливается на первом `.git` (`jira.py:179`), в worktree это его собственный файл `.git`; README.md:46 «Each project commits its settings to its own repository, so every worktree has them». |
| 4. Verdict without a severity threshold | Не применимо: рецензента нет. |
| 5. Dependency skill that writes or asks where its role must not | `dependencies.skills` нет. Свой навык пишет в Jira и достаётся каждой роли без `skills:`, в том числе только читающей; область записи по умолчанию это покрывает; работники говорят только с супервизором (SKILL.md:112-113). |

## Not traced

- R10 не выполнено как написано: проба на CRM3 не записана (F12.1).
- R6 обещает строку в каждой ошибке настроек; часть ошибок её не даёт (F5.5).
- R7/R1 «8.x» против createmeta 8.4+ (F5.2).
- Все элементы кита названы требованиями (таблица раздела 3); мер бюджета выше green нет;
  скелетов потоков нет, потому что нет потоков (R2).

## Questions for the human

1. R10: засчитывается ли проба на тестовой Jira 8.13.19 (скрипт и живая сессия LADO) вместо
   пробы на CRM3 для v1.0.0? Совет: да, если CRM3 тоже 8.13 и её проверят первым делом
   после релиза; записать это в R10.
2. Ограничения агентов сверх R11 (удаление, закрытие, чужие задачи): совет — ничего сверх
   R11 в 1.0.0 (удаления в ките нет), записать решение в BLUEPRINT (F7.2).
3. Наблюдения пробы: совет — взять оба (F3.3 одна строка про `link` без remote; F5.3 — не
   обращаться к Jira после кода 9).
4. Оставлять ли в публичном BLUEPRINT имена Clens/CRM3 (F12.2)? Совет: убрать.
5. Переименовать ли репозиторий в `lado-kit-tracker-jira-server` до маркетплейса (F12.4)?
   Совет: да, пока ссылок мало.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не знает кита без
  `flows/`: читает `kit.yaml` как поток и выходит с кодом 2 (`error: kit.yaml: states must
  be a non-empty mapping`), и с `--out`, и с `--compare`. Всё ещё открыто.
