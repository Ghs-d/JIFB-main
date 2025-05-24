$(document).on('submit', '#form-comentario', function(e) {
  e.preventDefault();

  const corpoComentario = $("#body").val().trim();
  const csrfToken = $('input[name=csrfmiddlewaretoken]').val();

  if (!corpoComentario) {
    mostrarMensagemErro("O comentário não pode estar vazio.");
    return;
  }

  const $form = $(this);
  const $botao = $form.find('button[type=submit]');
  $botao.prop('disabled', true);

  $.ajax({
    type: 'POST',
    url: window.location.href,
    data: {
      body: corpoComentario,
      csrfmiddlewaretoken: csrfToken
    },
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    },
    success: function (data) {
      console.log("Sucesso:", data);
      const novoComentario = `
        <div class="user" id="comentario-${data.id}">
          <div class="user-pic">
            <a href="/u/${data.autor}">
              <img src="${data.foto}" alt="Avatar" style="width: 100%; height: 100%;">
            </a>
          </div>
          <div class="user-info">
            <span>@${data.autor}</span>
            <p>${data.data}</p>
          </div>
          <div class="dropdown ms-auto">
            <i class="fas fa-ellipsis-vertical" data-bs-toggle="dropdown" aria-expanded="false"></i>
            <ul class="dropdown-menu">
              <li>
                <span class="dropdown-item"><i class="fas fa-pen mx-2"></i> Ainda em desenvolvimento</span>
              </li>
              <li>
                <a href="/excluir-comentario/${data.id}">
                  <span class="dropdown-item"><i class="fas fa-trash mx-2"></i>Excluir</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div class="comment-content">${data.body}</div>
      `;

      const $comentario = $(novoComentario);
      $('#lista-comentarios').prepend($comentario);;

      $("#body").val("");
    },
    error: function (xhr) {
      let mensagem = xhr.responseJSON?.error || 'Erro ao comentar.';
      mostrarMensagemErro(mensagem);
    },
    complete: function () {
      $botao.prop('disabled', false);
    }
  });
});

// ✅ Aqui está fora do submit handler, como deve ser
function mostrarMensagemErro(mensagem) {
  let $erro = $('#mensagem-erro');
  if ($erro.length === 0) {
    $erro = $('<div id="mensagem-erro" class="alert alert-danger mt-2"></div>');
    $('#form-comentario').after($erro);
  }
  $erro.text(mensagem).fadeIn();

  setTimeout(() => $erro.fadeOut(), 5000);
}