from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# כתובת ה-API של מאגר כלי הרכב הפעילים במאגר הממשלתי
API_URL = "https://data.gov.il/api/3/action/datastore_search"
RESOURCE_ID = "053cea08-09bc-40ec-8f7a-156f0677aff3"

@app.route('/car-info', methods=['GET', 'POST'])
def get_car_info():
    # קליטת מספר הרכב מימות השיח (תומך גם ב-GET וגם ב-POST)
    car_number = request.args.get('carNumber') or request.form.get('carNumber')
    
    if not car_number:
        return "id_list_message=t-לא התקבל מספר רכב. נא נסה שוב."

    # שליפת הנתונים ממאגר המידע הממשלתי
    params = {
        "resource_id": RESOURCE_ID,
        "filters": f'{{"mispar_rechev": "{car_number}"}}'
    }

    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

        if data.get("success") and data["result"]["records"]:
            car = data["result"]["records"][0]
            
5            # איסוף ומיצוי כלל הפרטים של הרכב
            mispar_rechev = car.get("mispar_rechev", "לא ידוע")
            tozeret = car.get("tozeret_nm", "לא ידוע")
            kinuy_mishari = car.get("kinuy_mishari", "לא ידוע")
            shnat_yitzur = car.get("shnat_yitzur", "לא ידוע")
            tzeva = car.get("tzeva_rechev", "לא ידוע")
            sug_דלק = car.get("sug_delek_nm", "לא ידוע")
            moed_aliya = car.get("moed_aliyah_lakvish", "לא ידוע")
            kvutzat_zihum = car.get("kvutzat_zihum", "לא ידוע")
            baalut = car.get("baalut", "לא ידוע")

            # בניית מחרוזת קולית מפורטת הכוללת את כלל הפרטים להשמעה בימות השיח
            text_to_read = (
                f"פרטי הרכב עבור מספר {mispar_rechev}: "
                f"יצרן: {tozeret}. "
                f"דגם: {kinuy_mishari}. "
                f"שנת ייצור: {shnat_yitzur}. "
                f"צבע: {tzeva}. "
                f"סוג דלק: {sug_דלק}. "
                f"מועד עליה לכביש: {moed_aliya}. "
                f"קבוצת זיהום: {kvutzat_zihum}. "
                f"סוג בעלות: {baalut}."
            )

            # החזרת המחרוזת בפורמט המובן לימות השיח
            return f"id_list_message=t-{text_to_read}"
        else:
            return "id_list_message=t-לא נמצאו פרטים במאגר עבור מספר רכב זה."

    except Exception as e:
        return "id_list_message=t-אירעה שגיאה בחיבור למאגר הנתונים."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)