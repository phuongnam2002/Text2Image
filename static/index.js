const draw_btn = document.getElementById('draw-btn')
const image_display = document.getElementById('image-display')
const desc_textarea = document.getElementById('desc-textarea')
const csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0]
const spiner = document.getElementById('spiner')

const server_url = `${window.location.protocol}//${window.location.host}`

draw_btn.onclick =  async function(){
    desciption = desc_textarea.value
    token = csrf_token.value
    image_display.style.display = "none"
    spiner.style.display = "flex"

    await $.ajax({
        type: "POST",
        url: server_url,
        headers: {
            "X-CSRFToken": token
        },
        data: {
          "desciption": desciption,
        },
        success: function (result) {
          image_display.src = result['image_url']
        },
        dataType: "json"
      });
    spiner.style.display = "none"
    image_display.style.display = "flex"
}