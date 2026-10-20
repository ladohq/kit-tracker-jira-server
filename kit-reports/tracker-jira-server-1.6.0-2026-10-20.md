# Отчёт о ките: tracker-jira-server 1.6.0

- Дата: 2026-10-20
- Кит: `.` (worktree запуска `improve/tracker-jira-server`, ветка
  `lado/kit-tracker-jira-server/improve-tracker-jira-server`), путь задан
- Коммит: 8ebb8ca (`kit.yaml` `version: 1.6.0`). Визит 1 оценивал 6f175cf (отчёт 66d8918),
  визит 2 — ee2dc59 (отчёт a5a7cd5).
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.5.0-2026-10-20.md`
  (85d77cb, оценивал ceddd32); база — ceddd32, коммит, который план называет для своего
  отчёта. План — артефакт `plan`, сборка — `build-report`, проба — `trial-1.6.0`.
- Визит 3, после пробы `field` на тестовой Jira 8.13.19 (`trial-1.6.0`, на a5a7cd5: всё по
  плану, кроме T1 [medium] — `Fields:` в `get` и список «usable names» exit 3 включали
  имена не текстовых полей, в том числе системное `description`). С визита 2 (a5a7cd5 →
  8ebb8ca): 8377daa (BLUEPRINT R3, R7, журнал 1.6.0 — F5.3, F5.4 визита 2; BACKLOG — F12.3),
  8ebb8ca (jira.py: `jira_fields`, `usable_fields`; тесты: 151). README, kit.yaml и SKILL.md
  не менялись.
- Проходы визита 3: три по правкам a5a7cd5..8ebb8ca и их окружению, по 12 критериям и
  известным дырам: мой (дифф целиком против SKILL.md, BLUEPRINT и пробы), субагент A
  (T1 по `get`, `edit`, exit 3 с настройками пробы; крайние случаи: только epic_*, `/field`
  отвечает 500/403, id без поля в Jira, перечитывание после `edit`), субагент B (BLUEPRINT
  R3, R7, R8, журнал против кода и SKILL.md; сверка с tracker-yougile 94a29f5; проверка
  вырезанных правил по `--word-diff`). Затем полный проход субагентом по BLUEPRINT.md и
  jira.py целиком (SKILL.md — как образец сказанного агентам). Пробы — против фейковой
  Jira тестов и закрытого порта localhost, переменные `JIRA_*` сняты; к настоящей Jira
  никто не обращался. Однопроходных находок отброшено: 0; оставлено как подтверждённые: 2
  (F5.7 — сверкой с yougile.py 94a29f5:1269-1270; F5.8 — по разделу 3 BLUEPRINT).
- Визиты 1 и 2: см. версии этого отчёта 66d8918 и a5a7cd5 (git хранит их); их итог — в
  «Прежние находки».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; жёлтых и красных мер нет |
| a. Потоки | 0 нарисовано: потоков нет (R2); в BLUEPRINT.md скелетов нет |
| b. Рубрика | визит 3: 3 новых находки в изменённом тексте (0 high, 0 medium, 3 low: F5.5, F5.6, F5.7) + 2 в «Пропущено ранее» (low: F4.1, F5.8); T1 пробы, F5.3 и F5.4 визита 2 RESOLVED; F12.3 — в BACKLOG по решению человека; F9.1 оставлена человеком; 10 из 12 критериев без открытых находок |
| Охват | повторная оценка изменённого текста (визиты 1–3: ceddd32..8ebb8ca, в визите 3 — BLUEPRINT.md и jira.py) с полным проходом по файлам правки; тесты: 151, OK |
| Правило остановки | выполнено: 0 high, 0 medium в изменённом тексте |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
expects commands: uv
```

Expects: `expects commands: uv`. Предупреждения `expects.commands needs LADO 0.30 or newer`
нет: `dependencies.lado: ">=0.30"`.

