class Render:
    @staticmethod
    def common_response(err_code, message, data=None):
        return {'err_code': err_code, 'message': message, 'data': data}
