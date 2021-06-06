# ium-project

## Service
Proste przedstawienie działąnia serwisu znajduje się w notebooku `./Service showcase.ipynb`.

### Wymagania
- python 3.8
- fastapi
- uvicorn
- sqlalchemy
- joblib
- pandas
- sklearn
- xgboost

Baza SQLite znajdująca się pod ścieżką `service/sql_app.db` posiadająca tabelę o następującą strukturze:
```
CREATE TABLE "ab-test-logs" ("id" integer NOT NULL,"query_id" integer NOT NULL,"query" text NOT NULL,"model_name" text NOT NULL,"result" text NOT NULL, PRIMARY KEY (id));
```

### Deploy
1. Uruchom
```
uvicorn service.main:app
```

### Development
1. Uruchom
```
uvicorn service.main:app --reload
```

2. Otwórz stonę z dokumentacją API (Sagger)
http://127.0.0.1:8000/docs
