window.addEventListener('load', function () {
    // Everything has loaded!

    const element = document.querySelector('#portal_sale_content')
    const title_element = document.querySelector('.my-0')

    const button_element = $(".o_download_btn")

    button_element.on("click", function () {

        let title = ""
        let formatted_title = title_element.textContent.trim().split('\n')

        for (i in formatted_title) {
            if (i > 0) {
                title += " "
            }
            title += formatted_title[i].trim()
        }

        var width = element.offsetWidth + 350;
        var height = element.offsetHeight + 250;
        var opt = {
            margin: 25,
            filename: title,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 1 },
            jsPDF: { unit: 'px', format: [width, height], orientation: 'portrait' }
        };

        html2pdf().set(opt).from(element).toContainer().toCanvas().toImg().toPdf().save()
        //.then(cleanup())
    })
});

function cleanup() {
    the_node = document.querySelector('#wrapwrap').style.zIndex = "1001";
    // setTimeout(() => {
    //     const elements = ['.html2canvas-container', '.html2pdf__overlay', '.html2pdf__container']

    //     elements.forEach((n) => {
    //         node = document.querySelector(n);
    //         console.log(node)
    //         node.remove()
    //     })
    //     debugger
    // }, 5000)
}