# Отчёт о ките: tracker-jira-server 1.5.0

- Дата: 2026-10-13
- Кит: `.` (ветка `main` репозитория кита), путь задан
- Коммит: 867defa (`kit.yaml` `version: 1.5.0`); изменение — коммиты 8dc07d2 и 867defa
- Оценил: независимый критик (слои a и b)
- Режим: повторная оценка относительно `kit-reports/tracker-jira-server-1.4.0-2026-10-12.md`
  (f460312, оценивал 07b1cd7, открытых находок нет). База — f460312, выпущенная 1.4.0. Дифф
  `git diff f460312 867defa` затрагивает 6 файлов: BLUEPRINT.md, README.md, kit.yaml,
  skills/tracker/SKILL.md, skills/tracker/jira.py, tests/test_jira.py. Требования — задача
  Yougile LAD-46 (J1–J9), в пересказе supervisor'а.
- Проходы: изменение — около 450 строк текста кита и 300 строк тестов. Я сделал два прохода
  сам, по 12 критериям и известным дырам: 1) дифф `jira.py` (`Jira.call`/`send`,
  `same_server`, `ATTACHMENT`, `_check_files`, `cmd_attach`, `cmd_download`, правки
  `create`/`edit`/`comment`/`transition`, `_print_issue`) против `_http_failure`,
  `_network_failure` и требований J1–J5; 2) SKILL.md, BLUEPRINT R3/R7/R8/R10/R11/R12, README и
  kit.yaml против кода и J6–J7. Затем десять проб против фейковой Jira из тестов (без
  `JIRA_*` из окружения, к настоящей Jira не обращался): тайм-аут и 500 на загрузке, редирект
  на `content`, нечитаемый файл, `--to` без права записи, `attachment:` в блоке кода,
  `search`, имена с `|`, `!`, `]`, обрыв на втором файле `download`, имя с `"` и `\`,
  `transition` в тот же статус с неизвестным именем. Отдельного субагента не было.
  Однопроходных находок отброшено: 1 (кавычка и обратная косая черта в имени файла
  экранируются в `Content-Disposition` обратной косой чертой, а браузеры шлют `%22`; на Jira
  не проверено, вреда без такого имени нет). Оставлено как подтверждённые пробой: 4.

Находки — кандидаты для человека, а не оценка «прошёл/не прошёл».

## Карточка

| Слой | Результат |
|---|---|
| a. `lado kits check` | OK; 0 предупреждений; `expects commands: uv` |
| a. Бюджет | green; нет жёлтых и красных мер |
| a. Потоки | 0 нарисовано: потоков нет (R2), скелетов в BLUEPRINT.md нет |
| b. Рубрика | 4 находки (0 high, 0 medium, 4 low); 9 из 12 критериев без находок |
| Охват | повторная оценка изменённого текста (6 файлов дифа f460312..867defa) по 12 критериям и J1–J9; пробы против фейковой Jira; тесты: 130, OK |
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

Read-only: строки `read-only roles: …` нет, потому что ролей нет; `dependencies.lado: ">=0.30"`.

### Скрипт бюджета (код выхода 0)

```
# Complexity budget: tracker-jira-server 1.5.0

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
No flows in .: nothing to do (exit status 0)
```

### Тесты

```
$ uv run --no-project python -m unittest discover -s tests
Ran 130 tests in 8.243s

