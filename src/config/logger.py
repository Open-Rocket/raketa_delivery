import logging

log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s \n--------------------\n%(message)s\n--------------------"
)
handler.setFormatter(formatter)
log.addHandler(handler)


__all__ = ["log"]
