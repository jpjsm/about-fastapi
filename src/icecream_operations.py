"""Route definitions and REST API implementations."""

from pathlib import Path
import json
import traceback

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, Response

from icecream.models.create_icecream_params import CreateIceCreamParams
from icecream.models.error import Error
from icecream.models.icecream import IceCream
from icecream.models.patch_icecream_params import PatchIceCreamParams
from icecream.utilities.icecream_json_encoder import IcecreamJsonEncoder
from icecream.config import Pool
from icecream.utilities.icecream_db import Icecream_DB

router = APIRouter()

# create sample data.
_icecreams = []
_icecreams.append(
    IceCream(
        Id=1,
        Name="vanilla",
        Price=3.1,
        Quantity=100,
        OnDisplay='Y',
        Description="Vanilla Bean Ice Cream: Speck-tacular Flavor!",
    )
)
_icecreams.append(
    IceCream(
        Id=2,
        Name="Blue Moon",
        Price=2,
        Quantity=20,
        OnDisplay='Y',
        Description="an ice cream flavor with bright blue coloring",
    )
)
_icecreams.append(
    IceCream(
        Id=3,
        Name="Mint chocolate chip",
        Price=3.2,
        Quantity=110,
        OnDisplay='Y',
        Description="composed of mint ice cream with small chocolate chips",
    )
)
_icecreams.append(
    IceCream(
        Id=4,
        Name="Raspberry Ripple",
        Price=4.2,
        Quantity=150,
        OnDisplay='Y',
        Description="consists of raspberry syrup injected into vanilla",
    )
)
_icecreams.append(
    IceCream(
        Id=5,
        Name="Strawberry Cheesecake",
        Price=1.9,
        Quantity=140,
        OnDisplay='N',
        Description="filled with strawberry cheesecake & graham-cracker swirl",
    )
)


