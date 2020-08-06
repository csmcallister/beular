$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

$('.modal').on('show.bs.modal', function (event) {
    let clauseCard = $(event.relatedTarget) // card that triggered the modal
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




