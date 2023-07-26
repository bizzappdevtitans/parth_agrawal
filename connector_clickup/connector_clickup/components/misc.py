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
    """Return dynamic queue job description"""
    model_parts = model.split(".")
    model_name = " ".join(part.title() for part in model_parts[1:])
    model_name = " ".join(dict.fromkeys(model_name.split()))
    return model_name


def update_existing_message(self, messages, external_id, comment_text):
    """Update comments and attachments from clickup to project"""
    existing_message = messages.filtered(lambda msg: msg.external_id == external_id)
    existing_message.write({"body": comment_text})


def get_attachment_urls(self, attachments):
    """Get attachments url from clickup to project"""
    attachment_urls = []
    for attachment in attachments:
        if attachment.get("type") == "attachment":
            attachment_url = attachment.get("attachment", {}).get("url")
            if attachment_url:
                attachment_urls.append(attachment_url)
    return attachment_urls


def find_author(self, commenter_email):
    """Find the user to define author"""
    return (
        self.env["res.partner"]
        .sudo()
        .search([("email", "=", commenter_email)], limit=1)
    ).id or self.env.user.id


def create_comment_with_attachments(
    self, messages, comment_id, res_id, comment_text, author_id, attachment_urls, model
):
    """Create comments and attachments from clickup to project"""
    new_message = messages.sudo().create(
        {
            "model": str(model),
            "external_id": comment_id,
            "res_id": res_id,
            "message_type": "comment",
            "author_id": author_id,
            "body": comment_text,
        }
    )
    for attachment_url in attachment_urls:
        attachment_data = {
            "name": attachment_url.split("/")[-1],
            "url": attachment_url,
        }
        new_message.attachment_ids = [(0, 0, attachment_data)]