@router.get("/icecream", status_code=status.HTTP_200_OK)
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
        _src_file = Path(__file__).name
        print(f"[{Path(__file__).name}].[geticecreams]: {_req.query_params}")
        qry_params_list = _req.query_params._list
        qry_params_dict_ci = {}
        for _key, _value in qry_params_list:
            _key_ci = _key.lower()
            if _key_ci not in qry_params_dict_ci:
                qry_params_dict_ci[_key_ci] = []
            qry_params_dict_ci[_key_ci].append(_value)

        requested_ids = qry_params_dict_ci.get("id")
        print(f"[{Path(__file__).name}].[geticecreams]: {requested_ids=}")

        requested_names = qry_params_dict_ci.get("name")
        print(f"[{Path(__file__).name}].[geticecreams]: {requested_names=}")

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
        _json = json.loads(
            json.dumps(
                Error(
                    ErrorMessage=f"Unable to process the request. {str(_err)}",
                    ErrorKey="GENERIC_ERROR",
                ),
                cls=IcecreamJsonEncoder,
            )
        )
        return JSONResponse(
            content=_json, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/icecream", status_code=status.HTTP_201_CREATED)
async def createicecream(createparam: CreateIceCreamParams):
    """Creates a new ice cream.

    :param createparam: new ice cream paarmeters
    :return: Created ice cream
    """
    name_requested_icecream = Icecream_DB.get_icecream_by_names(pool=Pool, ids=[createparam.Name])
    if name_requested_icecream:
        if (name_requested_icecream[0].Price == createparam.Price
            and name_requested_icecream[0].Quantity == createparam.Quantity
            and name_requested_icecream[0].OnDisplay == createparam.OnDisplay
            and name_requested_icecream[0].Description == createparam.Description
        ):
            return JSONResponse(content=name_requested_icecream[0].__dict__, status_code=status.HTTP_200_OK)
        else:
            err_msg = {
                "ErrorMessage": f"Unable to process the request. Icecream with same name {createparam.Name} exist",
                "ErrorKey": "DUPLICATE_ICECREAM"
            }
            return JSONResponse(content=err_msg, status_code=status.HTTP_409_CONFLICT)
            
    try:
        newicecream = IceCream(
            Id=0,
            Name=createparam.Name,
            Price=createparam.Price,
            Quantity=createparam.Quantity,
            Description=createparam.Description,
        )
        icecream = Icecream_DB.insert_icecream(pool=Pool, icecream=newicecream)
        return JSONResponse(content=icecream.__dict__, status_code=status.HTTP_201_CREATED)
    except Exception as _err:
        traceback.print_exc()
        _json = json.loads(
            json.dumps(
                Error(
                    ErrorMessage=f"Sorry, unable to process the request. {str(_err) }",
                    ErrorKey="GENERIC_ERROR",
                ),
                cls=IcecreamJsonEncoder,
            )
        )
        return JSONResponse(
            content=_json, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/icecream/{req_id}")
async def geticecream_withid(req_id: int):
    """Retrieve the information of the icecream with the matching icecream ID..

    :param req_id: ice cream id
    :return: matching ice cream
    """
    try:
        for i in range(len(_icecreams)):
            if _icecreams[i].Id == req_id:
                return JSONResponse(content=_icecreams[i].__dict__, status_code=status.HTTP_200_OK)
        error= {
            "ErrorMessage":f"No matching icecream with id {req_id} found",
            "ErrorKey":"ICECREAM_NOT_FOUND"
        }
        return JSONResponse(content=error, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as _err:
        error= {
            "ErrorMessage":f"Sorry, unable to process the request. {str(_err)}",
            "ErrorKey":"GENERIC_ERROR"
        }
        return JSONResponse(
            content=error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/icecream/{req_id}")
async def deleteicecream_withid(req_id: int):
    """Deletes the ice cream with the matching icecream ID..

    :param req_id: ice cream id
    :return: empty json response
    """
    try:
        for i in range(len(_icecreams)):
            if _icecreams[i].Id == req_id:
                _icecreams.pop(i)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
        error= {
            "ErrorMessage":f"No matching icecream with id {req_id} found",
            "ErrorKey":"ICECREAM_NOT_FOUND"
        }
        return JSONResponse(content=error, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as _err:
        error= {
            "ErrorMessage":f"Sorry, unable to process the request. {str(_err)}",
            "ErrorKey":"GENERIC_ERROR"
        }
        return JSONResponse(
            content=error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.patch("/icecream/{req_id}")
async def updateicecream_withid(req_id: int, patchparam: PatchIceCreamParams):
    """Update some or all the information of an existing ice cream with matching id..

    :param req_id: ice cream id
    :param patchparam: new ice cream properties
    :return: updated ice cream
    """
    try:
        for i in range(len(_icecreams)):
            if _icecreams[i].Name == patchparam.Name and req_id != _icecreams[i].Id:
                _json = json.loads(
                    json.dumps(
                        Error(
                            ErrorMessage="".join(
                                [
                                    f"New name {patchparam.Name} conflicts",
                                    "with existing name in different ice cream",
                                ]
                            ),
                            ErrorKey="ICECREAM_NAME_CONFLICT",
                        ),
                        cls=IcecreamJsonEncoder,
                    )
                )
                return JSONResponse(
                    content=_json, status_code=status.HTTP_400_BAD_REQUEST
                )

        for i in range(len(_icecreams)):
            if _icecreams[i].Id == req_id:
                if patchparam.Name is not None:
                    _icecreams[i].Name = patchparam.Name
                if patchparam.Price is not None:
                    _icecreams[i].Price = patchparam.Price
                if patchparam.Quantity is not None:
                    _icecreams[i].Quantity = patchparam.Quantity
                if patchparam.Description is not None:
                    _icecreams[i].Description = patchparam.Description
                _json = json.loads(json.dumps(_icecreams[i], cls=IcecreamJsonEncoder))
                return JSONResponse(content=_json, status_code=status.HTTP_200_OK)
        _json = json.loads(
            json.dumps(
                Error(
                    ErrorMessage=f"No matching icecream with id {req_id} found",
                    ErrorKey="ICECREAM_NOT_FOUND",
                ),
                cls=IcecreamJsonEncoder,
            )
        )
        return JSONResponse(content=_json, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as _err:
        _json = json.loads(
            json.dumps(
                Error(
                    ErrorMessage=f"Sorry, unable to process the request. {str(_err)}",
                    ErrorKey="GENERIC_ERROR",
                ),
                cls=IcecreamJsonEncoder,
            )
        )
        return JSONResponse(
            content=_json, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/icecream/{req_id}")
async def replaceicecream_withid(req_id: int, newicecream: IceCream):
    """Completely updates an existing ice cream with matching id..

    :param req_id: ice cream id
    :param newicecream: new ice cream properties
    :return: updated ice cream
    """
    try:
        if req_id != newicecream.Id:
            _json = json.loads(
                json.dumps(
                    Error(
                        ErrorMessage="".join(
                            [
                                f"Path id {req_id} doesn't match the id",
                                f"in body of the update {newicecream.Id}",
                            ]
                        ),
                        ErrorKey="ICECREAM_ID_MISMATCH",
                    ),
                    cls=IcecreamJsonEncoder,
                )
            )
            return JSONResponse(content=_json, status_code=status.HTTP_400_BAD_REQUEST)

        for i in range(len(_icecreams)):
            if _icecreams[i].Name == newicecream.Name:
                _json = json.loads(
                    json.dumps(
                        Error(
                            ErrorMessage="".join(
                                [
                                    f"New name {newicecream.Name} conflicts",
                                    "with existing name in different ice cream",
                                ]
                            ),
                            ErrorKey="ICECREAM_NAME_CONFLICT",
                        ),
                        cls=IcecreamJsonEncoder,
                    )
                )
                return JSONResponse(
                    content=_json, status_code=status.HTTP_400_BAD_REQUEST
                )

        for i in range(len(_icecreams)):
            if _icecreams[i].Id == req_id:
                _icecreams[i].Name = newicecream.Name
                _icecreams[i].Price = newicecream.Price
                _icecreams[i].Quantity = newicecream.Quantity
                _icecreams[i].Description = newicecream.Description
                _json = json.loads(json.dumps(_icecreams[i], cls=IcecreamJsonEncoder))
                return JSONResponse(content=_json, status_code=status.HTTP_200_OK)
        _json = json.loads(
            json.dumps(
                Error(
                    ErrorMessage=f"No matching icecream with id {req_id} found",
                    ErrorKey="ICECREAM_NOT_FOUND",
                ),
                cls=IcecreamJsonEncoder,
            )
        )
        return JSONResponse(content=_json, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as _err:
        _json = json.loads(
            json.dumps(
                Error(
                    ErrorMessage=f"Sorry, unable to process the request. {str(_err)}",
                    ErrorKey="GENERIC_ERROR",
                ),
                cls=IcecreamJsonEncoder,
            )
        )
        return JSONResponse(
            content=_json, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
