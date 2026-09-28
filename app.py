from flask import Flask, request
import requests

app = Flask(__name__)

# כתובת ה-API של מאגר הנתונים הממשלתי (CKAN API)
API_URL = "https://data.gov.il/api/3/action/datastore_search"
# מזהה טבלת הרכב הפעיל במאגר הממשלתי
RESOURCE_ID = "053cea08-09bc-40ec-8f7a-156f0677aff3"

# כותרות לדפדפן כדי למנוע חסימות אוטומטיות
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

@app.route('/')
def home():
    return "שירות בדיקת רכב פעיל פועל בהצלחה."

@app.route('/car-info', methods=['GET', 'POST'])
def get_car_info():
    # קליטת מספר הרכב ממערכת ימות המשיח (תומך גם ב-GET וגם ב-POST)
    car_number = request.args.get('carNumber') or request.form.get('carNumber')
    
    if not car_number:
        return "id_list_message=t-לא התקבל מספר רכב. נאנסה שנית."

    # הגדרת הפרמטרים לשאילתה מול המאגר הממשלתי
    params = {
        "resource_id": RESOURCE_ID,
        "filters": f'{{"mispar_rechev": "{car_number}"}}'
    }

    try:
        # שליחת הבקשה לשרת הממשלתי
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return f"id_list_message=t-שגיאה בחיבור למאגר, קוד שגיאה {response.status_code}"

        data = response.json()

        # בדיקה האם נמצאו רשומות תואמות למספר הרכב
        if data.get("success") and data["result"]["records"]:
            car = data["result"]["records"][0]
            
            mispar_rechev = car.get("mispar_rechev", car_number)
            tozeret = car.get("tozeret_nm", "לא ידוע")
            kinuy_mishari = car.get("kinuy_mishari", "")
            shnat_yitzur = car.get("shnat_yitzur", "לא ידוע")
            tzeva = car.get("tzeva_rechev", "לא ידוע")

            # בניית המחרוזת להקראה קולית במערכת הטלפונית
            text_to_read = (
                f"רכב מספר {mispar_rechev}. "
                f"יצרן {tozeret} {kinuy_mishari}. "
                f"שנת ייצור {shnat_yitzur}. "
                f"צבע {tzeva}."
            )

            return f"id_list_message=t-{text_to_read}"
        else:
            return "id_list_message=t-לא נמצאו פרטים עבור מספר רכב זה במאגר."

    except requests.exceptions.Timeout:
        return "id_list_message=t-הזמן הקצוב לתשובה מהמאגר פג. נאנסה שנית."
    except Exception as e:
        return "id_list_message=t-אירעה שגיאה פנימית בעיבוד הנתונים."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
