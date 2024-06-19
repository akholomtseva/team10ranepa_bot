from yadisk import YaDisk
from yadisk.exceptions import YaDiskError


class YandexFunctions:
    def __init__(self, token):
        self.token = token

    async def check_token(self):
        y = YaDisk(token=self.token)

        try:
            if y.check_token():
                return True
            else:
                return False
        except YaDiskError as e:
            return False