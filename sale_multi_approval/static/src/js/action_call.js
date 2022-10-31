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
                this.$buttons.find('.oe_download_button').click(this.proxy('action_def')) ;
            }
            var res_id = this.model.get(this.handle).res_id;
        },

        action_def: function () {
            var self = this;

            var res_id = this.model.get(this.handle).res_id;

            $.ajax({
                url: `${session['web.base.url']}/my/orders/${res_id}`,
                type: "GET",
                success: function(res) {
                    var parser = new DOMParser();
                    var document = parser.parseFromString(res, "text/html");

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

                    let elems = document.querySelectorAll("#portal_sale_content > div > .card-body > div[data-oe-model='sale.order'], div[data-oe-model='sale.order.line'], div[data-oe-model='sale.order.option']")

                    if (elems.length === 0) {
                        // when there is no user logged in
                        elems = document.querySelectorAll("#portal_sale_content > div > .card-body > .oe_no_empty")
                    }

                    Array.from(elems).forEach( function (el) {
                        const section_div = el.querySelectorAll("section > div.container")
                        console.log("section_div", section_div)
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

                    console.log("title", title)

                    const opt = {
                        margin: [5, 5, 10, 5], //top, left, bottom, right
                        filename: title,
                        image: { type: 'jpeg', quality: 0.98 },
                        html2canvas: { scale: 2, logging: true, dpi: 192, letterRendering: true},
                        jsPDF: { unit: 'mm', format: ['210', '297'], orientation: 'portrait' },
                    };

                    html2pdf().set(opt).from(element).toContainer().toCanvas().toImg().toPdf().save()

                }
            });
        },
    };
    FormController.include(includeDict);

})
