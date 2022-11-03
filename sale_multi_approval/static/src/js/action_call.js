odoo.define("sale_multi_approval.sale_action_button", function (require) {
    "use strict";


    var FormController = require("web.FormController");
    var session = require('web.session');

    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('.oe_download_button').click(this.proxy('action_sign')) ;
            }
            this.sale_order_id = this.model.get(this.handle);
            this.sale_order_data = this.model.get(this.handle).data;

            if (this.sale_order_data.check_approve_ability == false || this.sale_order_data.document_fully_approved == true || this.sale_order_data.is_approved == true) {
                this.$buttons.find('.oe_download_button').addClass("o_invisible_modifier")
            }
        },

        action_sign: async function () {
            var self = this;
            await self._rpc({
                model: 'sale.order',
                method: 'access_token_sale_order',
                args: [[]],
                kwargs: {'order_id': self.sale_order_id.res_id}
            }).then(async (token_data) => {
                var dom_data = await $.ajax({
                    url: `${session['web.base.url']}${token_data.url}`,
                    type: "GET",
                    success: function(res) {
                        return res
                    }
                })
                if (this.sale_order_data.signed_xml_document == false) {
                    const [opt, element, title] = self.serialize_data(dom_data)
                    html2pdf().set(opt).from(element).outputPdf().then(async(pdf) => {
                        return await self.create_pdf_attachment(title, this.sale_order_id, pdf)
                    })
                }
                var def_data = await self.tigger_sign_action()
                window.location.href = def_data.url
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
                    'res_id': sale_order_id.res_id,
                    'res_name': sale_order_id.data.name,
                    'res_model': 'sale.order',
                    'datas': btoa(pdf),
                    'type': 'binary',
                    'mimetype': 'application/pdf'
                }
           })
        },

        tigger_sign_action: async function () {
            return await this._rpc({
                model: 'sale.order',
                method: 'sale_approve',
                args: [[]],
                kwargs: {'order_id': this.sale_order_id.res_id}
            })
        }
    };
    FormController.include(includeDict);

})
