from config import Config
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime
import pymssql


# instantiate the app
app = Flask(__name__)

# configuration from config-file
app.config.from_object(Config)

# enable CORS
CORS(app)

# sanity check route
@app.route('/api/v1/zk', methods=['POST'])
def show_zk():
    # Getting info about zk from barcode(order_head_id)

    order_head_id = request.get_json()['order_head_id']

    query_order_info = 'SELECT orha.order_id, orha.local_id, orha.[date], cst.CUSTOMER_NAME ' \
        'FROM order_head_actual orha ' \
        'inner join CUSTOMER cst on cst.CUSTOMER_ID = orha.customer_id ' \
        f'where orha.order_id = {order_head_id}'
    with pymssql.connect(app.config['SERVER'], app.config['USER'], app.config['PASSWORD'], app.config['DBNAME']) as conn:
        with conn.cursor(as_dict=True) as cur:
            try:
                cur.execute(query_order_info)
                order_head = cur.fetchone()
                if order_head:
                    query_order_pos = 'select op_id, dt.device_name, dt.device_mark, opa2.qty, trar.COMMENT, '\
                        'trar.LOCATION, dest.destination_name, trar.destination_id, opa2.work_done, count(dcra.employee_id) as nazn '\
                        'from TRANSPORTATION_ACTUAL_RVR trar '\
                        'inner join ORDER_POS_ACTUAL opa2 on opa2.ORDER_POS_ID = trar.ORDER_POS_ID '\
                        'left join device_calibration_rec_actual dcra on dcra.order_pos_id = opa2.ORDER_POS_ID '\
                        'inner join device_type dt on dt.dt_id = opa2.dt_id '\
                        'inner join destination dest on dest.destination_id = trar.destination_id '\
                        'inner join(select tra.ORDER_POS_ID AS op_id, MAX(tra.TRANSPORTATION_ID) AS tra_id '\
                        'from TRANSPORTATION_ACTUAL_RVR tra '\
                        'where tra.ORDER_POS_ID in '\
                        '(select opa2.order_pos_id from ORDER_POS_ACTUAL opa2 '\
                        f'where opa2.ORDER_ID={order_head_id}) '\
                        'GROUP BY tra.ORDER_POS_ID) tra2 '\
                        'on tra2.tra_id = trar.TRANSPORTATION_ID '\
                        'group by op_id, dt.device_name, dt.device_mark, opa2.qty, trar.COMMENT, '\
                        'trar.LOCATION, dest.destination_name, trar.destination_id, opa2.work_done'

                    with conn.cursor(as_dict=True) as cur:
                        cur.execute(query_order_pos)
                        order_head['devices'] = cur.fetchall()
                else:
                    return jsonify({'status': 'error', 'error_text': 'Ничего не найдено!'})
            except pymssql.Error:
                return jsonify({'status': 'error', 'error_text': 'MSSQL exception!'})
    # return jsonify(order_positions)
    return jsonify(order_head)


