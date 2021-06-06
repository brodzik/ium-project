# ium-project

## Opis katalogów

**data -** dane które pierwotnie otrzymaliśmy do analizy. Okazały się błędne.

**dana_new -** drugi, już poprawny zestaw danych.

**data_preprocessed -** `data_new` po preprocessing-u (m.in. oczyszczenie, kodowanie).

**models -** gotowe modele.

**notebooks -** notebooki w których znajduje się analiza danych, preprocessing, tworzenie modeli.

**service -** kod serwisu implementujący testy AB na stworzonych modelach.

## Service
Proste przedstawienie działąnia serwisu znajduje się w notebooku `./Service showcase.ipynb`.

### Wymagania
1. Python 3.8

2. Pakiety:
- fastapi
- uvicorn
- sqlalchemy
- joblib
- pandas
- sklearn
- xgboost

3. Baze SQLite znajdująca się pod ścieżką `service/sql_app.db` posiadającą tabelę o następującą strukturze:
```
CREATE TABLE "ab-test-logs" ("id" integer NOT NULL,"query_id" integer NOT NULL,"query" text NOT NULL,"model_name" text NOT NULL,"result" text NOT NULL, PRIMARY KEY (id));
```

### Deploy
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
