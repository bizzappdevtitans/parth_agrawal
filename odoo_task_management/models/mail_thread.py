from odoo import models, api

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # @api.model
    # def message_get_payload(self, message, message_dict, model=None, thread_id=None, **kwargs):
    #     payload = super(MailThread, self).message_get_payload(message, message_dict, model=model, thread_id=thread_id, **kwargs)
    #     if model == 'product.product':
    #         product = self.env[model].browse(thread_id)
    #         attachments = product.attachment_ids.filtered(lambda att: att.res_model == model and att.res_id == thread_id)
    #         if attachments:
    #             payload['attachments'] = [(att.name, att.datas_fname, att.datas) for att in attachments]
    #     return payload
