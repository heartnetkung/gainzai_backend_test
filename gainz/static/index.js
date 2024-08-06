(() => {
  let token = "";

  const onAuthSubmit = async (event) => {
    event.preventDefault();
    const apiKeyData = document.getElementById("auth-input").value;
    const response = await fetch("/api/auth", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ api_key: apiKeyData }),
    });
    if (!response.ok) {
      alert("");
      throw new Error("");
    }
    token = await response.json();
  };

  document.getElementById("auth-form").addEventListener("submit", onAuthSubmit);
})();
