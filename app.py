from flask import Flask, request, jsonify, render_template
from db_connector_rasp import get_db_connection
# from pyngrok import ngrok
from pub_sub_mqtt import test_mqtt_subscribe, test_mqtt_publish, get_last_mqtt_state


app = Flask(__name__)

# # Khởi động subscriber khi Flask chạy
# test_mqtt_subscribe()


# ---------- Flask API Endpoints ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/control', methods=['POST'])
def set_command():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        command = data.get('command')
        if command is None:
            return jsonify({'error': 'Missing command parameter'}), 400

        cursor = conn.cursor()
        cursor.execute("UPDATE lamps SET state = %s WHERE id = 1", (command,))
        conn.commit()

        return jsonify({'status': f'Command set to {command}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/api/control', methods=['GET'])
def get_command():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM lamps WHERE id = 1")
        row = cursor.fetchone()
        command = row[0] if row else 'unknown'

        return jsonify({'command': command})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

                
# ---------- MQTT API ----------

@app.route('/api/mqtt', methods=['POST'])
def mqtt_publish_api():
    try:
        data = request.get_json()
        command = int(data.get('command'))
        if command not in (0, 1):
            return jsonify({'error': 'Invalid command'}), 400

        test_mqtt_publish(int(command))
        return jsonify({'status': f'MQTT command {command} sent'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mqtt', methods=['GET'])
def mqtt_get_state():
    value = get_last_mqtt_state()
    print(f"[DEBUG] Current MQTT state: {value}")
    return jsonify({'mqtt_command': value})

@app.route('/api/delay', methods=['POST'])
def set_delay_time():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        s = data.get('s')
        if s is None:
            return jsonify({'error': 'Missing delay time parameter'}), 400

        cursor = conn.cursor()
        cursor.execute("UPDATE delay_time SET dt_value = %s", (s,))
        conn.commit()

        return jsonify({'status': f'Delay time updated successfully {s}s'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/api/delay', methods=['GET'])
def get_delay_time():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT dt_value FROM delay_time")
        row = cursor.fetchone()
        dt_value = row[0] if row else 'na'

        return jsonify({'dt_value': dt_value})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/api/src', methods=['POST'])
def set_source_value():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        s = data.get('s')
        if s is None:
            return jsonify({'error': 'Missing source value parameter'}), 400

        cursor = conn.cursor()
        cursor.execute("UPDATE source_control SET src_value = %s", (s,))
        conn.commit()

        return jsonify({'status': f'Source value updated successfully {s}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/api/src', methods=['GET'])
def get_source_value():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT src_value FROM source_control")
        row = cursor.fetchone()
        src_value = row[0] if row else 'na'

        return jsonify({'src_value': src_value})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # LOCAL
    # # public_url = ngrok.connect(8080)
    # # print(f" * Public URL: {public_url}")
    app.run(host='0.0.0.0', port=8080, debug=True)

    # # RAILWAY
    # import os
    # port = int(os.environ.get('PORT', 8080))
    # app.run(host='0.0.0.0', port=port)
