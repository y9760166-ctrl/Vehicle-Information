from flask import Flask, request
import requests

app = Flask(__name__)

SEARCH_URL = "https://data.gov.il/api/3/action/package_search"
DATASTORE_URL = "https://data.gov.il/api/3/action/datastore_search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def get_current_resource_id():
    # ננסה קודם כל לחפש את המזהה העדכני של מאגר הרכב הפעיל
    try:
        response = requests.get(SEARCH_URL, params={"q": "רכב פעיל"}, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                for dataset in data["result"]["results"]:
                    title = dataset.get("title", "")
                    if "רכב" in title and "פעיל" in title:
                        for resource in dataset.get("resources", []):
                            if resource.get("format", "").upper() in ["CSV", "API", "JSON"] or "datastore" in resource.get("datastore_active", False):
                                return resource["id"]
    except Exception:
        pass
    
    # מזהה קבוע מעודכן למאגר הרכב הפעיל של משרד התחבורה
    return "053cea08-09bc-40ec-8f7a-156f0677aff3"

@app.route('/')
def home():
    return "שירות בדיקת רכב פועל."

@app.route('/car-info', methods=['GET', 'POST'])
def get_car_info():
    car_number = request.args.get('carNumber') or request.form.get('carNumber')
    
    if not car_number:
        return "id_list_message=t-לא התקבל מספר רכב."

    resource_id = get_current_resource_id()

    params = {
        "resource_id": resource_id,
        "filters": f'{{"mispar_rechev": "{car_number}"}}'
    }

    try:
        response = requests.get(DATASTORE_URL, params=params, headers=HEADERS, timeout=10)
        
        # אם קיבלנו 404, ננסה לבצע בקשה נוספת עם מזהה חלופי נפוץ נוסף במקום להחזיר שגיאה מיד
        if response.status_code == 404:
            alt_resource_id = "f6934e89-49d7-48f8-b398-f2b7c6c44933"
            params["resource_id"] = alt_resource_id
            response = requests.get(DATASTORE_URL, params=params, headers=HEADERS, timeout=10)

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
