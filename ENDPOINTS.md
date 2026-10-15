     # My Festival API — endpoint-dokumentti / endpoint document

**Tekijä / Author:** <Kentta Teemu>
**Julkinen osoite / Public URL:** `https://festival-api-festival-kenttate.2.rahtiapp.fi`
**GitHub:** `https://github.com/KenTee05/festival-api`
**Tarkistimen tulos / Checker result:** ""Testing https://festival-api-festival-kenttate.2.rahtiapp.fi

[PASS] GET /api/artists returns 200
[PASS]   Content-Type is application/json
[PASS]   response is a non-empty JSON list
[PASS]   items have artist_id and name
[PASS] GET /api/days returns day_id + date
[PASS] GET /api/stages returns stage_id + name
[PASS] GET /api/artists/3/events returns a JSON list
[PASS] GET unknown artist returns 404
[PASS] GET /api/timetable returns a JSON list
[PASS] GET /api/timetable?day=2026-07-17 returns only that day
[PASS]   rows are in time order (starts)
[PASS] GET timetable with bad date returns 400
[PASS] POST with missing fields returns 400
[PASS] POST with bad foreign key returns 400
[PASS] POST with bad start_dt format returns 400
[PASS] POST with valid body returns 201 + event_id
[PASS]   new event is returned by GET /api/artists/{id}/events
[PASS] DELETE /api/events/18 returns 204
[PASS]   deleted event is gone
[PASS] DELETE same event again returns 404

20/20 checks passed""
---

## 1. Endpointit / Endpoints

| Metodi / Method | Polku / Path | Onnistuu / Success | Virheet / Errors |
|---|---|---|---|
| GET | `/api/artists` | 200 | – |
| GET | `/api/days` | 200 | – |
| GET | `/api/stages` | 200 | – |
| GET | `/api/artists/{id}/events` | 200 | 404 |
| GET | `/api/timetable?day=YYYY-MM-DD` | 200 | 400 |
| POST | `/api/events` | 201 | 400 |
| DELETE | `/api/events/{id}` | 204 | 404 |

## 2. Esimerkit / Examples

Kirjoita jokaisesta endpointista esimerkkikutsu ja (lyhennetty) vastaus. Malli:
For every endpoint, write an example call and a (shortened) response. Example:

### GET /api/artists

```bash
curl https://festival-api-festival-kenttate.2.rahtiapp.fi/api/artists
```
```json
[
  {"artist_id": 1, "country": null, "name": "Dua Lipa"},
  {"artist_id": 2, "country": null, "name": "The Weeknd"},
  {"artist_id": 3, "country": null, "name": "Billie Eilish"},
  {"artist_id": 4, "country": null, "name": "Imagine Dragons"},
  {"artist_id": 5, "country": null, "name": "David Guetta"}
]


```

### GET /api/artists/{id}/events
```bash
curl https://festival-api-festival-kenttate.2.rahtiapp.fi/api/artists/1/events
```
```json
[
  {"event_id": 3, "artist_id": 3, "stage_id": 1, "day_id": 1, "event_type_id": 1, "start_time": "18:00", "end_time": "19:00"}
]

```
Tuntematon id / unknown id → `<tilakoodi ja runko / status code and body>`

### GET /api/timetable?day=YYYY-MM-DD
```bash
curl "https://festival-api-festival-kenttate.2.rahtiapp.fi/api/timetable?day=2026-07-17"
```
```json
[
  {"event_id": 1, "artist_id": 1, "stage_id": 1, "day_id": 1, "event_type_id": 1, "start_time": "20:00", "end_time": "21:00"},
  {"event_id": 2, "artist_id": 2, "stage_id": 2, "day_id": 1, "event_type_id": 1, "start_time": "18:00", "end_time": "19:00"}
]

```
Virheellinen päivämäärä / invalid date → `<tilakoodi ja runko / status code and body>`

### POST /api/events
```bash
curl -X POST https://festival-api-kenttate.2.rahtiapp.fi/api/events \
     -H "Content-Type: application/json" \
     -d '{"artist_id": 3, "stage_id": 1, "day_id": 2, "start_dt": "2026-07-18 15:00:00"}'
```
```json
{"event_id": 18, "message": "Event created successfully"}

```
Puuttuva kenttä / missing field → `<{"error": "Missing fields: stage_id, day_id, start_dt"}>` · Olematon artist_id / unknown artist_id → `<{"error": "Integrity error: FOREIGN KEY constraint failed"}>`

### DELETE /api/events/{id}
```bash
curl -X DELETE https://festival-api-kenttate.2.rahtiapp.fi/api/events/17
```
Onnistuu / success → `<204 (tyhjä runko)>` · Tuntematon id / unknown id → `<404 {"error": "Event not found"}>`

## 3. Julkaisu Rahtiin / Deploying to Rahti (3–6 lausetta / sentences)

<Laitoin valmiin koodin GitHub-repositorioon. Rahdissa loin oman projektin nimellä festival-csc-tunnus ja valitsin Import from Git sekä Dockerfile-strategian. Rahti haki koodin GitHubista, rakensi kontin imagen, käynnisti Podin ja loi julkisen HTTPS-Route-osoitteen. Julkisen osoitteen löysin Networkin-näkymässä olevasta Routes näkymästä. Yksi ongelma oli, että ensimmäisellä kerralla tiedostot olivat alikansiossa githubissa – korjasin rakenteen juureen ja tein uuden buildin, minkä jälkeen API alkoi toimia>

## 4. Tietoturva / Security (2–4 lausetta / sentences)

<Ennen oikeaa tuotantokäyttöä rajapinta tarvitsisi autentikoinnin (esim. API-avain tai token), rate limitingin ja mahdollisesti lokituksen. SQL-injektio on estetty käyttämällä parametrisoituja kyselyitä. Käyttäjän syötettä ei koskaan liitetä suoraan SQL-merkkijonoon. Lisäksi POST-endpoint validoi pakolliset kentät ja päivämäärämuodon ennen tietokantaan kirjoittamista.>
