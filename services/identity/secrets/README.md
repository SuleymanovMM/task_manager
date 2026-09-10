# JWT-ключи

Это dev/demo-ключи для быстрого запуска Docker Compose. В продакшене не использовать и приватные ключи в Git не коммитить.

Сгенерировать новую пару:

```bash
./scripts/generate_keys.sh
```

PowerShell:

```powershell
./scripts/generate_keys.ps1
```

`private.pem` в `.gitignore` и не коммитится. После клонирования (или перегенерации пары) сначала выполните скрипт выше, затем скопируйте `public.pem` в `services/project/secrets/`, `services/task/secrets/` и `services/notification/secrets/` — эти сервисы хранят только публичный ключ и проверяют токены локально им.
