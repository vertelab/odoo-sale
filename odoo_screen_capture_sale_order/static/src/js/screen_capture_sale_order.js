odoo.define("odoo_screen_capture_sale_order.screen_capture_sale_order", function (require) {
    "use strict";

    var publicWidget = require('web.public.widget')

    publicWidget.registry.screenCaptureSaleOrder = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        read_events: {
            'click .no_existing_doc': '_fetch_pdf',
        },

        _fetch_pdf: function () {
            /* TODO: 
                properly fit contents in pdf using page break 
                html2pdf library suggests <div class="html2pdf__page-break"/> to be added before the element you want to break into the next page

                PROBLEM: How to determine the contents on each page, the previous page and next page, this will help to know which page to apply page-break on

                SUGGESTED SOLUTION: 

            */

            const title_element = document.querySelector('.my-0')

            let header_information = document.querySelectorAll("#portal_sale_content > div > .card-body > #informations > div.row > div > span")
            if (header_information.length > 0) {
                Array.from(header_information).forEach( function (el) {
                    const section_div = el.querySelectorAll("section > div.container")    
                    Array.from(section_div).forEach( function (section_div_el) {
                        section_div_el.classList.remove('container')
                    })
                });
            }

            // when there is a user logged in
            let elems = document.querySelectorAll("#portal_sale_content > div > .card-body > div[data-oe-model='sale.order'], div[data-oe-model='sale.order.line'], div[data-oe-model='sale.order.option']")

            if (elems.length === 0) {
                elems = document.querySelectorAll("#portal_sale_content > div > .card-body > .oe_no_empty") // when there is no user logged in
            }

            Array.from(elems).forEach( function (el) {
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
                margin: [5, 5, 10, 5], //top, left, buttom, right
                filename: title,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, logging: true, dpi: 192, letterRendering: true},
                jsPDF: { unit: 'mm', format: ['210', '297'], orientation: 'portrait' },
            };

            html2pdf().set(opt).from(element).toContainer().toCanvas().toImg().toPdf().save()
        }
    })
})
