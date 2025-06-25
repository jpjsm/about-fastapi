"""Create Application."""
from pathlib import Path

from config import Pool
from icecream_db import Icecream_DB

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def home():
    """Heartbeat response.

    :return: 'Welcome to Icecream' hearbeat string
    """
    _r = {"message": "Welcome to your icecream cart! We offer thousands of flavors."}
    return JSONResponse(content=_r)


@app.get("/health")
async def healthcheck():
    """System healthcheck

    :return: 'Welcome to Icecream' hearbeat string
    """
    _health = {"health": "OK"}
    return JSONResponse(content=_health)


@app.get("/icecream", status_code=status.HTTP_200_OK)
async def geticecreams(_req: Request):
    """Retrieves all IceCreams when no query parameters are used.

    If only `id` is provided, the result set contains all ice creams
    that have id matches in the system; if there's no match to one or
    more id, those values are ignored. If there is no match to any id,
    the result is an empty array.

    If `name` is provided, the behavior is similar to `id` but using nameinstead.
    If `name` and `id` query parameters are provided the result is
    the union of both searches.

    :return: list of matching ice creams
    """
    try:
        qry_params_list = _req.query_params._list
        qry_params_dict_ci = {}
        for _key, _value in qry_params_list:
            _key_ci = _key.lower()
            if _key_ci not in qry_params_dict_ci:
                qry_params_dict_ci[_key_ci] = []
            qry_params_dict_ci[_key_ci].append(_value)

        requested_ids = qry_params_dict_ci.get("id")

        requested_names = qry_params_dict_ci.get("name")

        if qry_params_dict_ci:
            results = set()
            if requested_ids is not None:
                _results = Icecream_DB.get_icecream_by_ids(pool=Pool, ids=requested_ids)
                results.update(_results)

            if requested_names is not None:
                _results = Icecream_DB.get_icecream_by_names(pool=Pool, names=requested_names)
                results.update(_results)

            return JSONResponse(content=[x.__dict__ for x in results])

        _icecream_rows = Icecream_DB.get_all_icecream(pool=Pool)
        return JSONResponse(content=[x.__dict__ for x in _icecream_rows])
    except Exception as _err:
        return JSONResponse(
            content=_err.__dict__, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

