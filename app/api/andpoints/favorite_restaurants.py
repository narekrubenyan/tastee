
from fastapi import HTTPException, status, APIRouter, Query
from fastapi.responses import JSONResponse

import main

favorite_restaurants_router = APIRouter(tags=["favorite_restaurants"], prefix="/favorite_restaurants")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


@favorite_restaurants_router.post("/add_favorite_restaurants")
def add_favorite_restaurants(user_id: int, restaurant_id: int):
    try:
        main.cursor.execute("""SELECT * FROM users WHERE user_id = %s """,
                            (user_id,))

        user = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"User by {user_id} id not found"})

    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id = %s """,
                            (restaurant_id,))

        restaurant = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"Restaurants by {user_id} id not found"})

    try:
        main.cursor.execute("""INSERT INTO favorite_restaurants (user_id, restaurant_id) 
                            VALUES (%s, %s)""",
                            (user_id, restaurant_id))

        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"There was an error adding favorite restaurant"
                                    f"ERROR: {error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite restaurant successfully added"},
                        headers=headers)


@favorite_restaurants_router.delete("/delete_favorite_restaurant/{favorite_restaurant_d}")
def delete_favorite_restaurant(favorite_restaurant_id: int, user_id: int):
    try:
        main.cursor.execute("""SELECT * FROM favorite_restaurants WHERE favorite_restaurant_id =%s AND user_id =%s""",
                            (favorite_restaurant_id, user_id))

        favorite_restaurant = main.cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if favorite_restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"Favorite restaurant by {favorite_restaurant_id} id not found"})

    try:
        main.cursor.execute("""DELETE FROM favorite_restaurants WHERE favorite_restaurant_id = %s AND user_id =%s""",
                            (favorite_restaurant_id, user_id))

        main.conn.commit()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": f"An error occurred while deleting, please try again"
                                    f"ERROR: {error}"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Favorite restaurant successfully deleted"},
                        headers=headers)


@favorite_restaurants_router.get("/get_all_favorite_restaurants_by_user_id/{user_id}")
def get_all_favorite_restaurants_by_user_id(user_id: int, page: int = Query(default=1, ge=1)):
    per_page = 20

    main.cursor.execute("SELECT count(*) FROM favorite_restaurants")
    count = main.cursor.fetchall()[0]['count']

    if count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content=[], headers=headers)

    max_page = (count - 1) // per_page + 1

    if page > max_page:
        page = max_page

    offset = (page - 1) * per_page

    try:
        main.cursor.execute("""SELECT * FROM favorite_restaurants WHERE user_id =%s LIMIT %s OFFSET %s""",
                            (user_id, per_page, offset))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    try:
        favorite_restaurants = main.cursor.fetchall()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=
                            {f"An error occurred while searching for all favorite restaurants. ERROR {str(error)}"})

    if not favorite_restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": f"User with id {user_id} has no favorite restaurants"})

    content = {
        "favorite_restaurants": favorite_restaurants,
        "page": page,
        "total_pages": max_page,
        "total_restaurants": count
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=content, headers=headers)
