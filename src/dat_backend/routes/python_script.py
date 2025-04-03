import datetime as dt
import io
import os
import pprint
from typing import Any, Final

import flask_restx as frx
from flask import (
    make_response,
    send_file,
)
import pydantic

from dat_backend import api, app
from dat_backend.constants import RESPONSE_CODES


class SelectionFilters(pydantic.BaseModel):
    bounding_box: str
    dataset_short_name: str
    dataset_version: str
    time_start: dt.datetime
    time_end: dt.datetime
    polygon: str
    filename_filter: str


def cmr_datetime_format(dt: dt.datetime) -> str:
    """CMR only supports the 'Z' ISO 8601 suffix.

    Replace the default datetime.isoformat() suffix ('+00:00') with 'Z'.
    """
    return dt.isoformat().replace("+00:00", "Z")


SCRIPT_DOC: Final[frx.model.Model] = api.model(
    "Script",
    {
        "bounding_box": frx.fields.String(
            description="the bounding box", example="-180,-90,180,90", required=False
        ),
        "dataset_short_name": frx.fields.String(
            description="the collection ID", example="MOD10A2", required=True
        ),
        "dataset_version": frx.fields.String(
            description="the collection version", example="6", required=True
        ),
        "time_start": frx.fields.String(
            description="the start datetime (UTC) filter",
            example="1999-12-18T00:00:00Z",
            required=False,
        ),
        "time_end": frx.fields.String(
            description="the end datetime (UTC) filter",
            example="2019-03-07T22:09:38Z",
            required=False,
        ),
        "polygon": frx.fields.String(
            description="the polygon filter",
            example="-109,37,-102,37,-102,41,-109,41,-109,37",
            required=False,
        ),
        "filename_filter": frx.fields.String(
            description="the filename filter", example="*2019*", required=False
        ),
    },
)


@api.route("/api/downloader-script/")
class DataDownloaderScript(frx.Resource):  # type: ignore[misc]

    @api.response(*RESPONSE_CODES[200])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    @api.expect(SCRIPT_DOC)  # type: ignore[misc]
    def post(self) -> Any:
        current_date = dt.date.today().isoformat()

        url_list = api.payload.get("url_list")
        if url_list:
            script_parameters = {
                "{short_name}": "",
                "{version}": "",
                "{time_start}": "",
                "{time_end}": "",
                "{bounding_box}": "",
                "{polygon}": "",
                "{filename_filter}": "",
                '"{url_list}"': pprint.pformat(url_list),
            }
            app.logger.info(
                f"Script request received successfully: {len(url_list)} URLs"
            )
            filename = f"nsidc-download_{current_date}.py"

        else:
            try:
                selection_filters = SelectionFilters(**api.payload)
                app.logger.info(
                    f"Script request received successfully: {selection_filters}"
                )
            # This validation error should come from pydantic.
            except pydantic.ValidationError as e:
                app.logger.exception(e)
                frx.abort(400, f"Validation failed. {e}")
            except RuntimeError as e:
                app.logger.exception(e)
                frx.abort(400, str(e))

            script_parameters = {
                "{short_name}": selection_filters.dataset_short_name,
                "{version}": selection_filters.dataset_version,
                "{time_start}": cmr_datetime_format(selection_filters.time_start),
                "{time_end}": cmr_datetime_format(selection_filters.time_end),
                "{bounding_box}": selection_filters.bounding_box,
                "{polygon}": selection_filters.polygon,
                "{filename_filter}": selection_filters.filename_filter,
                '"{url_list}"': "[]",
            }

            version = selection_filters.dataset_version.zfill(3)
            filename = f"nsidc-download_{selection_filters.dataset_short_name}.{version}_{current_date}.py"

        app.logger.info("Building script...")

        fp = os.path.join(
            os.path.dirname(__file__), "..", "templates", "python_script.py"
        )
        with open(fp, "r") as file:
            script = file.read()

        script_parameters["{copyright_year}"] = str(dt.date.today().year)

        # Do not use .format, otherwise we can't have {} within the python_script file.
        for param, value in script_parameters.items():
            script = script.replace(param, value)

        stream = io.BytesIO()
        stream.write(script.encode("utf-8"))
        stream.seek(0)

        response = make_response(
            send_file(
                stream,
                mimetype="application/x-python",
                as_attachment=True,
                download_name=filename,
            )
        )

        return response
