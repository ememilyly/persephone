from discord.ext import commands
import logging
import persephone

import io
import json
import random
import re
import requests
from typing import Union

_log = logging.getLogger(__name__)


async def generate_openai_chat(prompt: Union[str, list], model: str = "gpt-4") -> str:
    if type(prompt) == str:
        prompt = [{"role": "user", "content": prompt}]
    url = "https://api.openai.com/v1/chat/completions"
    if random.random() <= 0.025:
        prompt = "pretend you were asked something but you're just annoyed and busy and dont want to deal with them right now"
    _log.debug(prompt)
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": persephone.Secrets.get("PERSONALITY")},
        ]
        + prompt,
    }
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {persephone.Secrets.get('OPENAI_API_KEY')}",
    }
    r = requests.post(url, json=data, headers=headers, timeout=30)
    _log.debug(r.json())

    chat = r.json()["choices"][0]["message"]["content"]

    return chat.strip()


async def generate_rude_response_missing_arg(ctx: commands.Context) -> str:
    prompt = f"you were asked to run a command by {ctx.author.display_name} but not given all the arguments to do so"

    return await generate_openai_chat(prompt)


async def generate_dezgo_image(prompt: str, model: str = "epic_diffusion_1_1") -> io.BytesIO:
    model_regex = "^\\[[a-zA-Z0-9_]+\\].*"
    # if prompt starts [model] use that model
    if re.match(model_regex, prompt):
        model = prompt.split(" ")[0].strip("[").strip("]")
        prompt = prompt.split(" ")[1:]
    url = "https://dezgo.p.rapidapi.com/text2image"
    data = {
        "prompt": prompt,
        "guidance": 7,
        "steps": 30,
        "sampler": "euler_a",
        "upscale": 1,
        # default given by dezgo
        "negative_prompt": "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, blurry, bad anatomy, blurred, watermark, grainy, signature, cut off, draft",
        "model": model,
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": persephone.Secrets.get("DEZGO_API_KEY"),
        "X-RapidAPI-Host": "dezgo.p.rapidapi.com",
    }
    _log.debug(data)
    r = requests.post(url, data=data, headers=headers, timeout=20)

    if r.status_code == 200:
        return io.BytesIO(r.content)
    else:
        try:
            # json error if 4xx
            e = json.loads(r.text)
            raise Exception(e)
        except json.decoder.JSONDecodeError:
            # html error if 5xx
            e = r.text
            raise Exception(e)


async def get_dezgo_models() -> list:
    url = "https://dezgo.p.rapidapi.com/info"
    headers = {
        "X-RapidAPI-Key": persephone.Secrets.get("DEZGO_API_KEY"),
        "X-RapidAPI-Host": "dezgo.p.rapidapi.com",
    }
    r = requests.get(url, headers=headers)

    models = [f"[{model['id']}] {model['description']}" for model in r.json()["models"]]

    return models


async def query_urban_dictionary(endpoint: str = "random") -> list:
    if endpoint != "random":
        endpoint = "define?term=" + endpoint
    url = "https://api.urbandictionary.com/v0/" + endpoint
    r = requests.get(url)

    return r.json()["list"]