Read-only: строки `read-only roles: …` нет — ролей нет; `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.6.0

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
$ flow_diagram.py . --compare BLUEPRINT.md
no flows in . or BLUEPRINT.md: nothing to do (exit status 0)
```

### Тесты и следы проекта

```
$ uv run --no-project python -m unittest discover -s tests
Ran 151 tests in 9.576s

OK
```
Следов проекта правки визита 3 не добавили (полный проход: в jira.py и SKILL.md нет
`LAD-`, `waiting`, `polygon`); grep визита 1 по skills, README, kit.yaml, tests и BACKLOG
был пуст.

## Исправить сначала

Блокирующих нет; правило остановки выполнено. Если править до тега — по одной строке:

1. README «Where it was tried» — строка о пробе `field` 1.6.0 (F4.1).
2. R7: точный ключ типа вместо «ending `:textfield`» (F5.5).

## Находки

Визит 3: только находки в изменённом тексте, открытые сейчас. Находки визитов 1 и 2 — в
«Прежние находки».

### 1. Границы ролей

Не применимо: ролей нет; правило записи — одно, SKILL.md:30-31.

### 2. Передачи между шагами

Не применимо: потоков нет. Вывод `field` не менялся.

### 3. Готовность и исходы

Каждый новый путь отказа даёт код из таблицы: имя не из `fields` или не того типа — 3
(«report it; the user fixes the file»), сбой `/field` — его код (500 → 12, 403 → 6; проба
субагента A); после PUT в `edit` сбой перечитывания — «changed, but reading the task back
failed (do not run it again)».

### 4. Независимая проверка

Не применимо: потоков нет. `field` опробован на тестовой Jira 8.13.19 (`trial-1.6.0`);
правка T1 проверена тестами, повторно на Jira — нет (вопрос 2).

### 5. Противоречия

- **F5.5** [low] `BLUEPRINT.md:177` (R7)
  > `  text field (`schema.custom` ending `:textfield`; a system field, a multi-line or an`
  R7 пускает любой `schema.custom`, оканчивающийся на `:textfield`, а код — только точный
  ключ Atlassian (jira.py:64 `TEXT_FIELD = "com.atlassian.jira.plugin.system.customfieldtypes:textfield"`,
  сравнение на равенство в `usable_fields` и `cmd_field`). Поле чужого плагина проходит по
  R7 и отказано кодом, а сообщение противоречит себе (проба A и полного прохода,
  `schema.custom: com.example.plugin:textfield`): «is of type textfield, not a custom
  single-line text field (textfield): report it, the user fixes the file». Автор по R7
  ослабит проверку; пользователь не поймёт, что не так.
  Fix: в R7 — «`schema.custom` is `com.atlassian.jira.plugin.system.customfieldtypes:textfield`»;
  по желанию — в сообщении весь ключ, когда он задан. Passes: 3/3

- **F5.6** [low] `skills/tracker/jira.py:1138`
  > `    fields = jira_fields(jira)`
  Правка T1 перенесла запрос `GET /rest/api/2/field` до проверки имени. Имя не из
  настроек и `epic_*` раньше давали exit 3 без запроса — так и в tracker-yougile («a name
  the settings lack: before any request»); теперь зависят от ответа Jira. Проба B (закрытый
  порт): `field ABC-1 relase` — exit 9 «send Jira nothing more until you are told it
  answers again», хотя SKILL.md:100 обещает «A name the settings lack, `epic_link` or
  `epic_name` (they serve `create`), … is exit 3». Агент получает остановку вместо ошибки
  настроек. Fix: проверить имя по `named_fields(config)` и `EPIC_FIELDS` до `jira_fields`;
  `/field` читать только для списка пригодных имён и проверки типа. Passes: 2/3

