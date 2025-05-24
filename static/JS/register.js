document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
  
    form.addEventListener('submit', function (e) {
      const username = document.getElementById('username').value.trim();
      const password1 = document.getElementById('password1').value;
      const password2 = document.getElementById('password2').value;
  
      errorMessage.textContent = '';
      successMessage.style.display = 'none';
  
      // Verificações básicas
      if (!username || !password1 || !password2) {
        e.preventDefault();
        errorMessage.textContent = 'Todos os campos são obrigatórios.';
        return;
      }
  
      if (password1 !== password2) {
        e.preventDefault();
        errorMessage.textContent = 'As senhas não coincidem.';
        return;
      }
  
      if (password1.length < 6) {
        e.preventDefault();
        errorMessage.textContent = 'A senha deve ter pelo menos 6 caracteres.';
        return;
      }
  
      // Se tudo OK, o formulário será enviado.
      successMessage.style.display = 'block';
    });
  });
  