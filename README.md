# Year in Review using Trakt

Generate year in review from Trakt history

## Steps

1. Make your Trakt profile as public from Trakt's account setting.

2. Create `.env` file from `.env.example` file

```bash
cp .env.example .env
```

3. Update trakt user name, trakt client id and year in `.env` file

4. Run below command on full terminal screen

```bash
python generate.py
```

5. Alternatively, You can also pass trakt user name, year and client id in command line argument

```bash
python generate.py user_id 2024 trakt_client_id
```

6. Make your Trakt profile as private again from Trakt's account setting.

## Screenshots

![](Screenshot.png)