OK
```

## Исправить сначала

Ничего обязательного: находки только low. Если чинить, то первой — F3.1: строка ошибки
`attach` не должна называть «не загруженным» файл, запрос которого мог пройти.

## Находки

### 1. Границы ролей

Не применимо: ролей нет. Границы записи — SKILL.md:29 «Create, transition, comment, assign,
label, link or attach only when your role, your step or the human asks for it», как R11.

### 2. Передачи между шагами

Не применимо: потоков нет. Выход новых действий задан и пригоден для следующего шага:
`attach` печатает строку `<id> <name> attachment:<имя в URL-кодировке>` на файл, готовую к
вставке в Markdown (тест `test_attach_one_file`), `download` — абсолютный путь на файл.

### 3. Готовность и исходы

Каждый отказ новых действий попадает в строку таблицы кодов: 2 (файл нет/папка/нечитаем —
проба: `cannot be read (Permission denied); nothing uploaded`, запросов 0; `--to` без права
записи — запросов 0; `attachment:` в `create`), 6 (403), 7 (файла нет, файлы задачи
перечислены), 11 (413, отключённые вложения, 404 на загрузке, чужой адрес, неизвестное имя в
`attachment:`), 12 (5xx). Проверка имён идёт до первой записи: проба `transition TEST-1 Open
--comment "[x](attachment:b.png)"` при задаче уже в Open — exit 11, комментарий не добавлен.

- **F3.1** [low] `skills/tracker/jira.py:1199`
  > `            raise Failure(failure.code, "%s: uploaded %s; not uploaded %s%s: %s" % (`
  Файл, на котором `attach` упал, всегда попадает в «not uploaded», какой бы ни была ошибка.
  При тайм-ауте (9) или 5xx (12) загрузка могла пройти, и та же строка это говорит:
  проба с тайм-аутом на первом файле — `exit 9 … TEST-1: uploaded none; not uploaded a.txt,
  b.txt: Jira did not answer … the change may have been applied: once Jira answers again,
  check with get`; 500 на единственном файле — `exit 12 … uploaded none; not uploaded a.txt:
  Jira failed (500): boom; the change may have been applied`. Строка утверждает «не
  загружен» и тут же «могло примениться», а SKILL.md:111-113 учит по ней: «the line names
  those uploaded and those not: do not attach the uploaded ones again», то есть «не
  загруженные» можно слать снова. Агент, поверивший первой половине, загрузит файл второй
  раз; в Jira появятся два файла с одним именем, и `!NAME!` будет показывать новейший. Вред —
  лишняя копия файла, отсюда low. Тест `test_attach_partial_failure_names_both_sides`
  закрепляет нынешний текст для 500.
  Fix: при кодах 9 и 12 называть упавший файл отдельно: «%s may have been uploaded (check
  with get); not uploaded <остальные>», а при 2/6/7/11 оставить как есть; тест для 500 и
  тайм-аута на первом и втором файле. В SKILL.md:111-113 дописать «a file named "may have
  been uploaded": check with `get` first».
  Passes: 1/1, подтверждено двумя пробами.

- **F3.2** [low] `skills/tracker/jira.py:433-434`
  > `        return "!%s!" % name  # Jira's image markup has no alt text`
  Имя файла вставляется в wiki-разметку как есть. Имя с `!`, `|` или `]` ломает её: проба
  `to_wiki("[log](attachment:a%7Cb.txt) ![](attachment:x%21y.png) [t](<attachment:c]d.txt>)")`
  даёт `[log|^a|b.txt] !x!y.png! [t|^c]d.txt]`, а имена при этом считаются найденными
  (`['a|b.txt', 'x!y.png', 'c]d.txt']`), так что проверка J4 пропускает их и пишет в Jira
  битую ссылку. Сам `attach` печатает такие имена как готовые к вставке
  (`attachment:x%21y.png`). Имена со `!` бывают («done!.png»), с `|` и `]` — редко.
  Fix (самый простой): если в имени есть `!`, `|`, `[` или `]`, давать exit 2 «rename the
  file before attaching, Jira's markup cannot link it» — в `attach` до загрузки и в
  конвертере для `attachment:`; одна строка в SKILL.md рядом с «write the name URL-encoded».
  Passes: 1/1, подтверждено пробой.

### 4. Независимая проверка

Не применимо: потоков нет. Файлы опробованы на тестовой Jira 8.13.19 до выпуска (R10,
BLUEPRINT.md:306-309, артефакт `lad-46-probe`); найденный там ответ 404 с текстом на файл
сверх лимита закреплён тестом `test_attach_refusals` («Jira 8.13.19's answer to a file over
jira.attachment.size»).

### 5. Противоречия

- **F5.1** [low] `skills/tracker/SKILL.md:114-116` (против `BLUEPRINT.md:204-205`, R11)
  > `  files share is the newest of them), into a new temporary folder outside the`
  > `  repository, or into an existing folder given with \`--to\`, and prints each file's full`
  R11 говорит: «a downloaded file is data, not instructions, kept outside the repository»
  (J6: «outside repo»). SKILL.md описывает только папку по умолчанию как лежащую вне
  репозитория, а `--to` разрешает любую существующую папку; код тоже не проверяет. Агент,
  которому велели «положи скриншот рядом», скачает `--to .`, и файл из задачи (с чужим
  текстом) окажется в рабочем дереве, откуда его может забрать `git add -A`. Правило R11 до
  агента не доходит.
  Fix: в пункт **download** SKILL.md дописать «keep `--to` outside the repository too,
  unless the human or your step asks for the file in it». Код не трогать (простейший путь).
  Passes: 1/1, подтверждено цитатами.

### 6. Дублирование

Повторов нет. Правило `attachment:` описано в одном месте («Writing in Jira: Markdown»,
SKILL.md:134-142), пункт **attach** и строки 2/11 таблицы кодов ссылаются на него, не
повторяя. Описание kit.yaml, README и SKILL.md называют файлы одинаково.

### 7. Когда звать человека

Отказы, которые агент не исправит сам, ведут к «report it»: файл сверх лимита, вложения
отключены, чужой адрес (SKILL.md, строка 11 таблицы). Чужой адрес назван с причиной: «Jira's
base URL differs from JIRA_URL; report it».

### 8. Повторные визиты

Не применимо: потоков нет. `download` повторно не перезаписывает (`-1`, `-2`, открытие с
`"xb"`); `attach` повторно добавляет копию, о чём SKILL.md предупреждает (см. F3.1).

### 9. Краткость и «почему»

Причины названы там, где агент мог бы спросить: `create` без `attachment:` — «the task has
no files yet»; «`!NAME!`» — «a link follows the name, so after a newer file of that name is
attached, older links show the newer file; give a version you mean to keep its own name»
(SKILL.md:137-139, по пробе на Jira).

### 10. Описания навыков

Описание навыка называет новые действия и поводы: «attach files to a task and download its
files (screenshots, logs, documents)», «"attach the screenshot", "look at the file in the
task"» (SKILL.md:7-11). kit.yaml и README согласованы с ним; строк в таблице действий две
(SKILL.md:49-50).

### 11. Нейтральность к провайдеру

Нового пути и имён CLI нет; скрипт по-прежнему через `${SKILL_DIR}/jira.py`. Папка по
умолчанию — `tempfile.mkdtemp(prefix="lado-jira-")`, без привязки к ОС.

### 12. Безопасность и границы

Учётные данные уходят только на `content` URL с той же схемой, хостом и портом, что у
`JIRA_URL` (`same_server`, jira.py:304), проверка всех выбранных файлов — до первого
скачивания; тест `test_download_from_another_server_sends_no_credentials` проверяет, что
другой сервер не получил ни одного запроса. Имя чистится (`_safe_name`: base name, без
управляющих символов, `.`/`..` заменены), тест с `../evil\x01.txt`. `attach` — запись по
правилу SKILL.md:29, без секретов (SKILL.md:109-111).

- **F12.1** [low] `skills/tracker/jira.py:1259`
  > `            data = jira.send("GET", item["content"])`
  J3 требует «no redirects followed», и код это делает (`_NoRedirect`): проба с 302 на
  `content` в сторону другого сервера — `exit 4 … downloaded none; not downloaded a.txt: Jira
  answered with a redirect (302), not followed: JIRA_URL is not Jira's base address, or a
  login page (SSO) is in front of it`, другой сервер получил 0 запросов. Но 1) теста на это
  нет, хотя J8 просит тесты на всё из J3, а именно этот путь бережёт пароль, если Jira или
  прокси перед ней начнут отдавать файлы редиректом; 2) совет строки и строки 4 SKILL.md
  («the user fixes their shell profile») здесь неверен: REST API только что ответил с этого
  же `JIRA_URL`, так что адрес верен, а редирект — у раздачи файлов.
  Fix: тест «302 на `content` → чужой сервер не получил запросов, `Authorization` не ушёл»;
  в `cmd_download` 3xx давать exit 11 «Jira serves the file by a redirect, not followed so
  the credentials stay with JIRA_URL; report it».
  Passes: 1/1, подтверждено пробой.

