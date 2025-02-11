from _dependencies import logging


log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

logging.basicConfig(
    level=logging.INFO, format="--------------------\n%(message)s\n--------------------"
)


__all__ = ["log"]
