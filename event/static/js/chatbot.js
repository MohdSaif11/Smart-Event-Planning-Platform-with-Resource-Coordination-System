document.addEventListener("DOMContentLoaded", function () {

    const button = document.getElementById("chatbot-button");
    const box = document.getElementById("chatbot-box");
    const close = document.getElementById("chatbot-close");
    const input = document.getElementById("chatbot-input");
    const send = document.getElementById("chatbot-send");
    const messages = document.getElementById("chatbot-messages");

    if (!button || !box || !input || !send || !messages) {
        return;
    }

    button.addEventListener("click", function () {
        box.classList.add("active");
        input.focus();
    });

    if (close) {
        close.addEventListener("click", function () {
            box.classList.remove("active");
        });
    }

    function addMessage(text, type) {

        const message = document.createElement("div");

        message.className = type === "user"
            ? "user-message"
            : "bot-message";

        message.textContent = text;

        messages.appendChild(message);

        messages.scrollTop = messages.scrollHeight;

        return message;
    }

    async function sendMessage() {

        const message = input.value.trim();

        if (!message) {
            return;
        }

        addMessage(message, "user");

        input.value = "";

        const thinkingMessage = addMessage("Thinking...", "bot");

        send.disabled = true;

        try {

            const response = await fetch("/chatbot/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    message: message
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.reply || "Server error");
            }

            thinkingMessage.textContent = data.reply;

        } catch (error) {

            console.error("Chatbot error:", error);

            thinkingMessage.textContent =
                "Sorry, I couldn't connect to the Event Assistant.";

        } finally {

            send.disabled = false;
            messages.scrollTop = messages.scrollHeight;

        }
    }

    send.addEventListener("click", sendMessage);

    input.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }

    });

    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {

            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {

                cookie = cookie.trim();

                if (cookie.startsWith(name + "=")) {

                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }

});