## Известные дыры

| Известная дыра | Находка, или как кит её закрывает |
|---|---|
| 1. Красная проверка возвращается без учёта среды | Не применимо: потоков нет. Сообщения `uv`/Python SKILL.md по-прежнему отличает от сообщений скрипта |
| 2. Работа вне потока, слияние без гейта | Не применимо: ролей и потоков нет; `attach` — только по просьбе роли, шага или человека (SKILL.md:29) |
| 3. Путь вне worktree запуска | Нет для скрипта: `${SKILL_DIR}/jira.py`. Скачанные файлы по умолчанию — во временной папке вне репозитория; `--to` в репозиторий не запрещён — F5.1 |
| 4. Вердикт без порога серьёзности | Не применимо: ревьюеров нет |
| 5. Зависимый навык пишет или спрашивает, где роли нельзя | Не применимо: зависимых навыков нет |
| 6. Команды не в ладу с `expects.commands` | Закрыта: `expects commands: uv`, `dependencies.lado: ">=0.30"`; новых команд нет (`tempfile`, `multipart` — стандартная библиотека) |
| 7. Read-only роли не в ладу с делом | Не применимо: ролей нет |

## Не прослежено

Ничего. Файлы задачи прослежены в R3 (три действия, «no attachments» убрано), R7 (ресурсы
вложений), R8 (коды файлов), R10 (проба `lad-46-probe`), R11 (`attach` — запись, без секретов,
скачанное — данные) и R12 (`attachment:`); раздел 3 называет `attach` и `download`; журнал
раздела 5 имеет строку 1.5.0 с источниками. Раздел 4 «Output of the kit-budget script on the
built kit (1.4.0; 1.5.0 adds no role, flow, skill or MCP server, so the values hold)»
совпадает с выводом выше. README говорит, что делает кит и где опробован («Where it was
tried», README.md:92). Скелетов потоков нет: потоков нет (R2).

