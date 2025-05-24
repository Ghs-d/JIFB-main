document.getElementById("loginForm").addEventListener("submit", async function (event) {
  event.preventDefault();

  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;
  const error = document.getElementById("loginError");

  error.style.display = "none";

  try {
      const response = await fetch("", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (data.success) {
          localStorage.setItem("userEmail", data.email);
          localStorage.setItem("userRole", data.role);

         
          if (data.role === "admin") {
              window.location.href = "admin.html";
          } else if (data.role === "jornalista") {
              window.location.href = "jornalista.html";
          } else {
              window.location.href = "index.html";
          }
      } else {
          error.textContent = data.error || "Erro ao fazer login.";
          error.style.display = "block";
      }
  } catch (err) {
      error.textContent = "Erro na comunicação com o servidor.";
      error.style.display = "block";
  }
});
