from odoo import _, fields
from odoo.exceptions import ValidationError
from odoo.tools.misc import ustr


def to_remote_datetime(date, date_format):
    """Return the date in format accepted by remote"""
    if not date:
        raise ValidationError(_("Please provide date"))
    if not date_format:
        raise ValidationError(_("Please provide date format."))
    if isinstance(date, str):
        date = fields.Datetime.from_string(date)
    try:
        return date.strftime(date_format)
    except Exception as ex:
        raise ValidationError from ex(_("%s") % (ustr(ex)))


def to_iso_datetime(date):
    """Return the date in format accepted by remote"""
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        return to_remote_datetime(date, date_format)
    except Exception as ex:
        raise ValidationError from ex(_("%s") % (ustr(ex)))


def queue_job_description(self, model):
    model_parts = model.split(".")
    model_name = " ".join(part.title() for part in model_parts[1:])
    model_name = " ".join(dict.fromkeys(model_name.split()))
    return model_name