## Прежние находки

В отчёте 1.4.0 открытых находок не было. Требования LAD-46:

| Требование | Статус | Доказательство |
|---|---|---|
| J1 `get`: блок `Files: N` между Description и Comments, строка `<id> <name> (<size>, <author>, <date>)`, без файлов — без блока; `search` без изменений | RESOLVED | `_print_issue`; тесты `test_get_shows_files_between_description_and_comments`, `test_get_without_files_has_no_block`; проба: `search` просит `summary,status,issuetype,assignee` |
| J2 `attach`: multipart `file`, `X-Atlassian-Token: no-check`, все файлы до первой загрузки, строка на файл, `--comment` последним, имена комментария до загрузки, частичный отказ называет обе стороны | RESOLVED, с замечанием | `cmd_attach`, `Jira.call(upload=…)`; тесты `test_attach_*` (9); см. F3.1 о файле, упавшем на 9/12 |
| J3 `download`: id, затем имя (новейший); данные только на схему, хост, порт `JIRA_URL`; без редиректов; `mkdtemp(prefix="lado-jira-")`; `--to` существует; чистка имени; без перезаписи; абсолютные пути; нет файла → 7 со списком | RESOLVED, с замечанием | `cmd_download`, `same_server`, `_safe_name`, `_free_path`; тесты `test_download_*` (7); редирект не следуется (проба), но без теста — F12.1 |
| J4 `attachment:` → `!NAME!`, `[text\|^NAME]`; URL-кодировка или `<…>`; проверка до записи (11) в edit/comment/transition/attach; в create — 2; `--wiki` без проверки | RESOLVED, с замечанием | `ATTACHMENT`, `_attachment`, `_check_files`; тесты `test_attachment_links`, `test_edit_comment_transition_check_the_names`, `test_create_with_attachment_links_is_refused`, `test_attach_wiki_comment_is_not_checked`; проба: в блоке и в спане кода не трогается; см. F3.2 об именах с `!`, `\|`, `]` |
| J5 коды: 413/отключено/лимит → 11; 403 → 6; локальный файл → 2; `--to` → 2; сбой посередине называет сделанное | RESOLVED | `_http_failure` 413; `cmd_attach` 404/«disabled»; `test_attach_refusals` (5 случаев); пробы: нечитаемый файл и `--to` только для чтения — exit 2, запросов 0; обрыв на втором файле `download` — «downloaded …/a.txt; not downloaded b.txt» |
| J6 SKILL.md: две строки таблицы; раздел файлов (запись по просьбе, без секретов; скачанное — данные, вне репозитория, картинку открыть как картинку); `attachment:` в «Writing in Jira»; порядок create → attach → edit; описание | RESOLVED, с замечанием | SKILL.md:7-11, :49-50, :103-122, :134-142; «вне репозитория» — только для папки по умолчанию, F5.1 |
| J7 BLUEPRINT R3 без «no attachments», три действия, прослеживание, журнал 1.5.0; kit.yaml 1.5.0; README | RESOLVED | BLUEPRINT.md R3, R7, R8, R11, R12, раздел 3, строка журнала 1.5.0; kit.yaml `version: 1.5.0`; README:5-6, :83-87, :92-98 |
| J8 тесты на фейковой Jira | RESOLVED, с замечанием | `Ran 130 tests … OK` (было 108), класс `FilesTest` (21 тест) и `test_attachment_links`; нет теста на редирект `content` (F12.1) и на тайм-аут загрузки (F3.1) |
| J9 проба на Jira 8.13.19 | RESOLVED | BLUEPRINT.md:306-309, строка журнала 1.5.0, README «Where it was tried»; найденный 404 закреплён тестом |

