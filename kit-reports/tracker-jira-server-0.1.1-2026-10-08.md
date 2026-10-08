# Отчёт о ките: tracker-jira-server 0.1.1

- Дата: 2026-10-08
- Кит: `.` (worktree запуска `improve/tracker-jira-server-2`), путь задан
- Коммит: 03d08f3 (`kit.yaml` всё ещё `version: 0.1.0`, версию ставит релиз; имя отчёта — плановая версия)
- Оценил: критик kit-builder (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-0.1.0-2026-10-08.md`
  (артефакт `assessment`), база — ec8af0b (её называет план),
  `git diff ec8af0b -- kit.yaml README.md BLUEPRINT.md agents flows skills`: 4 файла,
  около 30 строк (jira.py `cmd_get`, `cmd_create`; README «Credentials»; SKILL.md строка
  кода 5; BLUEPRINT разделы 4 и 5).
- Проходы: три прохода я сделал сам, без субагентов, — изменение маленькое. Проход 1:
  SKILL.md и README против плана. Проход 2: код `cmd_create` / `cmd_get` и пути, на которые
  ведут его сообщения (`setting`, строка кода 8 в SKILL.md). Проход 3: BLUEPRINT и тесты,
  затем снова роли текста. Затем полный проход по всем четырём затронутым файлам целиком
  (Re-evaluation 5). Однопроходных находок отброшено: 0; оставлено как подтверждённые: 2
  (F5.1 подтверждена запуском, F9.1 — цитатой и планом), плюс одна из полного прохода в
  «Missed earlier».

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано (у кита нет потоков); `--compare` неприменим, см. «Потоки» |
| b. Рубрика | 2 находки (0 high, 1 medium, 1 low); 10 из 12 критериев без находок; плюс 1 low в «Missed earlier» |
| Охват | повторная оценка изменённого текста, с полным проходом по 4 файлам, которых касается diff (README.md, BLUEPRINT.md, skills/tracker/SKILL.md, skills/tracker/jira.py); тесты: 48, OK |
| Правило остановки | не выполнено: 0 high, 1 medium (F5.1) — совет для ворот релиза, не блок |

Счёт относится только к тому, что названо в строке «Охват»: счёт повторной оценки и счёт
полной оценки не сравнимы.

### `lado kits check .`

```
tracker-jira-server: OK (0 agents, 1 skills, 0 packs and 0 flows)
```

### Скрипт бюджета (код выхода 0)

Системный `python3` без `pyyaml` (`ModuleNotFoundError: No module named 'yaml'`, причина
вне кита); запущен как `uv run --no-project --with pyyaml python3 kit_budget.py .`:

```
# Complexity budget: tracker-jira-server 0.1.0

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

У кита нет потоков (R2), в BLUEPRINT.md нет скелетов («Flow skeletons: none»). Скрипт
потоков не знает такого случая (см. «Found on the way»); супервизор раньше признал сравнение
неприменимым (#601).

```
$ flow_diagram.py . --out kit-reports/tracker-jira-server-0.1.1-2026-10-08
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
$ flow_diagram.py . --compare BLUEPRINT.md
error: kit.yaml: states must be a non-empty mapping   (exit status 2)
```

## Исправить сначала

1. Подсказка `--epic-name` по имени поля только когда `fields.epic_name` не задан; иначе при
   неверной настройке скрипт советует то, что агент уже сделал (F5.1).

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Права на запись в Jira не изменились: SKILL.md «Create, transition,
comment or link only when your role, your step or the human asks for it».

### 2. Передачи между шагами

Не применимо: потоков нет.

### 3. Готовность и исходы

Проверены новые строки кодов 5 и 8 и `get`: у каждого кода в SKILL.md по-прежнему одно
действие; «Comments: none» не меняет кода выхода (тест `test_get_without_comments`).

### 4. Независимая проверка

Не применимо: в ките нет шагов работы; проверку выполняет этот поток (`evaluate`).

### 5. Противоречия

- **F5.1** [medium] `skills/tracker/jira.py:474`
  > if f.get("fieldId") == epic_name or f.get("name", "").lower() == "epic name":
  Если `fields.epic_name` в настройках указывает на другое поле, чем Epic Name этой Jira,
  `create --epic-name …` пишет значение в неверное поле, а сообщение кода 8 снова советует
  `--epic-name` — то, что агент уже дал. Строка 8 в SKILL.md («give them and run again»)
  ведёт его повторить ту же команду или гадать; до 0.1.1 подсказка `--field id=value` с
  верным id вела к успешному созданию. Ошибочная настройка при этом нигде не названа.
  Проверено запуском (настройки `epic_name: customfield_10101`, Jira требует
  `customfield_10200` «Epic Name», команда с `--epic-name Login`):
  `exit 8 … jira.py: creating Epic in TEST needs: Epic Name (customfield_10200): give it with --epic-name '<name>'`.
  Fix: совпадение по имени — только когда настройка не задана:
  `f.get("fieldId") == epic_name or (not epic_name and f.get("name", "").lower() == "epic name")`;
  тогда при неверной настройке остаётся подсказка `--field id=value`. Можно добавить тест
  на этот случай. Passes: 1/3, confirmed

### 6. Дублирование

Новая причина CAPTCHA стоит в двух местах — README «Credentials» и строка 5 в SKILL.md;
это разные читатели (человек и агент), и формулировки совпадают:
«after failed logins (on some servers after the first)». Не находка.

### 7. Когда звать человека

Не изменилось: коды 3 и 5 по-прежнему ведут к отчёту («report it; the user fixes the file»,
«The lead tells every agent to stop using Jira until the human says it is fixed»).

### 8. Циклы на повторном визите

Не применимо: потоков нет. (Повтор `create` после кода 8 — см. F5.1.)

### 9. Краткость и «почему»

- **F9.1** [low] `BLUEPRINT.md:130`
  > Output of the kit-budget script on the built kit (0.1.1 changes; kit.yaml still says 0.1.0 until the release):
  План: «sections 1–4 unchanged»; автор изменил заголовок раздела 4. После релиза (kit.yaml
  0.1.1) скобка «kit.yaml still says 0.1.0 until the release» станет неверной.
  Fix: вернуть строку к «on the built kit (0.1.1):» в шаге релиза, или оставить прежнюю
  строку, как велит план. Passes: 1/3, confirmed (`git diff ec8af0b -- BLUEPRINT.md`, план)

### 10. Описания навыков

`description` навыка `tracker` не менялся; зависимостей-навыков нет.

### 11. Нейтральность к провайдеру

Изменённый текст не называет ни одного CLI; путь к скрипту — `${SKILL_DIR}`.

### 12. Безопасность и границы

«never retried» сохранено: README «A wrong password is never retried», SKILL.md строка 5
«stop using Jira and report it». Https-проверка и область записи не тронуты.

## Known holes

| Known hole | Находка, или как кит это решает |
|---|---|
| 1. Red check sent back with no environment cause considered | Без изменений: окружение — коды 4, 9, 10 с причиной; ошибка настройки — код 3. F5.1 — случай, где неверная настройка выглядит как недостающее поле. |
| 2. Work outside a flow, merge without a gate | Нет работы с git; запись в Jira ограничена SKILL.md («only when your role, your step or the human asks for it»). |
| 3. Path outside the run's worktree | Без изменений: `find_config` останавливается на первом `.git`. |
| 4. Verdict without a severity threshold | Не применимо: нет рецензента. |
| 5. Dependency skill that writes or asks where its role must not | Не применимо: нет `dependencies.skills`. |

## Not traced

Ничего. Новые строки раздела 5 BLUEPRINT ссылаются на пробный запуск (`trial-test-server`);
все меры бюджета зелёные; скелетов потоков нет, потому что нет потоков (R2). Отклонение
раздела 4 от плана — F9.1.

## Изменения из плана

| Изменение плана | Статус | Доказательство |
|---|---|---|
| Epic без Epic Name → подсказка `--epic-name`; без «a Epic» | RESOLVED (см. F5.1 о краевом случае) | `jira.py:475` `give it with --epic-name '<name>'`; сообщение `creating %s in %s needs`; тест `test_create_epic_without_name_points_to_epic_name` |
| `get` без комментариев → «Comments: none» | RESOLVED | `jira.py:405` `print("\nComments: none")`; тест `test_get_without_comments` |
| CAPTCHA: «after failed logins (on some servers after the first)» в README и SKILL.md; строка 401 скрипта, если там «a few» | RESOLVED | README.md:39, SKILL.md:121; в скрипте «more failed logins», не «a few» — оставлено, как разрешает план |
| `kit.yaml`: версия в шаге релиза | RESOLVED (не трогали) | `version: 0.1.0` |
| BLUEPRINT: три строки раздела 5 | RESOLVED | BLUEPRINT.md:150-152 (5d632bc) |

Предыдущий отчёт: 0 находок, поэтому нечего отмечать.

## Cut rules

| Удалённое правило (файл:строка в базе) | Где теперь |
|---|---|
| README.md:39 «after a few failed logins Jira asks for a CAPTCHA» → «never retried» | README.md:39-40, правило то же, причина уточнена |
| jira.py:468-469 «give each with --field id=value» | jira.py:477 для каждого поля, кроме Epic Name |

Правил не потеряно.

## Missed earlier

- **F9.2** [low] `skills/tracker/SKILL.md:35`
  > | create a task | `create --type <type> --summary '<text>' [--description -] [--epic KEY-9] [--field id=value]` |
  В строке использования `create` нет `--epic-name`, хотя ниже сказано «An epic also needs
  `--epic-name`», а 0.1.1 теперь на него указывает. Агент, читающий только таблицу, его не
  увидит до кода 8.
  Fix: добавить `[--epic-name '<name>']` в эту строку. Passes: full pass, confirmed

## Questions for the human

Нет.

## Found on the way

- `[kit-builder]` Скрипт потоков `kit-budget` (`flow_diagram.py`) не знает кита без
  `flows/`: читает `kit.yaml` как поток и выходит с кодом 2 (`error: kit.yaml: states must be
  a non-empty mapping`), и с `--out`, и с `--compare`. Всё ещё открыто; это не файл кита.
- `[kit-builder]` Скрипты `kit-budget` требуют `pyyaml`, которого нет в системном
  `python3` этой машины; запуск через `uv run --with pyyaml` работает. В SKILL.md
  `kit-budget` стоит назвать эту зависимость.
