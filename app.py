from flask import Flask, request
import requests

app = Flask(__name__)

SEARCH_URL = "https://data.gov.il/api/3/action/package_search"
DATASTORE_URL = "https://data.gov.il/api/3/action/datastore_search"

# פונקציה שמוצאת אוטומטית את ה-Resource ID העדכני של מאגר הרכב
def get_current_resource_id():
    try:
        # מחפש את חבילת המידע של רכב במאגר הממשלתי
        response = requests.get(SEARCH_URL, params={"q": "רכב פעיל"}, timeout=5)
        data = response.json()
        
        if data.get("success"):
            for dataset in data["result"]["results"]:
                for resource in dataset.get("resources", []):
                    # מחפש את המשאב הפעיל של הנתונים
                    if "datastore" in resource.get("datastore_active", False) or "csv" in resource.get("format", "").lower():
                        return resource["id"]
    except Exception:
        pass
    
    # ברירת מחדל אם החיפוש האוטומטי נכשל
    return "053cea08-09bc-40ec-8f7a-156f0677aff3"

@app.route('/')
def home():
    return "שירות בדיקת רכב פועל באופן אוטומטי."

@app.route('/car-info', methods=['GET', 'POST'])
def get_car_info():
    car_number = request.args.get('carNumber') or request.form.get('carNumber')
    
    if not car_number:
        return "id_list_message=t-לא התקבל מספר רכב."

    # איתור דינמי של המזהה העדכני
    resource_id = get_current_resource_id()

    params = {
        "resource_id": resource_id,
        "filters": f'{{"mispar_rechev": "{car_number}"}}'
    }

    try:
        response = requests.get(DATASTORE_URL, params=params, timeout=10)
        
        # אם עדיין יש שגיאת 404, ננסה להשתמש במזהה גיבוי מוכר
        if response.status_code == 404:
            params["resource_id"] = "053cea08-09bc-40ec-8f7a-156f0677aff3"
            response = requests.get(DATASTORE_URL, params=params, timeout=10)

        if response.status_code != 200:
            return "id_list_message=t-שגיאה בחיבור למאגר הנתונים."

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
