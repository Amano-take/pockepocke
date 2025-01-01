import logging


def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # ログレベルを設定
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # ログフォーマットを設定
        handlers=[logging.StreamHandler()],  # logging.FileHandler("app.log")],  # コンソール出力  # ファイル出力
    )


setup_logging()
