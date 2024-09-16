import React, { useState } from "react";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import "./AndrewBotCustom.css";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
  ConversationHeader,
  Avatar,
} from "@chatscope/chat-ui-kit-react";
import AndrewBotCustomContent from "./AndrewBotCustomContent";
import axios from "axios";

// Define the type for message
interface chatMessage {
  message?: string;
  sentTime: string;
  sender: string;
  direction: "incoming" | "outgoing";
  position: "single" | "first" | "normal" | "last";
  type: "html" | "text" | "image" | "custom";
  payload?: string | object;
}

type AndrewBotContext = "createOrder" | "viewOrder" | "exit" | "none";

export default function AndrewBot() {
  const [isTyping, setIsTyping] = useState(false);
  const [initialMessageSent, setInitialMessageSent] = useState(false); // Track if initial message has been sent
  const [messages, setMessages] = useState<chatMessage[]>([]); // Initialize messages as an empty array
  const [AndrewBotContext, setAndrewBotContext] =
    useState<AndrewBotContext>("none");

  const handleSend = async (userMessage: string) => {
    let newBotMessage: chatMessage | null = null;
    let AndrewBotContextMsg = "";

    const newUserMessage: chatMessage = {
      message: userMessage,
      sentTime: "just now",
      sender: "user",
      direction: "outgoing",
      position: "single",
      type: "text",
    };

    // Only accept "Hi" or "hi" as the first message
    if (!initialMessageSent && userMessage.toLowerCase() !== "hi") {
      newBotMessage = {
        sentTime: "just now",
        sender: "Andrew",
        direction: "incoming",
        position: "single",
        type: "text",
        message: "Please start by typing Hi",
      };

      setMessages((prevMessages) =>
        newBotMessage
          ? [...prevMessages, newUserMessage, newBotMessage]
          : [...prevMessages, newUserMessage]
      );
      return;
    }

    if (!initialMessageSent && userMessage.toLowerCase() === "hi") {
      newBotMessage = {
        sentTime: "just now",
        sender: "Andrew",
        direction: "incoming",
        position: "single",
        type: "text",
        message:
          "Hi, I am Andrew. How may I help you?\nPlease click any of the below buttons to select the task that you want to perform.",
      };

      const newBotMessageCustom: chatMessage = {
        sentTime: "just now",
        sender: "Andrew",
        direction: "incoming",
        position: "single",
        type: "custom",
        payload: (
          <AndrewBotCustomContent onChoiceSelected={handleChoiceSelected} />
        ),
      };
      setInitialMessageSent(true);

      setMessages((prevMessages) =>
        newBotMessage
          ? [
              ...prevMessages,
              newUserMessage,
              newBotMessage,
              newBotMessageCustom,
            ]
          : [...prevMessages, newUserMessage]
      );
      return;
    }

    // Handle messages based on the bot context
    if (initialMessageSent) {
      if (AndrewBotContext === "createOrder") {
        AndrewBotContextMsg = userMessage;
      } else if (AndrewBotContext === "viewOrder") {
        AndrewBotContextMsg = `Order ID received: ${userMessage}, getting the details.`;
      } else if (AndrewBotContext === "none") {
        AndrewBotContextMsg = userMessage;
      }

      if (
        AndrewBotContext === "createOrder" ||
        AndrewBotContext === "viewOrder" ||
        AndrewBotContext === "none"
      ) {
        // console.log(JSON.stringify(AndrewBotContextMsg));

        newBotMessage = {
          sentTime: "just now",
          sender: "Andrew",
          direction: "incoming",
          position: "single",
          type: "text",
          message: AndrewBotContextMsg,
        };
        setMessages((prevMessages) =>
          newBotMessage
            ? [...prevMessages, newBotMessage]
            : [...prevMessages, newUserMessage]
        );

        let abcMessage = "";

        if (AndrewBotContext === "viewOrder") {
          const orderID = JSON.stringify(userMessage);
          console.log("AndrewBot Order ID:", orderID);

          // Store the orderID in localStorage and open a new window
          localStorage.setItem("orderID", orderID);
          abcMessage = `Order ID ${orderID.substring(
            1,
            orderID.length - 1
          )} viewed. What do you want to do next?`;

          setTimeout(() => {
            window.open("/view-order", "_blank");
            sendBotMessageWithPayload(abcMessage);
          }, 1000);
        }

        if (AndrewBotContext === "createOrder") {
          //const storedOrderID = localStorage.getItem("orderID");
          const storedOrderID = 100003;
          abcMessage = `Order ID ${storedOrderID} created. What do you want to do next?`;

          setTimeout(() => {
            window.open("/create-order", "_blank");
            sendBotMessageWithPayload(abcMessage);
          }, 1000);
        }

        setAndrewBotContext("none"); // Reset context after handling

        return;
      }
    }
  };

  // Callback function to handle the selected choice
  function handleChoiceSelected(chosenAction: string): void {
    let choice = chosenAction;
    let responseMessageAndrew = "";
    const responseMessageCreateOrder =
      "You have selected Create Order. Please enter your order details seperated by commas in item, brand, quantity in gms/kgs.\nE.g - wheat, ashirvaad, 5 kg, rice, india gate, 2 kg etc.";
    const responseMessageViewOrder =
      "You have selected View Order. Please enter your order ID.";
    const responseMessageExit =
      "I hope I was able to help you, Thank you. Bye!!!";

    console.log("choice:", choice);

    switch (choice) {
      case "Create Order":
        // Perform actions for creating an order
        responseMessageAndrew = responseMessageCreateOrder;
        setAndrewBotContext("createOrder");
        break;
      case "View Order":
        // Perform actions for viewing an order
        responseMessageAndrew = responseMessageViewOrder;
        setAndrewBotContext("viewOrder");
        break;
      case "Exit":
        // Perform actions for exiting
        responseMessageAndrew = responseMessageExit;
        setAndrewBotContext("exit");
        setInitialMessageSent(false);
        break;
      default:
        setAndrewBotContext("none");
        alert("Unknown action selected.");
    }

    const responseMessage: chatMessage = {
      message: responseMessageAndrew,
      sentTime: "just now",
      sender: "Andrew",
      direction: "incoming",
      position: "single",
      type: "text",
    };
    setMessages((prevMessages) => [...prevMessages, responseMessage]);
  }

  function sendBotMessageWithPayload(newBotMessage1: string): void {
    let newBotMessage: chatMessage | null = null;

    newBotMessage = {
      sentTime: "just now",
      sender: "Andrew",
      direction: "incoming",
      position: "single",
      type: "text",
      message: newBotMessage1,
    };

    const newBotMessageCustom: chatMessage = {
      sentTime: "just now",
      sender: "Andrew",
      direction: "incoming",
      position: "single",
      type: "custom",
      payload: (
        <AndrewBotCustomContent onChoiceSelected={handleChoiceSelected} />
      ),
    };

    setMessages((prevMessages) => [
      ...prevMessages,
      newBotMessage,
      newBotMessageCustom,
    ]);
  }

  return (
    // <div style={{ position: "relative", height: "500px", width: "700px" }}>
    <div className="andrewbot-body">
      <div className="andrewbot-container">
        <MainContainer>
          <ChatContainer>
            <ConversationHeader>
              <Avatar name="Andrew" src="src\assets\AndrewAvatar.svg" />
              <ConversationHeader.Content userName="Andrew" />
            </ConversationHeader>
            <MessageList scrollBehavior="auto">
              {messages.map((message, index) => (
                <Message key={index} model={message} />
              ))}
            </MessageList>
            <MessageInput
              placeholder={
                initialMessageSent ? "Type a message..." : "Type Hi here..."
              }
              attachButton={false}
              fancyScroll={true}
              onSend={handleSend}
            />{" "}
            {/* Disabled for now */}
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  );
}
