from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_line = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Order Lines',
        states={'cancel': [('readonly', True)], 'done': [('readonly', False)]}, copy=True, auto_join=True)

    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)

        #  assign the signed document to the email template
        #	NOTE: This appears to be a poor solution, that causes follow on permission problems,
       	#		where a user needs persmission to WRITE in email.templates. This is non-desirable, 
       	#		and aught not be required. This requires further testing, so this is left in here,
	#		in case future problemes appears related to this.
        #if self.signed_xml_document:
        #    template.attachment_ids = [(6, 0, [self.signed_xml_document.id])]
        #else:
        #    template.attachment_ids = False

        #  assign the signed document to the email-wizard
        signed_doc = []
        if self.signed_xml_document:
            signed_doc.append(self.signed_xml_document.id)

        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
            #  continiuation of assign the signed document to the email-wizard
            'default_attachment_ids': signed_doc,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
