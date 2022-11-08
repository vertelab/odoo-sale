odoo.define("sale_multi_approval.proceed_with_signature", function (require) {
    "use strict";

    var publicWidget = require('web.public.widget')
    var session = require('web.session');

    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    publicWidget.registry.sign = publicWidget.Widget.extend({
        selector: '#sign',
        read_events: {
            'click #trigger_sign': 'action_sign',
        },

        action_sign: async function () {
            var order_id = $('#sale_id').val()
            var self = this

            await self._rpc({
                model: 'sale.order',
                method: 'access_token_sale_order',
                args: [[]],
                kwargs: {'order_id': order_id}
            }).then(async (token_data) => {
                var dom_data = await $.ajax({
                    url: `${token_data.url}`,
                    type: "GET",
                    success: function(res) {
                        return res
                    }
                })
                const [opt, element, title] = self.serialize_data(dom_data)
                html2pdf().set(opt).from(element).outputPdf().then(async(pdf) => {
                    await self.create_pdf_attachment(title, order_id, pdf)
                })

            })
        },

        serialize_data: function (dom_data) {
            var parser = new DOMParser();
            var document = parser.parseFromString(dom_data, "text/html");

            const title_element = document.querySelector('.my-0')

            let header_information = document.querySelectorAll(
                "#portal_sale_content > div > .card-body > #informations > div.row > div > span")


            if (header_information.length > 0) {
                Array.from(header_information).forEach( function (el) {
                    const section_div = el.querySelectorAll("section > div.container")
                    Array.from(section_div).forEach( function (section_div_el) {
                        section_div_el.classList.remove('container')
                    })
                });
            }

            let content_elements = document.querySelectorAll("#portal_sale_content > div > .card-body > div[data-oe-model='sale.order'], div[data-oe-model='sale.order.line'], div[data-oe-model='sale.order.option']")

            if (content_elements.length === 0) {
                // when there is no user logged in
                content_elements = document.querySelectorAll("#portal_sale_content > div > .card-body > .oe_no_empty")
            }

            Array.from(content_elements).forEach( function (el) {
                const section_div = el.querySelectorAll("section > div.container")
                Array.from(section_div).forEach( function (section_div_el) {
                    section_div_el.classList.remove('container')
                })
            });

            const element = document.querySelector('#portal_sale_content')

            let title = ""
            let formatted_title = title_element.textContent.trim().split('\n')
            let i = 0

            for (i in formatted_title) {
                if (i > 0) {
                    title += " "
                }
                title += formatted_title[i].trim()
            }

            const opt = {
                margin: [5, 5, 10, 5], //top, left, bottom, right
                filename: title,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, logging: true, dpi: 192, letterRendering: true},
                jsPDF: { unit: 'mm', format: ['210', '297'], orientation: 'portrait' },
            };

            return [opt, element, title];
        },

        create_pdf_attachment: async function (title, sale_order_id, pdf) {
            var self = this;
            var attachment_id = await self._rpc({
                model: 'ir.attachment',
                method: 'create_attachment',
                args: [[]],
                kwargs: {
                    'name': title,
                    'res_id': sale_order_id,
                    'res_model': 'sale.order',
                    'datas': btoa(pdf),
                    'type': 'binary',
                    'mimetype': 'application/pdf'
                }
           })
           var def_data = await self.tigger_sign_action(sale_order_id)
           window.location.href = def_data.url
        },

        tigger_sign_action: async function (sale_order_id) {
            return await this._rpc({
                model: 'sale.order',
                method: 'sale_approve',
                args: [[]],
                kwargs: {'order_id': sale_order_id}
            })
        },

    });

});