- **F5.7** [low] `BLUEPRINT.md:98` (R3)
  > `  the line only when `fields` has usable names; `search` does not. `label` stays Jira's`
  После T1 строка `Fields:` зависит от типов полей: если в `fields` только имена не
  текстовых полей, `get` здесь строки не печатает, а tracker-yougile 94a29f5 печатает
  `Fields: none` всякий раз, когда `fields` не пуст (yougile.py:1269-1270 `if
  config["fields"]: print("Fields: %s" % (… or "none"))`). Процесс-кит на обоих трекерах
  при тех же настройках видит «нет строки» и «Fields: none». SKILL.md:104 («when `fields`
  has such names») совпадает с кодом этого кита — расхождение только между китами.
  Fix: печатать строку, когда `named_fields(config)` не пуст (`Fields: none`, если пригодных
  нет), и сказать это в R3; либо назвать разницу в R3 как намеренную. Passes: 1/3,
  confirmed (jira.py:676 и :708 `if named:` после `usable_fields`; цитата yougile.py выше)

Остальное согласовано: R3 «for each usable name (a custom textfield, R7)», R7, R8 и журнал
1.6.0 совпадают с кодом (F5.3, F5.4 визита 2 RESOLVED).

### 6. Дублирование

Правило типа — в одном месте кода (`usable_fields`, им пользуются и `get`, и список exit
3); в BLUEPRINT — R7, R3 и R8 ссылаются на него.

### 7. Когда звать человека

Exit 3 по-прежнему «report it; the user fixes the file».

### 8. Повторные визиты

Не применимо: потоков нет.

### 9. Краткость и «почему»

Новые комментарии несут причину (jira.py:673-674 «a system field (description) would
print a whole text there»). F9.1 оставлен человеком.

### 10. Описания навыков

Не менялись.

### 11. Нейтральность к провайдеру

Нового CLI-специфичного текста нет.

### 12. Безопасность и границы

Чтение `/field` — чтение; запись по-прежнему только со значением или `--clear` и по
правилу SKILL.md:30-31; непригодное имя ничего не пишет и задачу не читает (проба A).

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Навык отличает среду (4, 5, 9, 10, 12; сообщения `uv`/Python) от запроса (2, 8, 11) |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и слияний нет; запись — по SKILL.md:30-31 |
| 3. Путь вне worktree запуска | `--to` внутри репозитория и основной копии — exit 2; подмодуль — BACKLOG.md:4 (F12.3, решение человека); новых путей нет |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; jira.py других CLI не запускает |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего блокирующего; бюджет green; потоков и скелетов нет. Прослеживание R11 в разделе 3 —
F5.8 («Пропущено ранее»).

## Прежние находки

Визит 2 (отчёт a5a7cd5, коммит ee2dc59) и проба:

| Находка | Статус | Доказательство |
|---|---|---|
| F5.3 [medium] R7 описывал старую проверку типа | RESOLVED | BLUEPRINT.md:176-178 «usable only a custom single-line text field (… a system field, a multi-line or an option field is not)»; остаток — точность ключа, F5.5 |
| F5.4 [low] строка журнала 1.6.0 | RESOLVED | BLUEPRINT.md:388 «R8: a field of another type (a system field included) exit 3, not on the edit screen or refused exit 11; release-gate fixes: …», источники — отчёты 66d8918, a5a7cd5, `trial-1.6.0` |
| F12.3 [low] подмодуль | оставлен в BACKLOG по решению человека | BACKLOG.md:4 |
| T1 [medium] пробы: `Fields:` и «usable names» включали не текстовые поля | RESOLVED | `usable_fields` (jira.py:1103-1107) берёт только `custom == textfield`; `_read_issue` (jira.py:673-678) и `_field_id` (jira.py:1111) — через него; проба A с настройками пробы: `Fields: release = 0.42.0`, textarea и `description` в запрос задачи не попали; неизвестное имя — exit 3 «usable names: release», задача не читается; только epic_* — запроса `/field` нет; тесты (151) |

