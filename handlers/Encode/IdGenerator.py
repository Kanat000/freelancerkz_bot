import base64


def encrypt_val(order_id):
    message = str(order_id)
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)

    base64_message = base64_bytes.decode('utf-8')

    return base64_message.replace('=', '_')


