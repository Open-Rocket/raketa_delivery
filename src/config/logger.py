import logging

log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("\n%(asctime)s - %(levelname)s - %(message)s\n\n")
handler.setFormatter(formatter)
log.addHandler(handler)


__all__ = ["log"]
