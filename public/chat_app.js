// import { marked } from "https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.0/lib/marked.esm.js";
import { marked } from "./marked.esm.js";
const convElement = document.getElementById("conversation");

const promptInput = document.getElementById("prompt-input");
const spinner = document.getElementById("spinner");

// stream the response and render messages as each chunk is received
// data is sent as newline-delimited JSON
async function onFetchResponse(response) {
  let text = "";
  let decoder = new TextDecoder();
  if (response.ok) {
    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      text += decoder.decode(value);
      addMessages(text);
      spinner.classList.remove("active");
    }
    addMessages(text);
    promptInput.disabled = false;
    promptInput.focus();
  } else {
    const text = await response.text();
    console.error(`Unexpected response: ${response.status}`, {
      response,
      text,
    });
    throw new Error(`Unexpected response: ${response.status}`);
  }
}

// take raw response text and render messages into the `#conversation` element
// Message created_at is assumed to be a unique identifier of a message, and is used to deduplicate
function addMessages(responseText) {
  const lines = responseText.split("<==Split==>");
  const messagesMap = new Map();
  lines
    .filter((line) => line.length > 1)
    .forEach((line) => {
      const parsed = JSON.parse(line);
      parsed.forEach((msg) => {
        messagesMap.set(msg.id, msg);
      });
    });
  const messages = Array.from(messagesMap.values());
  for (const message of messages) {
    const { id, created_at, role, content } = message;
    const $id = `msg-${id}`;
    let msgDiv = document.getElementById($id);
    if (!msgDiv) {
      msgDiv = document.createElement("div");
      msgDiv.id = $id;
      msgDiv.title = `${role} at ${created_at}`;
      msgDiv.classList.add("border-top", "pt-2", role);
      convElement.appendChild(msgDiv);
    }
    msgDiv.innerHTML = marked.parse(content);
  }
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

function onError(error) {
  console.error(error);
  document.getElementById("error").classList.remove("d-none");
  document.getElementById("spinner").classList.remove("active");
}

async function onSubmit(e) {
  e.preventDefault();
  spinner.classList.add("active");
  const body = new FormData(e.target);

  promptInput.value = "";
  promptInput.disabled = true;
  const response = await fetch("/api/messages", { method: "POST", body: body });
  await onFetchResponse(response);
}

document.addEventListener("DOMContentLoaded", function () {
  // call onSubmit when the form is submitted (e.g. user clicks the send button or hits Enter)
  document
    .querySelector("form")
    .addEventListener("submit", (e) => onSubmit(e).catch(onError));

  // load messages on page load
  fetch("/api/messages").then(onFetchResponse).catch(onError);
});