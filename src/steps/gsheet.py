import json, gspread

from loguru import logger
from steps.step import Step


class Gsheets(Step):
    name = "gsheets"

    def __init__(self, config: dict) -> None:
        # without this STEP.__init__ is not called
        super().__init__(config)
        self.gsheets_client = gspread.service_account(filename=self.service_account)
        assert type(self.header) == int, f"header ({self.header}) value must be an integer not {type(self.header)}"

    @staticmethod
    def configs() -> dict:
        return {
            "sheet": {"default": None, "help": "name of the sheet to archive"},
            "header": {"default": 1, "help": "index of the header row (starts at 1)"},
            "service_account": {"default": "secrets/service_account.json", "help": "service account JSON file path"},
            "columns": {
                "default": {
                    'url': 'link',
                    'status': 'archive status',
                    'folder': 'destination folder',
                    'archive': 'archive location',
                    'date': 'archive date',
                    'thumbnail': 'thumbnail',
                    'thumbnail_index': 'thumbnail index',
                    'timestamp': 'upload timestamp',
                    'title': 'upload title',
                    'duration': 'duration',
                    'screenshot': 'screenshot',
                    'hash': 'hash',
                    'wacz': 'wacz',
                    'replaywebpage': 'replaywebpage',
                },
                "help": "names of columns in the google sheet (stringified JSON object)",
                "cli_set": lambda cli_val, cur_val: dict(cur_val, **json.loads(cli_val))
            },
        }