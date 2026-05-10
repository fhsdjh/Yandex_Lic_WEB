import logging
import random

import requests
from flask import Flask, jsonify, request

from data import db_session
from data.stats import Stat

GEO_URL = "https://geocode-maps.yandex.ru/1.x/"
GEO_KEY = "8013b162-6b42-4997-9691-77b7074026e0"

CITIES = {
    "москва": "1540737/daa6e420d33102bf6947",
    "париж": "1652229/f77136c2364eb90a3ea8",
    "нью-йорк": "1652229/728d5c86707054d4745f",
    "пекин": "997614/86b8a1f2b8e23d8a9bea",
    "каир": "965417/0f2d1e1f7c94dc0d6a02",
}
WIN = "<speaker audio='alice-sounds-game-win-1.opus'>"
LOSE = "<speaker audio='alice-sounds-game-loss-3.opus'>"

ctx = {}

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def get_country(city):
    try:
        params = {"apikey": GEO_KEY, "geocode": city, "format": "json"}
        r = requests.get(GEO_URL, params=params, timeout=5).json()
        feat = r["response"]["GeoObjectCollection"]["featureMember"][0]
        return feat["GeoObject"]["metaDataProperty"]["GeocoderMetaData"][
            "AddressDetails"]["Country"]["CountryName"]
    except Exception:
        return None


def find_name(req):
    for ent in req["request"].get("nlu", {}).get("entities", []):
        if ent["type"] == "YANDEX.FIO":
            return ent["value"].get("first_name")
    return None


def get_stat(uid):
    sess = db_session.create_session()
    s = sess.query(Stat).filter(Stat.alice_uid == uid).first()
    if not s:
        s = Stat(alice_uid=uid, score=0, rounds=0)
        sess.add(s)
        sess.commit()
    return sess, s


def reply(req, text, tts=None, end=False, image=None, btns=None):
    res = {
        "session": req["session"],
        "version": req["version"],
        "response": {"text": text, "tts": tts or text, "end_session": end},
    }
    if image:
        res["response"]["card"] = {"type": "BigImage", "image_id": image,
                                   "title": "Что за город?"}
    if btns:
        res["response"]["buttons"] = [{"title": b, "hide": True} for b in btns]
    return jsonify(res)


@app.route("/", methods=["GET"])
def health():
    return "OK"


@app.route("/post", methods=["POST"])
def post():
    req = request.json
    uid = req["session"]["user_id"]
    sess, stat = get_stat(uid)

    if req["session"]["new"]:
        ctx[uid] = {"stage": "ask_name", "city": None}
        return reply(req, "Привет! Это игра «Угадай страну». Как тебя зовут?")

    state = ctx.setdefault(uid, {"stage": "ask_name", "city": None})
    text = req["request"].get("original_utterance", "").lower().strip()

    if state["stage"] == "ask_name":
        name = find_name(req) or (text.split()[0] if text else None)
        if not name:
            return reply(req, "Не расслышала имя, повтори, пожалуйста.")
        stat.name = name.title()
        sess.commit()
        city = random.choice(list(CITIES))
        state.update(stage="ask_country", city=city)
        return reply(req,
                     f"Приятно, {stat.name}! Угадай страну: какой это город?",
                     image=CITIES[city], btns=["Не знаю", "Хватит"])

    if text in ("хватит", "выход", "стоп"):
        return reply(req, f"Пока, {stat.name or 'друг'}! "
                          f"Твой счёт: {stat.score} из {stat.rounds}.", end=True)

    if state["stage"] == "ask_country":
        real = get_country(state["city"])
        stat.rounds += 1
        new_city = random.choice(list(CITIES))
        if real and real.lower() in text:
            stat.score += 1
            sess.commit()
            state["city"] = new_city
            return reply(req,
                         f"Верно! Это {real}. Счёт {stat.score}/{stat.rounds}. "
                         f"Следующий город?",
                         tts=f"{WIN} Верно! Это {real}. Следующий город?",
                         image=CITIES[new_city], btns=["Не знаю", "Хватит"])
        sess.commit()
        state["city"] = new_city
        hint = real or "не могу проверить"
        return reply(req,
                     f"Не угадал. Правильный ответ: {hint}. "
                     f"Счёт {stat.score}/{stat.rounds}. Попробуем ещё раз?",
                     tts=f"{LOSE} Правильный ответ: {hint}. Попробуем ещё раз?",
                     image=CITIES[new_city], btns=["Не знаю", "Хватит"])

    return reply(req, "Скажи название страны или «хватит», чтобы выйти.")


if __name__ == "__main__":
    db_session.global_init("db/diary.db")
    app.run(host="0.0.0.0", port=5001)
