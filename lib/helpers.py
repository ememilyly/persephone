from discord.ext import commands
import discord
import logging
from configparser import ConfigParser

import io
import json
import re
import requests

_log = logging.getLogger(__name__)


def reload_cfg(path) -> ConfigParser:
    global _config
    _config = ConfigParser()
    _config.read(path)

    return _config


def replace_mentions_with_names(ctx: commands.Context, args: str) -> str:
    text = []
    for word in args.split(" "):
        mention_regex = "^<(@|#)\\d*>$"
        # e.g. <@111222333444555666>
        if re.match(mention_regex, word):
            obj = get_object_from_mention(ctx, word)
            if isinstance(obj, discord.Member):
                if obj.nick:
                    word = obj.nick
                else:
                    word = obj.name
            else:
                word = obj.name
        text.append(word)

    return " ".join(text)


def get_object_from_mention(ctx: commands.Context, mention: str):
    mentioned_id = int(mention[2:][:-1])
    if mention[1] == "@":
        return ctx.guild.get_member(mentioned_id)
    elif mention[1] == "#":
        return ctx.guild.get_channel_or_thread(mentioned_id)
        pass


def generate_openai_chat(prompt: dict, model: str = "gpt-3.5-turbo") -> str:
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": _config["ai"]["personality_prompt"]},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {_config['ai']['openai_api_key']}",
    }
    r = requests.post(url, json=data, headers=headers)
    _log.debug(r.json())

    chat = r.json()["choices"][0]["message"]["content"]

    return chat.strip().strip('"')


def generate_rude_response_missing_arg(ctx: commands.Context) -> str:
    prompt = f"you were asked to run a command by {ctx.author.display_name} but not given all the arguments to do so"

    return generate_openai_chat(prompt)


def generate_dezgo_image(prompt: str, model: str = "epic_diffusion_1_1") -> io.BytesIO:
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
        # default given by dezgo /shrug linter fuming rn
        "negative_prompt": "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, blurry, bad anatomy, blurred, watermark, grainy, signature, cut off, draft",
        "model": model,
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": _config["ai"]["dezgo_api_key"],
        "X-RapidAPI-Host": "dezgo.p.rapidapi.com",
    }
    _log.debug(data)
    r = requests.post(url, data=data, headers=headers)

    # expect raw image, if json is error
    try:
        e = json.loads(r.text)
        raise Exception(e)
    except json.decoder.JSONDecodeError:
        return io.BytesIO(r.content)


def get_dezgo_models() -> list:
    url = "https://dezgo.p.rapidapi.com/info"
    headers = {
        "X-RapidAPI-Key": _config["ai"]["dezgo_api_key"],
        "X-RapidAPI-Host": "dezgo.p.rapidapi.com",
    }
    r = requests.get(url, headers=headers)

    models = [f"{model['id']}: {model['description']}" for model in r.json()["models"]]

    return models