@app.route('/api/v1/zkbynum', methods=['POST'])
def show_zk_by_num():

    # Getting info about zk from prefix, num and year
    prefix_id = request.get_json()['zk_prefix']
    # if was scanned num barcode cut out '%-' prefix
    zk_nomer = str(request.get_json()['zk_nomer']).replace(
        '%-', '')
    zk_year = str(request.get_json()['zk_year'])

    if (prefix_id and zk_nomer and zk_year):
        try:
            order_local_id = app.config['PREFIXES'][prefix_id] + \
                zk_nomer.strip()
        except KeyError:
            return jsonify(
                {'status': 'error', 'error_text': 'Wrong prefix!'})

        query_order_info = 'SELECT orha.order_id, orha.local_id, orha.[date], cst.CUSTOMER_NAME '\
            f'FROM order_head_actual_{zk_year} orha '\
            'inner join CUSTOMER cst on cst.CUSTOMER_ID = orha.customer_id '\
            'where orha.local_id = %s'

        with pymssql.connect(app.config['SERVER'], app.config['USER'], app.config['PASSWORD'], app.config['DBNAME']) as conn:
            with conn.cursor(as_dict=True) as cur:
                try:
                    cur.execute(query_order_info, order_local_id)
                    order_head = cur.fetchone()
                    if order_head:
                        order_head_id = order_head['order_id']
                        query_order_pos = 'select op_id, dt.device_name, dt.device_mark, opa2.qty, trar.COMMENT, '\
                            'trar.LOCATION, dest.destination_name, trar.destination_id, opa2.work_done, count(dcra.employee_id) as nazn '\
                            'from TRANSPORTATION_ACTUAL_RVR trar '\
                            'inner join ORDER_POS_ACTUAL opa2 on opa2.ORDER_POS_ID = trar.ORDER_POS_ID '\
                            'left join device_calibration_rec_actual dcra on dcra.order_pos_id = opa2.ORDER_POS_ID '\
                            'inner join device_type dt on dt.dt_id = opa2.dt_id '\
                            'inner join destination dest on dest.destination_id = trar.destination_id '\
                            'inner join(select tra.ORDER_POS_ID AS op_id, MAX(tra.TRANSPORTATION_ID) AS tra_id '\
                            'from TRANSPORTATION_ACTUAL_RVR tra '\
                            'where tra.ORDER_POS_ID in '\
                            '(select opa2.order_pos_id from ORDER_POS_ACTUAL opa2 '\
                            f'where opa2.ORDER_ID={order_head_id}) '\
                            'GROUP BY tra.ORDER_POS_ID) tra2 '\
                            'on tra2.tra_id = trar.TRANSPORTATION_ID '\
                            'group by op_id, dt.device_name, dt.device_mark, opa2.qty, trar.COMMENT, '\
                            'trar.LOCATION, dest.destination_name, trar.destination_id, opa2.work_done'

                        with conn.cursor(as_dict=True) as cur:
                            cur.execute(query_order_pos)
                            order_head['devices'] = cur.fetchall()
                    else:
                        return jsonify({'status': 'error', 'error_text': 'Ничего не найдено!'})
                except pymssql.Error as e:
                    print(str(e))
                    return jsonify({'status': 'error', 'error_text': 'MSSQL exception!'})
    else:
        return jsonify({'status': 'error', 'error_text': 'Not enough params!'})
    return jsonify(order_head)


@app.route('/api/v1/transport', methods=['POST'])
def transport_zk():

    destination_id = int(request.get_json()['destination_id'])
    if not(destination_id in range(1, 6)):
        result = {'status': 'error',
                  'error_text': 'Invalid destination! (must be in range 1-5)'}
        return jsonify(result)

    # Getting info about zk from barcode(last order_pos_id in it)
    try:
        dep_id = request.get_json()['dep_id']
        op_ids = request.get_json()['order_pos_ids']
        employee_id = request.get_json()['employee_id']

        if (employee_id and dep_id and op_ids):
            # order_pos_id = request.form['order_pos_id']
            # accept_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            employee_id = f'{employee_id}010030'  # convert to database format
            new_comment = request.get_json()['comment']
            new_location = request.get_json()['location']

            query_priem = 'INSERT INTO [TRANSPORTATION] ([ACCEPT_DATE], [EMPLOYEE_ID], ' \
                '[ORDER_POS_ID], [COMMENT], [LOCATION], [DEPARTMENT_ID], [DESTINATION_ID]) ' \
                'VALUES (GETDATE(), %s, %s, %s, %s, %s, %d)'

            query_data = []

            for op_id in op_ids:
                # query_data.append((employee_id, op_id['op_id'], op_id['comment'], op_id['location'], dep_id, destination_id))
                query_data.append(
                    (employee_id, op_id, new_comment, new_location, dep_id, destination_id))

            with pymssql.connect(app.config['SERVER'], app.config['USER'], app.config['PASSWORD'], app.config['DBNAME']) as conn:
                with conn.cursor() as cur:
                    try:
                        cur.executemany(query_priem, query_data)
                        conn.commit()
                    except pymssql.Error:
                        return jsonify({'status': 'error', 'error_text': 'MSSQL exception!'})

            result = {'status': 'ok', 'dep_id': dep_id,
                      'employee_id': employee_id, 'destination': destination_id}
        else:
            result = {'status': 'error', 'error_text': 'Some params is empty!'}
    except (ValueError, KeyError, TypeError) as error:
        print(error)
        result = {'status': 'error', 'error_text': 'Not enough params'}
    return jsonify(result)


if __name__ == '__main__':
    if app.config['SERVER'] == '-no-env-var-':
        print('ERROR! Envvar does not exists!')
    else:
        app.run()
