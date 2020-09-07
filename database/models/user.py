# firestore に保存するにあたって、いちいちディクショナリを作成して保存するより、
# クラスにまとめてモデルとして扱う
class User(object):
    def __init__(self, name, bankroll, registered_at):
        self.name = name
        self.bankroll = bankroll
        # self.password = password
        self.registered_at = registered_at

    @staticmethod
    def from_dict(source):
        # [START_EXCLUDE]
        user = User(source[u"name"],
                    source[u"bankroll"],
                    # source[u"password"],
                    source[u"registered_at"])

        # 任意で。あるならデフォルト引数を指定する
        # if u"capital" in source:
        #     city.capital = source[u"capital"]

        return user
        # [END_EXCLUDE]

    def to_dict(self):
        # [START_EXCLUDE]
        dest = {
            u"name": self.name,
            u"bankroll": self.bankroll,
            # u"password": self.password,
            u"registered_at": self.registered_at
        }

        # 任意で。デフォルト引数を指定する
        # if self.capital:
        #     dest[u"capital"] = self.capital

        return dest
        # [END_EXCLUDE]

    def __repr__(self):
        return(
            f"User(\
                name={self.name}, \
                bankroll={self.bankroll}"
                # password={self.password}"
        )