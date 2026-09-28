from flask import Flask, request
import requests

app = Flask(__name__)

API_URL = "https://data.gov.il/api/3/action/datastore_search"

# רשימת מזהים אפשריים (המזהה המרכזי וכמה מזהים חלופיים נפוצים למאגר רכב פעיל)
POSSIBLE_RESOURCE_IDS = [
    "053cea08-09bc-40ec-8f7a-156f0677aff3",
    "f6934e89-49d7-48f8-b398-f2b7c6c44933", # מזהה חלופי נפוץ לרכב פעיל
    "03788734-ec20-413c-8dd6-9ebf7435f114"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@app.route('/')
def home():
    return "שירות בדיקת רכב פועל."

@app.route('/car-info', methods=['GET', 'POST'])
def get_car_info():
    car_number = request.args.get('carNumber') or request.form.get('carNumber')
    
    if not car_number:
        return "id_list_message=t-לא התקבל מספר רכב."

    success_data = None

    # ננסה לעבור על מזהים שונים עד שאחד מהם יעבוד ולא יחזיר 404
    for res_id in POSSIBLE_RESOURCE_IDS:
        params = {
            "resource_id": res_id,
            "filters": f'{{"mispar_rechev": "{car_number}"}}'
        }
        try:
            response = requests.get(API_URL, params=params, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    success_data = data
                    break
        except Exception:
            continue

    # אם נמצאה טבלה תקינה והשאילתה הצליחה
    if success_data and success_data["result"]["records"]:
        car = success_data["result"]["records"][0]
        
        mispar_rechev = car.get("mispar_rechev", car_number)
        tozeret = car.get("tozeret_nm", "לא ידוע")
        kinuy_mishari = car.get("kinuy_mishari", "")
        shnat_yitzur = car.get("shnat_yitzur", "לא ידוע")
        tzeva = car.get("tzeva_rechev", "לא ידוע")

        text_to_read = (
            f"רכב מספר {mispar_rechev}. "
            f"יצרן {tozeret} {kinuy_mishari}. "
            f"שנת ייצור {shnat_yitzur}. "
            f"צבע {tzeva}."
        )

        return f"id_list_message=t-{text_to_read}"
    
    elif success_data:
        return "id_list_message=t-לא נמצאו פרטים עבור מספר רכב זה במאגר."
    else:
        return "id_list_message=t-מאגר הנתונים הממשלתי אינו זמין כרגע."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