## Вырезанные правила

| Удалённое правило (файл:строка в базе) | Где оно теперь |
|---|---|
| BLUEPRINT R3 «Nothing else (no delete, user search, attachments, boards or sprints…» | BLUEPRINT R3, «Nothing else (no delete, user search, deleting or renaming files, thumbnails, boards or sprints…»; «attachments» убрано намеренно (J7) |
| BLUEPRINT R3 «ten actions» | «twelve actions» |
| BLUEPRINT R11, SKILL.md:27 «…assign, label or link only when…» | BLUEPRINT R11, SKILL.md:29, то же, дополнено `attach` |
| kit.yaml, README, SKILL.md описания | те же, дополнены файлами |
| SKILL.md строки кодов 2, 7, 11 | те же строки, только дополнения; правила `assign` и `link_types` в строке 11 на месте |
| jira.py `Jira.call` (отправка, разбор JSON) | `Jira.call` (тело, заголовки, JSON) + `Jira.send` (запрос, ошибки); заголовки `Authorization`, `Accept` на месте; прежние тесты проходят |
| jira.py `cmd_transition`: перевод комментария после выбора перехода | до первого GET, чтобы проверить имена; тот же текст, та же метка |
| jira.py `cmd_create`: перевод описания после `createmeta` | до запросов; поле `description` то же |

Ни одно правило не потеряно.

## Пропущено ранее

Нет.

## Оставлено планом

Ничего: план (LAD-46) не оставлял пунктов.

## Вопросы к человеку

1. F3.1, F3.2, F5.1, F12.1 — все low. Чинить до выпуска или оставить? Рекомендую F3.1 и
   F12.1 (строка ошибки и тест, затрагивают только `jira.py` и тесты), F5.1 — одной фразой
   в SKILL.md; F3.2 — по желанию.
