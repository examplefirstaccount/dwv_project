document.addEventListener("DOMContentLoaded", async function() {
    const response = await fetch("http://127.0.0.1:5000/api/hello");
    const data = await response.json();
    document.getElementById("message").innerText = data.message;
});