Визит 1 (отчёт 66d8918): F12.1, F3.1, F5.1, F5.2, F12.2 и «пропущено ранее» F5.3, F3.2 —
RESOLVED на визите 2, правки визита 3 их не тронули (проверка типа стала только строже).
F9.1 — оставлена человеком. Отчёт 85d77cb: все 6 RESOLVED на визите 1.

План (артефакт `plan`): все пункты RESOLVED; проба на тестовой Jira проведена
(`trial-1.6.0`: запись, чтение в `get`, замена, очистка, уже так, отказы exit 2 и 3 — всё
✅, кроме T1, теперь исправленного).

## Вырезанные правила

| Удалённое правило (файл:строка в базе a5a7cd5) | Где оно теперь |
|---|---|
| BLUEPRINT R3:97 «for each usable name set on the task» | та же строка, уточнено «(a custom textfield, R7)» |
| BLUEPRINT R7:176-177 «`schema.type == "string"`, not a multi-line or option field» | R7:176-178, строже: только custom textfield; многострочные и списочные исключены, как прежде |
| журнал 1.6.0 «R8: `field`'s exit 11» | та же строка: «a field of another type … exit 3, not on the edit screen or refused exit 11» |
| jira.py `_field_id`: список имён из `named_fields` | jira.py:1111, из `usable_fields` (сужен намеренно, T1) |
| jira.py `cmd_field`: `known = [f for f in jira.call("GET", "field") …]`, «this Jira has no field» | jira.py:1138-1142, то же сообщение exit 3; запрос перенесён до проверки имени — F5.6 |

Ни одно правило не потеряно.

## Пропущено ранее

- **F4.1** [low] `README.md:102`
  > `release. 1.5.0 (files): `attach` of a PNG and a PDF, `get` with `Files:`, `download` with`
  Раздел «Where it was tried» говорит, что каждый выпуск, добавляющий действие, пробуется
  на тестовой Jira, но называет только 1.5.0; 1.6.0 добавил `field`, опробованный в
  `trial-1.6.0` (R10, BLUEPRINT.md:358-361, строка журнала). Человек по README не узнает,
  что `field` пробовали и на чём. Раздел не входил в дифф. Fix: строка «1.6.0 (`field`):
  write, read in `get`, replace, clear, already so and the refusals on a single-line text
  field; a textarea and a system field refused (exit 3)». Passes: 2/3 (мой проход и A)

- **F5.8** [low] `BLUEPRINT.md:348`
  > `- R11: `tracker` skill.`
  С 1.6.0 правило R11 — уже и код: `download --to` внутри репозитория или основной копии —
  exit 2 (`find_repository`, jira.py:226-250), с тестами
  `test_download_into_the_repository_is_refused` и
  `test_download_into_the_main_checkout_of_a_worktree_is_refused`; обратная проверка и
  строка `jira.py` раздела 3 (BLUEPRINT.md:334, «R3, R4, R5, R6, R7, R8, R9, R12») R11 не
  называют. Fix: «R11: `tracker` skill, `jira.py`, `tests/test_jira.py`» и R11 в строках
  `jira.py` и тестов. Passes: full pass, confirmed

Обе не блокируют и не идут в правило остановки.

## Оставлено планом

- **F9.1** [low] `skills/tracker/SKILL.md:93` — оставлена по решению человека на гейте
  выпуска (визит 1).

## Вопросы к человеку

1. F4.1 (README, строка о пробе 1.6.0) и F5.5 (R7, точный ключ) — по одной строке; внести
   до тега? Рекомендую да: README — то, что человек видит о пробах.
2. Правку T1 пробовали только тестами. Повторить `get` на тестовой Jira с настройками
   `trial-1.6.0` (release, notes, summary_sys) до тега? Рекомендую да: одна команда, поля
   и TEST-1 там остались.
3. F5.6 и F5.7 (порядок запроса `/field`; `Fields: none` против отсутствия строки, как у
   tracker-yougile) — low; рекомендую в BACKLOG вместе с пунктом про `--summary`/`--title`.
