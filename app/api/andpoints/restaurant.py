from fastapi import HTTPException, status, APIRouter, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import main
import datetime

from schemas.shemas import UpdateRestaurant

restaurant_router = APIRouter(tags=["restaurant"], prefix="/restaurant")

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Credentials": "true"
}

def save_uploaded_file(file_object, file_path):
    with open(file_path, "wb") as file_dest:
        shutil.copyfileobj(file_object.file, file_dest)

@restaurant_router.post("/add_restaurant")
def add_restaurant(restaurant_name: str = Form(...), kind: str = Form(...), description: str = Form(...),
                   restaurant_email: str = Form(...), phone_number: str = Form(...),
                   address: str = Form(...), rating: float = Form(), image_logo: UploadFile = File(...),
                   image_background: UploadFile = File(...)):

    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logo_image_name = f"logo_image_{current_date_time}.{image_logo.filename.split('.')[-1]}"
    background_image_name = f"background_image_{current_date_time}.{image_background.filename.split('.')[-1]}"

    try:
        main.cursor.execute("""INSERT INTO restaurants (restaurant_name, kind, description, restaurant_email, phone_number,
                         address, rating, background_image, logo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (restaurant_name, kind, description, restaurant_email,
                             phone_number, address, rating, background_image_name,
                             logo_image_name))

        main.conn.commit()

        logo_path = os.path.join(os.getcwd(), "static", "images", "logo", logo_image_name)
        background_path = os.path.join(os.getcwd(), "static", "images", "background", background_image_name)

        save_uploaded_file(image_logo, logo_path)
        save_uploaded_file(image_background, background_path)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant successfully added"},
                        headers=headers)

@restaurant_router.put("/update_logo_restaurants/{restaurant_id}")
def update_logo(restaurant_id, image_logo: UploadFile = File(...)):
    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logo_image_name = f"logo_image_{current_date_time}.{image_logo.filename.split('.')[-1]}"

    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id = %s""",
                            (restaurant_id,))

        target_restaurant = main.cursor.fetchone()

        if target_restaurant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        old_image_logo = target_restaurant.get('logo')

        main.cursor.execute("""UPDATE restaurants SET logo = %s WHERE restaurant_id = %s""",
                            (logo_image_name, restaurant_id))
        main.conn.commit()

        logo_path = os.path.join(os.getcwd(), "static", "images", "logo", logo_image_name)

        if old_image_logo and os.path.exists(logo_path):
            os.remove(logo_path)

        save_uploaded_file(image_logo, logo_path)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant logo updated successfully"},
                        headers=headers)

@restaurant_router.put("/update_background_restaurants/{restaurant_id}")
def update_background(restaurant_id, image_background: UploadFile = File(...)):
    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    background_image_name = f"background_image_{current_date_time}.{image_background.filename.split('.')[-1]}"

    try:
        main.cursor.execute("""SELECT * FROM restaurants WHERE restaurant_id = %s""",
                            (restaurant_id,))

        target_restaurant = main.cursor.fetchone()

        if target_restaurant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        old_image_background = target_restaurant.get('background_image')

        main.cursor.execute("""UPDATE restaurants SET background_image = %s WHERE restaurant_id = %s""",
                            (background_image_name, restaurant_id))

        main.conn.commit()

        background_path = os.path.join(os.getcwd(), "static", "images", "background", background_image_name)

        if old_image_background and os.path.exists(background_path):
            os.remove(background_path)

        save_uploaded_file(image_background, background_path)

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Restaurant background updated successfully"},
                        headers=headers)
