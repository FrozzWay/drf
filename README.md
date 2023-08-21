# Django Rest Framework application
Тестовое задание включает:

- Авторизация через имитацию отправки смс-кодов. Первый запрос на ввод номера телефона и отправку смс-сообщения. Второй запрос ввод кода. Записывает в БД новых пользователей.
- Для каждого пользователя создается инвайт-код, который может быть указан другим пользователем в своем профиле единожды.
- Список номеров телефонов пользователей, которые ввели инвайт-код текущего пользователя включен в его профиль.

Процесс авторизации завершается получением JWT токена.<br> **Пройти авторизацию и получить токен можно на html-странице `/login` (django-templates), либо через API.**<br><br>
[Коллекция Postman-запросов для тестирования](https://drive.google.com/uc?export=download&id=1hnTFXEV0Fd7_ksSCobNagFPZjTZAdWlu&export=download&confirm=t). Включает скриптованные запросы на создание 1+5 пользователей.<br>
Развернут на [виртуальной машине](https://drf.okunevad.cloud) (https://drf.okunevad.cloud).
>На моей VM запущены два сервиса в контейнерах `docker compose`, за переадресацию запросов и установку TSL-соединения отвечает отдельный контейнер nginx (по заголовку HOST). Вся композиция развертывается с помощью `ansible-playbooks` (подход Infrastructure as code).

## Auth API
⪢ `[POST] /login`  - первый запрос на отправку смс-сообщения. Возвращает `sms_token` для предоставления во втором запросе. Зашифрован, lifetime=5m, содержит в полезной нагрузке отправленный смс-код.
```json
{
    "phone": "+79876543210",
    "name": "superuser",
    "is_privileged": true
}
```
⪢ `[POST] /login?sms_confirmation=1`  - второй запрос на отправку смс-сообщения. Возвращает JWT bearer_token.
```json
{
    "sms_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIn0..0U6cyfDYLm4P7QqsJnS_GQ.JXmKzK7xaII572v6FB_iIWE3SG89d0L0CMdHYq4PSnNHw2khqkHc1QhjYWv8BCPfLRGLJtVltuvn2oJ75GxaTaukhwQmLvARvjetaTjv59IjS4ZhvZkmvNsScIpX81eyz5FiQ1ReOScczYeIc4ll8zuWD6NEMgTdXDT6cWteunu5sgRJ16aAUZI8WlBXW_f9M-YciOhTjoEnzwNHxMQPzW8RiEA2MlXxMOZqV6nSBWsQfCpRzrZfugCDYceNADzTLydrXDU25TTw3eYK8D61w1Uj6oR3gntiYpi_OW8bgBb6SO-CfnFxALvC5THyjLD4a6hrmd6_JeKkgWzwQO6KLVUbjS9TR0JkaNStiAsyn1RM5PjFQOxGZVPoFDwXj4FX.rCHK6lF22qlyifDn_lvvZ6-fZRgibg1pca0BbXcCIS4",
    "sms_code": "0000"
}
```
## Profiles API
⪢ `[GET] /profile` - собственный профиль через авторизацию заголовком Authorization: Bearer <token>.<br>
⪢ `[GET] /profile/<int:pk>` - профиль пользователя с id. Требует `PrivilegeAccessPermission` (проверяет флаг is_privileged у отправляющего запрос пользователя).
```json
{
    "id": 69,
    "name": "superuser",
    "phone": "+79876543210",
    "is_privileged": true,
    "invitation_code": "d6cdee",
    "invited_by": null,
    "invited_users_phones": ["+7(832) 482-3870", "+7(922) 592-2366"]
}
```
⪢ `[POST] /profile/invitation` - ввести реферальный код (защищен авторизацией).
```json
{
    "invitation_code": "0fe5d6"
}
```
⪢ `[DELETE] /profile/<int:pk>` - удалить пользователя с id. Требует `PrivilegeAccessPermission`.<br>
⪢ `[DELETE] /profiles` - удалить всех пользователей. Требует `PrivilegeAccessPermission`.
