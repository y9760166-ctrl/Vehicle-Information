from flask import Flask, request
import requests

app = Flask(__name__)

API_URL = "https://data.gov.il/api/3/action/datastore_search"
RESOURCE_ID = "053cea08-09bc-40ec-8f7a-156f0677aff3"

@app.route('/car-info', methods=['GET', 'POST'])
def get_car_info():
    car_number = request.args.get('carNumber') or request.form.get('carNumber')
    
    if not car_number:
        return "id_list_message=t-לא התקבל מספר רכב. נא נסה שוב."

    params = {
        "resource_id": RESOURCE_ID,
        "filters": f'{{"mispar_rechev": "{car_number}"}}'
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        data = response.json()

        if data.get("success") and data["result"]["records"]:
            car = data["result"]["records"][0]
            
            # שליפה בטוחה של הנתונים כדי למנוע קריסה אם שדה ריק
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
            return "id_list_message=t-לא נמצאו פרטים במאגר עבור מספר רכב זה."

    except Exception as e:
        return f"id_list_message=t-שגיאה בשרת: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
