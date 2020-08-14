$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

$('.modal').on('show.bs.modal', function (event) {
    //remove lengthy eli5 description
    $('pre').remove()

    // POST feedback to Redis Queue
    let clauseCard = $(event.relatedTarget) 
    let clause  = clauseCard.text()
    let modal = $(this)
    $('.validation').on('click', (e) => {
      messageText = modal.find('#message-text')
      let feedback = messageText.val()
      let validation = $(e.target).text()
      $.ajax({
        url: '/to_s3',
        data: { type: validation + '|' + feedback + '|' + clause },
        method: 'POST'
      })
      .done((res) => {
        console.log(res)
      })
      .fail((err) => {
        console.log(err)
      });
    })
})

$('#docList a').on('click', function (e) {
  e.preventDefault()
  $(this).tab('show')
  let doc_id = $(this).text().replace(".", "\\.")
  
  $(".to-hide").each(function(){
    if (! $(this).hasClass('d-none') ) {
      $(this).addClass('d-none')
    }
  })
  
  let target = $(`#${doc_id}`)
  target.toggleClass('d-none')
})



