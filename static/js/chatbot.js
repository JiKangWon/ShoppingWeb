function SendMessage(userId) {
    const inputMessage = document.getElementById('input-message')
    const chatContent = document.querySelector('.chat-content');
    if (inputMessage === "") {
        return;
    }
    const messageValue = inputMessage.value;
    const data = {
        message: messageValue,
    };
    inputMessage.value = "";
    let content = `
        <p > [You]: ${messageValue} </p>
    `
    chatContent.insertAdjacentHTML("beforeend", content);
    const SendMessageUrl = `/chatbot/send-message/${userId}/`;
    // Gửi yêu cầu POST
    fetch(SendMessageUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify(data), // Chuyển dữ liệu thành JSON
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
        .then((data) => {
            content = `
                <p > [Linda] ${data.response} </p>
            `
        chatContent.insertAdjacentHTML("beforeend", content);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
}

function toggleChat() {
  const chatWindow = document.getElementById("chatWindow");
  const isVisible = chatWindow.style.display === "flex";

  chatWindow.style.display = isVisible ? "none" : "flex";
  // Reset về kích thước mặc định khi đóng/mở
  if (!isVisible) {
    chatWindow.classList.remove("maximized");
  }
}

function toggleSize() {
  const chatWindow = document.getElementById("chatWindow");
  chatWindow.classList.toggle("maximized");
}

