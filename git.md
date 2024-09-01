### Git Cheat Sheet: Основные Операции

#### 1. Инициализация проекта с Git
- Команда в консоли: git init
- PyCharm Hotkey: 
  - Windows/Mac: VCS → Enable Version Control Integration...

#### 2. Клонирование удалённого репозитория
- Команда в консоли: git clone <URL>
- PyCharm Hotkey:
  - Windows/Mac: VCS → Get from Version Control

#### 3. Добавление изменений для коммита
- Команда в консоли: git add <файл/папка> или git add . (все файлы)
- PyCharm Hotkey:
  - Windows: Ctrl + K
  - Mac: Cmd + K

#### 4. Создание коммита
- Команда в консоли: git commit -m "Сообщение коммита"
- PyCharm Hotkey:
  - Windows: Ctrl + K (в одном окне с добавлением)
  - Mac: Cmd + K (в одном окне с добавлением)

#### 5. Просмотр статуса изменений
- Команда в консоли: git status
- PyCharm Hotkey:
  - Windows: Alt + 9, затем 4
  - Mac: Cmd + 9, затем 4

#### 6. Отправка изменений в удаленный репозиторий (Push)
- Команда в консоли: git push
- PyCharm Hotkey:
  - Windows: Ctrl + Shift + K
  - Mac: Cmd + Shift + K

#### 7. Получение изменений из удаленного репозитория (Pull)
- Команда в консоли: git pull
- PyCharm Hotkey:
  - Windows: Ctrl + T
  - Mac: Cmd + T

#### 8. Создание новой ветки
- Команда в консоли: git branch <имя_ветки>
- PyCharm Hotkey:
  - Windows/Mac: Щелкните на текущую ветку в правом нижнем углу → New Branch

#### 9. Переключение на другую ветку
- Команда в консоли: git checkout <имя_ветки>
- PyCharm Hotkey:
  - Windows/Mac: Щелкните на текущую ветку в правом нижнем углу → выберите ветку из списка

#### 10. Слияние веток (Merge)
- Команда в консоли: 
  1. Переключитесь на основную ветку: git checkout <основная_ветка>
  2. Выполните слияние: git merge <ветка_с_изменениями>
- PyCharm Hotkey:
  - Windows/Mac: Щелкните правой кнопкой на ветке → Merge into Current

#### 11. Просмотр истории коммитов
- Команда в консоли: git log
- PyCharm Hotkey:
  - Windows: Alt + 9, затем 5
  - Mac: Cmd + 9, затем 5

#### 12. Создание удалённого репозитория и привязка его к локальному
- Команда в консоли: 
  1. Добавить удалённый репозиторий: git remote add origin <URL>
  2. Отправить в удалённый репозиторий: git push -u origin master

#### 13. Удаление ветки
- Команда в консоли: git branch -d <имя_ветки>
- PyCharm:
  - Windows/Mac: Щелкните правой кнопкой на ветке → Delete

#### 14. Создание и переключение на новую ветку в одной команде
- Команда в консоли: git checkout -b <имя_ветки>

### Краткие советы
- Ветки: Используйте ветки для разделения работы над различными фичами или задачами. После завершения работы сливайте ветку в основную и удаляйте её.
- Коммиты: Пишите осмысленные сообщения коммитов, чтобы другие разработчики (и вы сами в будущем) могли понять, какие изменения были внесены.
- Push/Pull: Всегда старайтесь получать последние изменения перед началом работы (Pull) и делайте push после завершения работы.

### Работа с Git в PyCharm
- Интеграция: PyCharm тесно интегрирован с Git, что позволяет выполнять практически все команды через интерфейс IDE.
- Конфликты: Если возникают конфликты при слиянии веток, PyCharm предложит удобный инструмент для их разрешения.
- Просмотр изменений: В PyCharm легко увидеть, какие строки были изменены в файлах, и сделать коммит только нужных изменений.