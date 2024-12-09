# trakt-year-in-review

Generate year in review from Trakt history

## Steps

1. Create `.env` file from `.env.example` file

```bash
cp .env.example .env
```

2. Update trakt user name, trakt client id and year in `.env` file

3. Run below command on full terminal screen

```bash
python generate.py
```

4. Alternatively, You can also pass trakt user name, year and client id in command line argument

```bash
python generate.py user_id 2024 trakt_client_id
```

## Screenshots

![](Screenshot.png)
