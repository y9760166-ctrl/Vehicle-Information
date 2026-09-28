from flask import Flask, request
import requests

app = Flask(__name__)

API_URL = "https://data.gov.il/api/3/action/datastore_search"
RESOURCE_ID = "053cea08-09bc-40ec-8f7a-156f0677aff3"

# כותרת שגורמת לשרת הממשלתי לחשוב שמדובר בדפדפן רגיל ולא בבוט
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.route('/')
def home():
    return "שירות בדיקת רכב פועל."

@app.route('/car-info', methods=['GET', 'POST'])
def get_car_info():
    car_number = request.args.get('carNumber') or request.form.get('carNumber')
    
    if not car_number:
        return "id_list_message=t-לא התקבל מספר רכב."

    params = {
        "resource_id": RESOURCE_ID,
        "filters": f'{{"mispar_rechev": "{car_number}"}}'
    }

    try:
        # שליחת הבקשה עם הכותרת המדומה של הדפדפן
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return f"id_list_message=t-שגיאה בחיבור למאגר, קוד {response.status_code}"

        data = response.json()

        if data.get("success") and data["result"]["records"]:
            car = data["result"]["records"][0]
            
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
        else:
            return "id_list_message=t-לא נמצאו פרטים עבור מספר רכב זה במאגר."

    except Exception as e:
        return "id_list_message=t-אירעה שגיאה בעיבוד הנתונים."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
