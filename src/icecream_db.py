from pathlib import Path
from dbaccess import DB_Access
from typing import Any
from icecream import IceCream
from psycopg_pool import ConnectionPool, AsyncConnectionPool

def Row2Icecreams(column_map, rows):
    _icecreams = []
    for row in rows:
        _icecream = IceCream(
            Id=int(row[column_map["ID"]]),
            Name=row[column_map["Name"]],
            Price=float(row[column_map["Price"]][1:] if row[column_map["Price"]][0] == "$" else row[column_map["Price"]]),
            Quantity=int(row[column_map["Quantity"]]),
            OnDisplay=bool(row[column_map["OnDisplay"]]),
            Description=row[column_map["Description"]] if row[column_map["Description"]] else '(no description yet)'
        )
        _icecreams.append(_icecream)

    return _icecreams

class Icecream_DB():
    def get_icecream_by_names(pool:ConnectionPool, names: list[str]) -> list[IceCream]:
        sql_select = """
                    SELECT "ID", "Name", "Price", "Quantity", "OnDisplay", "Description" 
                    FROM public."Icecream"
                    WHERE "Name" = ANY(%s)
                    """
        column_map, rows = Icecream_DB._query(pool=pool, sql_select=sql_select, params=[names])
        return Row2Icecreams(column_map, rows)

    def get_icecream_by_ids(pool:ConnectionPool, ids: list[str]) -> list[IceCream]:
        sql_select = """
                    SELECT "ID", "Name", "Price", "Quantity", "OnDisplay", "Description" 
                    FROM public."Icecream"
                    WHERE "ID" = ANY(%s)
                    """
        column_map, rows = Icecream_DB._query(pool=pool, sql_select=sql_select, params=[ids])
        return Row2Icecreams(column_map, rows)

    def get_all_icecream(pool:ConnectionPool) -> list[IceCream]:
        sql_select = """
                    SELECT "ID", "Name", "Price", "Quantity", "OnDisplay", "Description" 
                    FROM public."Icecream"
                    """
        column_map, rows = Icecream_DB._query(pool=pool, sql_select=sql_select)
        return Row2Icecreams(column_map, rows)

    def _query(pool:ConnectionPool, sql_select: str, params:Any = None) -> Any:
        with pool.connection() as cnx:
            with cnx.cursor() as query_cur:
                
                query_cur.execute(sql_select, params) if params else query_cur.execute(sql_select)
                rows = query_cur.fetchall()

                column_map = dict([(x.name, i) for i, x in enumerate(query_cur.description)])

                return (column_map, rows)
            
    def insert_icecream(pool:ConnectionPool, icecream:IceCream) -> IceCream:
        with pool.connection() as cnx:
            with cnx.cursor() as lock_cur:
                lock_cur.execute("""
                                LOCK TABLE public."Icecream" IN EXCLUSIVE MODE
                                """)
            with cnx.cursor() as query_cur:
                query_cur.execute("""
                                  SELECT MAX("ID") AS LAST_ID
                                  FROM public."Icecream"
                                  """)
                LAST_ID = int(query_cur.fetchone()[0])
            with cnx.cursor() as insert_cur:
                icecream.Id = LAST_ID + 1
                insert_cur.execute("""
                                   INSERT INTO public."Icecream" ("ID", "Name", "Price", "Quantity", "OnDisplay", "Description")
                                   VALUES (%s, %s, %s, %s, %s, %s)
                                   """, (icecream.Id, 
                                         icecream.Name, 
                                         icecream.Price, 
                                         icecream.Quantity, 
                                         icecream.OnDisplay, 
                                         icecream.Description))
        return icecream
        




class AsyncIcecream_DB():
    async def async_get_icecream_by_names(pool:AsyncConnectionPool, names: list[str]) -> list[IceCream]:
        _icecreams = []
        sql_select = """
                    SELECT "ID", "Name", "Price", "Quantity", "OnDisplay", "Description" 
                    FROM public."Icecream"
                    WHERE "Name" = ANY(%s)
                    """
        column_map, rows = await AsyncIcecream_DB._async_query(pool=pool, sql_select=sql_select, params=[names])
        for row in rows:
            _icecream = IceCream(
                Id=int(row[column_map["ID"]]),
                Name=row[column_map["Name"]],
                Price=float(row[column_map["Price"]]),
                Quantity=int(row[column_map["Quantity"]]),
                OnDisplay=row[column_map["OnDisplay"]],
                Description=row[column_map["OnDisplay"]]
            )
            _icecreams.append(_icecream)

        return _icecreams

    async def async_get_icecream_by_ids(pool:AsyncConnectionPool, ids: list[str]) -> list[IceCream]:
        _icecreams = []
        sql_select = """
                    SELECT "ID", "Name", "Price", "Quantity", "OnDisplay", "Description" 
                    FROM public."Icecream"
                    WHERE "Name" = ANY(%s)
                    """
        column_map, rows = await AsyncIcecream_DB._async_query(pool=pool, sql_select=sql_select, params=[ids])
        for row in rows:
            _icecream = IceCream(
                Id=int(row[column_map["ID"]]),
                Name=row[column_map["Name"]],
                Price=float(row[column_map["Price"]]),
                Quantity=int(row[column_map["Quantity"]]),
                OnDisplay=row[column_map["OnDisplay"]],
                Description=row[column_map["OnDisplay"]]
            )
            _icecreams.append(_icecream)

        return _icecreams

    async def async_get_all_icecreams(pool:AsyncConnectionPool) -> list[IceCream]:
        _icecreams = []
        sql_select = """
                    SELECT "ID", "Name", "Price", "Quantity", "OnDisplay", "Description" 
                    FROM public."Icecream"
                    """
        column_map, rows = await AsyncIcecream_DB._async_query(pool=pool, sql_select=sql_select)
        for row in rows:
            _icecream = IceCream(
                Id=int(row[column_map["ID"]]),
                Name=row[column_map["Name"]],
                Price=float(row[column_map["Price"]]),
                Quantity=int(row[column_map["Quantity"]]),
                OnDisplay=row[column_map["OnDisplay"]],
                Description=row[column_map["OnDisplay"]]
            )
            _icecreams.append(_icecream)

        return _icecreams

    async def _async_query(pool:AsyncConnectionPool, sql_select: str, params:Any = None) -> Any:
        print("[icecream_db.py].[AsyncIcecream_DB].[_async_query] - begin")
        print(f"[icecream_db.py].[AsyncIcecream_DB].[_async_query] - validating state of connection pool: {pool.max_waiting}")
        await pool.open()
        
        print("[icecream_db.py].[AsyncIcecream_DB].[_async_query] - pool opened")

        async with pool.connection() as cnx:
            print(f"[icecream_db.py].[AsyncIcecream_DB].[_async_query] - connection server version: {cnx.info.server_version}")

            async with cnx.cursor() as query_cur:
                print(f"[icecream_db.py].[AsyncIcecream_DB].[_async_query] - cursor closed: {query_cur.closed}")
                
                await query_cur.execute(sql_select, params) if params else await query_cur.execute(sql_select)
                rows = await query_cur.fetchall()
                print(f"[icecream_db.py].[AsyncIcecream_DB].[_async_query] - rows retrieved: {len(rows)}")

                column_map = dict([(x.name, i) for i, x in enumerate(query_cur.description)])

                return (column_map, rows)
